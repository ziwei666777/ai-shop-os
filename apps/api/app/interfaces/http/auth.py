from dataclasses import dataclass
import secrets

import httpx
from fastapi import Header, HTTPException
from sqlalchemy import text

from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.database import SessionFactory


@dataclass(frozen=True)
class CompanyContext:
    user_id: str
    company_id: str


async def require_company_context(
    authorization: str = Header(default=""),
    x_company_id: str = Header(default="", alias="X-Company-ID"),
) -> CompanyContext:
    settings = get_settings()
    if not settings.auth_required:
        return CompanyContext(user_id="local-development-user", company_id=x_company_id or settings.local_company_id)

    if not x_company_id:
        raise HTTPException(status_code=400, detail="缺少公司标识 X-Company-ID。")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="登录状态无效，请重新登录。")
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(status_code=503, detail="Supabase 身份验证尚未配置。")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
                headers={"Authorization": f"Bearer {token}", "apikey": settings.supabase_publishable_key},
            )
        response.raise_for_status()
        user_id = str(response.json()["id"])
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=401, detail="登录状态无效，请重新登录。") from error

    if SessionFactory is None:
        raise HTTPException(status_code=503, detail="数据库尚未连接，无法验证公司成员身份。")
    with SessionFactory() as session:
        membership = session.execute(
            text("select 1 from public.company_members where company_id = :company_id and user_id = :user_id"),
            {"company_id": x_company_id, "user_id": user_id},
        ).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail="你无权访问这家公司的数据。")
    return CompanyContext(user_id=user_id, company_id=x_company_id)


async def require_merchant_bridge_context(
    authorization: str = Header(default=""),
    x_company_id: str = Header(default="", alias="X-Company-ID"),
    x_aicos_bridge_key: str = Header(default="", alias="X-AICOS-Bridge-Key"),
) -> CompanyContext:
    settings = get_settings()
    if settings.merchant_bridge_api_key and x_aicos_bridge_key:
        if not secrets.compare_digest(x_aicos_bridge_key, settings.merchant_bridge_api_key):
            raise HTTPException(status_code=401, detail="商家桥接密钥无效。")
        company_id = x_company_id or settings.merchant_bridge_company_id or settings.local_company_id
        return CompanyContext(user_id="merchant-message-bridge", company_id=company_id)
    return await require_company_context(authorization, x_company_id)


async def require_customer_message_ingest_context(
    authorization: str = Header(default=""),
    x_company_id: str = Header(default="", alias="X-Company-ID"),
    x_aicos_bridge_key: str = Header(default="", alias="X-AICOS-Bridge-Key"),
) -> CompanyContext:
    return await require_merchant_bridge_context(authorization, x_company_id, x_aicos_bridge_key)