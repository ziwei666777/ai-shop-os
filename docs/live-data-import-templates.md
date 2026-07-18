# 直播运营数据导入模板说明

## 目标

这组模板不是为了做展示，而是为了让真实商家把直播运营数据按统一格式交给 AI。AI 拿到这些数据后，才能稳定完成三件事：

1. 开播前检查风险。
2. 直播中发现异常并提醒。
3. 下播后复盘并计算节省的人工时间和金额。

## 商业价值

替代岗位：直播运营助理。

预计节省：

- 开播前资料检查：每天节省 20 到 40 分钟。
- 直播中盯盘提醒：每场节省 30 到 90 分钟。
- 下播复盘整理：每天节省 30 到 60 分钟。

老板愿意付钱的原因：这些工作原本需要人每天盯表、查库存、看优惠券、整理复盘。标准模板能让 AI 不靠猜，而是按数据做判断。

## 模板文件

模板都在 `apps/web/public/templates`：

| 文件 | 用途 | 对应 Workflow |
| --- | --- | --- |
| `live-products-template.csv` | 直播商品、库存、价格检查 | 开播前检查 |
| `live-coupons-template.csv` | 优惠券余量、过期检查 | 开播前检查 |
| `live-script-template.csv` | 直播脚本、赠品、商品顺序检查 | 开播前检查 |
| `live-metrics-template.csv` | 在线人数、成交率、停留率、点击率、异常订单 | 直播中扫描 |
| `live-post-review-template.csv` | 销售额、订单数、退款数、差评评论、主播表现 | 下播复盘 |

## 字段说明

### live-products-template.csv

| 字段 | 中文意思 | 是否必填 | 示例 |
| --- | --- | --- | --- |
| `title` | 商品名称 | 是 | 爆款连衣裙 |
| `inventory_count` | 当前库存 | 是 | 80 |
| `safe_stock` | 安全库存线 | 是 | 30 |
| `regular_price` | 日常价格 | 是 | 199 |
| `live_price` | 直播价格 | 是 | 129 |

### live-coupons-template.csv

| 字段 | 中文意思 | 是否必填 | 示例 |
| --- | --- | --- | --- |
| `name` | 优惠券名称 | 是 | 直播间满129减20 |
| `remaining_count` | 剩余张数 | 是 | 300 |
| `expired` | 是否已过期 | 是 | false |

### live-script-template.csv

| 字段 | 中文意思 | 是否必填 | 示例 |
| --- | --- | --- | --- |
| `script_text` | 直播脚本文案 | 是 | 今晚先讲爆款连衣裙 |
| `gift_ready` | 赠品是否准备好 | 是 | true |
| `product_order_ready` | 商品讲解顺序是否准备好 | 是 | true |

### live-metrics-template.csv

| 字段 | 中文意思 | 是否必填 | 示例 |
| --- | --- | --- | --- |
| `online_users` | 当前在线人数 | 是 | 860 |
| `conversion_rate` | 成交率 | 是 | 0.032 |
| `retention_rate` | 停留率 | 是 | 0.28 |
| `comment_count` | 评论数 | 是 | 420 |
| `like_count` | 点赞数 | 是 | 3800 |
| `product_click_rate` | 商品点击率 | 是 | 0.19 |
| `inventory_delta` | 库存减少量 | 是 | 34 |
| `abnormal_order_count` | 异常订单数 | 是 | 1 |

### live-post-review-template.csv

| 字段 | 中文意思 | 是否必填 | 示例 |
| --- | --- | --- | --- |
| `sales_amount_yuan` | 直播销售额 | 是 | 28600 |
| `order_count` | 订单数 | 是 | 214 |
| `viewer_count` | 观看人数 | 是 | 12800 |
| `refund_count` | 退款数 | 是 | 6 |
| `top_product_title` | 成交最高商品 | 是 | 爆款连衣裙 |
| `negative_comment_count` | 负面评论数 | 是 | 11 |
| `host_script_score` | 主播话术评分 | 是 | 82 |

## 使用方式

1. 商家打开“设置 / 平台数据导入”。
2. 下载对应直播模板。
3. 把直播间真实数据填进去。
4. 上传文件。
5. 系统生成检查、提醒、复盘和节省金额。

## 当前边界

当前模板已可下载，后端已有直播 Workflow API。文件直接驱动直播 Workflow 的正式入库还需要下一步把导入任务和 Workflow 调用打通。
## 网页直接执行 Workflow

当前 `/settings/data-import` 已支持商家上传直播模板后直接执行：

- 开播前检查：上传 `live-products-template.csv`、`live-coupons-template.csv`、`live-script-template.csv`。
- 直播中扫描：上传 `live-metrics-template.csv`。
- 下播复盘：上传 `live-post-review-template.csv`。

页面会直接展示 AI 检查结果、风险提醒、下一步动作、节省分钟数和预估节省金额。这个版本不新增数据库表，先用现有后端 Workflow API 验证真实商家是否愿意按模板提交直播数据。
