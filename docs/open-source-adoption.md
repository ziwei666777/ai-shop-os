# AI Commerce OS V3 开源项目采用记录

## 本轮正式采用

| 项目 | 用途 | 版本策略 | 许可证 | 结论 |
| --- | --- | --- | --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Agent 事件路由、状态流转、人工审批节点 | `>=1.2.6,<2` | MIT | 正式采用，作为唯一工作流编排引擎 |

Agent 之间不直接引用或调用。所有协作统一进入 LangGraph 工作流程，保证路由、审批和执行过程可追踪。

## 已审核，后续按模块采用

| 项目 | 计划用途 | 审核结论 |
| --- | --- | --- |
| [LiteLLM](https://github.com/BerriAI/litellm) | 统一调用 GPT、Claude、DeepSeek、Gemini、Qwen | 主体为 MIT，企业目录使用单独许可证；后续只采用开源 Python SDK 边界 |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | 浏览器、邮箱、飞书、企业微信等工具协议 | MIT；锁定稳定 `1.x`，暂不使用 `2.x` 测试版 |
| [pgvector-python](https://github.com/pgvector/pgvector-python) | SQLAlchemy 向量字段与相似度查询 | MIT；与当前 Supabase PostgreSQL 和 SQLAlchemy 匹配 |

PydanticAI 暂不作为第二套编排引擎引入，避免与 LangGraph 职责重叠。后续如果其模型适配层能明显减少维护成本，再单独审核。

## 国内平台接入边界

平台优先级调整为：淘宝、抖音、闲鱼，其后再考虑 Shopify 和其他海外平台。

- 淘宝：只使用淘宝开放平台 TOP API。官方 Python SDK 仍依赖 Python 2，因此后端将按官方 HTTP 协议封装 Python 3 Connector。
- 抖音：使用抖音或抖店开放平台正式授权、OpenAPI 和回调能力；商家必须先申请相应权限。
- 闲鱼：当前未确认可商用的公开官方订单、消息 API，不接入扫码登录、Cookie、抓包和自动化爬虫项目。
- 第三方仓库即使热度高，也必须同时满足许可证明确、维护活跃、官方协议合规、依赖安全四项条件才可采用。
