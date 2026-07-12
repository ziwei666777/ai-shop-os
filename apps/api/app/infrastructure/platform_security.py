from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from typing import Mapping

from apps.api.app.infrastructure.config import get_settings


class IntegrationUnavailableError(RuntimeError):
    pass


def sign_taobao_request(parameters: Mapping[str, str], app_secret: str, method: str = "hmac-sha256") -> str:
    payload = "".join(
        f"{key}{value}" for key, value in sorted(parameters.items()) if key != "sign" and value not in (None, "")
    ).encode("utf-8")
    secret = app_secret.encode("utf-8")
    if method == "md5":
        return hashlib.md5(secret + payload + secret).hexdigest().upper()
    digest = hashlib.sha256 if method == "hmac-sha256" else hashlib.md5
    return hmac.new(secret, payload, digest).hexdigest().upper()


def sign_douyin_request(parameters: Mapping[str, str], app_secret: str) -> str:
    payload = "".join(
        f"{key}{value}" for key, value in sorted(parameters.items()) if key != "sign" and value not in (None, "")
    ).encode("utf-8")
    return hmac.new(app_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class OAuthStatePayload:
    user_id: str
    company_id: str
    platform: str


class RedisOAuthStateStore:
    prefix = "ai-shop-os:oauth-state:"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.redis_url:
            raise IntegrationUnavailableError("Redis 尚未配置，暂时不能开始正式平台授权。")
        try:
            from redis import Redis
        except ImportError as error:
            raise IntegrationUnavailableError("Redis 客户端依赖尚未安装。") from error
        self._redis = Redis.from_url(settings.redis_url, decode_responses=True)

    def create(self, payload: OAuthStatePayload) -> str:
        state = secrets.token_urlsafe(32)
        self._redis.setex(f"{self.prefix}{state}", 600, json.dumps(payload.__dict__, ensure_ascii=False))
        return state

    def consume(self, state: str, platform: str) -> OAuthStatePayload:
        key = f"{self.prefix}{state}"
        pipeline = self._redis.pipeline()
        pipeline.get(key)
        pipeline.delete(key)
        raw, _ = pipeline.execute()
        if not raw:
            raise ValueError("授权状态已过期或已被使用，请重新发起授权。")
        payload = OAuthStatePayload(**json.loads(raw))
        if not hmac.compare_digest(payload.platform, platform):
            raise ValueError("授权平台不匹配，已拒绝本次请求。")
        return payload


class TokenCipher:
    def __init__(self) -> None:
        key = get_settings().token_encryption_key
        if not key:
            raise IntegrationUnavailableError("平台令牌加密密钥尚未配置。")
        try:
            from cryptography.fernet import Fernet
        except ImportError as error:
            raise IntegrationUnavailableError("令牌加密依赖尚未安装。") from error
        self._fernet = Fernet(key.encode("ascii"))

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode("ascii")).decode("utf-8")

