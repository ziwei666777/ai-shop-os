from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthStartResult:
    platform: str
    authorization_url: str
    state: str


class CommerceConnector(ABC):
    @abstractmethod
    def start_oauth(self, shop: str) -> OAuthStartResult:
        """生成官方授权链接，所有平台接入必须从授权边界开始。"""

    @abstractmethod
    def verify_webhook(self, raw_body: bytes, signature: str) -> bool:
        """校验平台 Webhook 签名，未通过则不得入库。"""


class ShopifyConnector(CommerceConnector):
    def start_oauth(self, shop: str) -> OAuthStartResult:
        state = "local-dev-state"
        scopes = "read_orders,read_products,read_customers"
        url = (
            f"https://{shop}/admin/oauth/authorize"
            f"?client_id=SHOPIFY_CLIENT_ID&scope={scopes}&redirect_uri=http://localhost:8000/v1/connectors/shopify/oauth/callback&state={state}"
        )
        return OAuthStartResult(platform="shopify", authorization_url=url, state=state)

    def verify_webhook(self, raw_body: bytes, signature: str) -> bool:
        # Sprint 2 前的试用版只接受显式测试签名；真实 HMAC 校验将在配置密钥后替换。
        return bool(raw_body) and signature == "dev-valid-signature"


class TaobaoConnector(CommerceConnector):
    def start_oauth(self, shop: str) -> OAuthStartResult:
        state = "taobao-dev-state"
        url = f"https://oauth.taobao.com/authorize?response_type=code&client_id=TAOBAO_APP_KEY&state={state}&view=web"
        return OAuthStartResult(platform="taobao", authorization_url=url, state=state)

    def verify_webhook(self, raw_body: bytes, signature: str) -> bool:
        # 淘宝真实验签依赖开放平台应用密钥；当前保留边界，不伪造接入。
        return bool(raw_body) and signature == "dev-valid-signature"
