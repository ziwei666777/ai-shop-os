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
    backend_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,https://ai-commerce-os-demo.ybqes.chatgpt.site,https://ai-commerce-os-internal.ybqes.chatgpt.site"
    merchant_bridge_api_key: str = ""
    merchant_bridge_company_id: str = ""
    token_encryption_key: str = ""
    taobao_app_key: str = ""
    taobao_app_secret: str = ""
    taobao_redirect_uri: str = "http://localhost:8000/v1/connectors/taobao/oauth/callback"
    douyin_app_key: str = ""
    douyin_app_secret: str = ""
    douyin_authorization_url: str = ""
    douyin_redirect_uri: str = "http://localhost:8000/v1/connectors/douyin/oauth/callback"
    live_workflow_log_storage: str = "memory"
    approval_record_storage: str = "memory"
    after_sale_decision_storage: str = "memory"
    ceo_report_snapshot_storage: str = "memory"
    live_metric_snapshot_storage: str = "memory"
    warehouse_notification_delivery_mode: str = "export_queue"
    warehouse_notification_export_prefix: str = "wms-export"
    warehouse_notification_wms_api_url: str = ""
    warehouse_notification_wms_api_key: str = ""
    warehouse_notification_wms_timeout_seconds: float = 10.0

    @property
    def has_database(self) -> bool:
        # 数据库密码未配置时自动走内存仓储，避免开发环境误连失败。
        return bool(self.database_url) and "YOUR_DATABASE_PASSWORD" not in self.database_url

    @property
    def has_redis(self) -> bool:
        return bool(self.redis_url)

    @property
    def cors_origins(self) -> list[str]:
        # 生产环境用逗号分隔域名，避免在代码里硬编码商家控制台地址。
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
