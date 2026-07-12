from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from sqlalchemy import text

from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.platform_security import (
    IntegrationUnavailableError,
    OAuthStatePayload,
    RedisOAuthStateStore,
    TokenCipher,
    sign_douyin_request,
)


@dataclass(frozen=True)
class OAuthTokenResult:
    platform: str
    shop_identifier: str
    shop_name: str
    access_token: str
    refresh_token: str | None
    expires_in: int
    refresh_expires_in: int | None


def start_platform_oauth(platform: str, user_id: str, company_id: str) -> str:
    settings = get_settings()
    state = RedisOAuthStateStore().create(OAuthStatePayload(user_id, company_id, platform))
    if platform == "taobao":
        if not settings.taobao_app_key:
            raise IntegrationUnavailableError("淘宝 App Key 尚未配置。")
        return "https://oauth.taobao.com/authorize?" + urlencode(
            {
                "response_type": "code",
                "client_id": settings.taobao_app_key,
                "redirect_uri": settings.taobao_redirect_uri,
                "state": state,
                "view": "web",
            }
        )
    if not settings.douyin_app_key or not settings.douyin_authorization_url:
        raise IntegrationUnavailableError("抖店应用 Key 或商家授权地址尚未配置。")
    return settings.douyin_authorization_url + ("&" if "?" in settings.douyin_authorization_url else "?") + urlencode(
        {"state": state, "redirect_uri": settings.douyin_redirect_uri}
    )


async def complete_platform_oauth(platform: str, code: str, state: str) -> tuple[OAuthStatePayload, OAuthTokenResult]:
    payload = RedisOAuthStateStore().consume(state, platform)
    result = await (_exchange_taobao(code) if platform == "taobao" else _exchange_douyin(code))
    _save_encrypted_token(payload.company_id, result)
    return payload, result


async def _exchange_taobao(code: str) -> OAuthTokenResult:
    settings = get_settings()
    if not settings.taobao_app_key or not settings.taobao_app_secret:
        raise IntegrationUnavailableError("淘宝应用凭证尚未配置。")
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://oauth.taobao.com/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.taobao_app_key,
                "client_secret": settings.taobao_app_secret,
                "redirect_uri": settings.taobao_redirect_uri,
            },
        )
    response.raise_for_status()
    data = response.json()
    if "access_token" not in data:
        raise ValueError("淘宝授权失败，请检查应用权限后重试。")
    shop_identifier = str(data.get("taobao_user_id") or data.get("sub_taobao_user_id") or "unknown")
    return OAuthTokenResult(
        "taobao",
        shop_identifier,
        str(data.get("taobao_user_nick") or shop_identifier),
        str(data["access_token"]),
        str(data["refresh_token"]) if data.get("refresh_token") else None,
        int(data.get("expires_in", 86400)),
        int(data["re_expires_in"]) if data.get("re_expires_in") else None,
    )


async def _exchange_douyin(code: str) -> OAuthTokenResult:
    settings = get_settings()
    if not settings.douyin_app_key or not settings.douyin_app_secret:
        raise IntegrationUnavailableError("抖店应用凭证尚未配置。")
    common = {
        "app_key": settings.douyin_app_key,
        "method": "token.create",
        "param_json": json.dumps({"code": code, "grant_type": "authorization_code"}, separators=(",", ":"), ensure_ascii=False),
        "timestamp": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
        "v": "2",
        "sign_method": "hmac-sha256",
    }
    common["sign"] = sign_douyin_request(common, settings.douyin_app_secret)
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post("https://openapi-fxg.jinritemai.com/token/create", params=common)
    response.raise_for_status()
    payload = response.json()
    if payload.get("err_no") not in (0, "0") or not payload.get("data", {}).get("access_token"):
        raise ValueError("抖店授权失败，请重新从抖店应用使用地址进入。")
    data = payload["data"]
    return OAuthTokenResult(
        "douyin",
        str(data.get("shop_id") or data.get("auth_id") or "unknown"),
        str(data.get("shop_name") or data.get("shop_id") or "抖音店铺"),
        str(data["access_token"]),
        str(data["refresh_token"]) if data.get("refresh_token") else None,
        int(data.get("expires_in", 604800)),
        int(data.get("refresh_expires_in", 1209600)),
    )


def _save_encrypted_token(company_id: str, result: OAuthTokenResult) -> None:
    if SessionFactory is None:
        raise IntegrationUnavailableError("数据库尚未连接，不能保存平台授权。")
    cipher = TokenCipher()
    now = datetime.now(timezone.utc)
    values = {
        "id": str(uuid4()),
        "company_id": company_id,
        "platform": result.platform,
        "shop_identifier": result.shop_identifier,
        "access_token": cipher.encrypt(result.access_token),
        "refresh_token": cipher.encrypt(result.refresh_token) if result.refresh_token else None,
        "token_expires_at": now + timedelta(seconds=result.expires_in),
        "refresh_token_expires_at": now + timedelta(seconds=result.refresh_expires_in) if result.refresh_expires_in else None,
        "connected_at": now,
    }
    with SessionFactory.begin() as session:
        session.execute(
            text("""
              insert into platform_connections (
                id, company_id, platform, status, shop_identifier, scopes, authorization_mode,
                access_token_encrypted, refresh_token_encrypted, token_expires_at,
                refresh_token_expires_at, connected_at
              ) values (
                :id, :company_id, cast(:platform as connector_platform), 'connected', :shop_identifier,
                array['read_orders','read_products','read_customers','read_logistics','read_after_sales'],
                'service_provider', :access_token, :refresh_token, :token_expires_at,
                :refresh_token_expires_at, :connected_at
              )
              on conflict (company_id, platform, shop_identifier) do update set
                status = 'connected', access_token_encrypted = excluded.access_token_encrypted,
                refresh_token_encrypted = excluded.refresh_token_encrypted,
                token_expires_at = excluded.token_expires_at,
                refresh_token_expires_at = excluded.refresh_token_expires_at,
                connected_at = excluded.connected_at, last_error = null, updated_at = now()
            """),
            values,
        )

