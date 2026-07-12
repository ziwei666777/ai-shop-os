from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="apps/api/.env", env_file_encoding="utf-8", extra="ignore")

    supabase_url: str = ""
    supabase_publishable_key: str = ""
    database_url: str = ""
    redis_url: str = ""
    auth_required: bool = False
    local_company_id: str = "00000000-0000-0000-0000-000000000001"
    token_encryption_key: str = ""
    taobao_app_key: str = ""
    taobao_app_secret: str = ""
    taobao_redirect_uri: str = "http://localhost:8000/v1/connectors/taobao/oauth/callback"
    douyin_app_key: str = ""
    douyin_app_secret: str = ""
    douyin_authorization_url: str = ""
    douyin_redirect_uri: str = "http://localhost:8000/v1/connectors/douyin/oauth/callback"

    @property
    def has_database(self) -> bool:
        # 数据库密码未配置时自动走内存仓储，避免开发环境误连失败。
        return bool(self.database_url) and "YOUR_DATABASE_PASSWORD" not in self.database_url

    @property
    def has_redis(self) -> bool:
        return bool(self.redis_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
