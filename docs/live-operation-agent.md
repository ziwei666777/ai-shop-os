# AI Live Operation Agent 直播运营助理

## 目标

直播运营助理不是聊天机器人。

它要替代直播运营助理每天重复做的检查、盯盘和复盘工作。

第一阶段替代岗位：

- 直播运营助理
- 直播场控助理
- 直播复盘助理

第一阶段目标：

- 每天节省 3 到 5 小时人工。
- 每月验证 6000 到 12000 元岗位价值。
- 所有节省时间进入 Savings Engine。

## 当前已实现接口

### 1. 开播前检查

```text
POST /v1/live-operations/pre-live-check
```

输入：

- 商品标题
- 商品库存
- 安全库存
- 日常价
- 直播价
- 优惠券剩余数量
- 优惠券是否过期
- 直播脚本
- 赠品是否准备
- 商品排序是否准备

输出：

- 检查项
- 阻塞项
- 预警
- 建议动作
- 节省分钟
- 预估节省金额

### 2. 直播中扫描

```text
POST /v1/live-operations/live-metric-scan
```

输入：

- 在线人数
- 成交率
- 停留率
- 评论数
- 点赞数
- 商品点击率
- 库存变化
- 异常订单数

输出：

- 在线人数风险
- 成交率风险
- 停留率风险
- 商品点击率风险
- 库存消耗风险
- 异常订单风险
- 主播下一步建议

### 3. 下播复盘

```text
POST /v1/live-operations/post-live-review
```

输入：

- 销售额
- 订单数
- 观看人数
- 退款数
- 爆款商品
- 负面评论数
- 主播脚本得分

输出：

- 成交率
- 退款风险
- 主播表现建议
- 第二天直播建议
- 节省分钟
- 预估节省金额

## 当前规则边界

AI 可以：

- 检查库存风险。
- 检查优惠券风险。
- 检查价格风险。
- 检查脚本违禁词。
- 监控直播中指标。
- 输出主播提醒。
- 生成下播复盘。
- 计算节省时间和金额。

AI 不可以：

- 自动改价。
- 自动改优惠券。
- 自动改商品排序。
- 自动承诺赔偿。
- 自动处理退款。
- 自动控制直播间。

涉及价格、优惠券、赔偿、退款、广告预算的动作必须老板审批。

## 接真实数据时的映射

抖店、淘宝直播、天猫直播或其它平台的数据不要直接进入 Agent。

必须先映射为统一字段：

- `products`
- `coupons`
- `script_text`
- `online_users`
- `conversion_rate`
- `retention_rate`
- `comment_count`
- `like_count`
- `product_click_rate`
- `inventory_delta`
- `abnormal_order_count`
- `sales_amount_yuan`
- `order_count`
- `viewer_count`
- `refund_count`
- `top_product_title`
- `negative_comment_count`
- `host_script_score`

然后再进入 Workflow。

## 下一步

1. 建立直播数据导入模板。
2. 建立直播 Workflow 日志。
3. 把每次检查结果写入 Savings Engine。
4. 接入真实抖店或淘宝直播数据。
5. 在老板日报里展示直播异常和第二天建议。

## 直播 Workflow 日志

```text
GET /v1/live-operations/runs
```

每次执行开播前检查、直播中扫描、下播复盘，系统都会记录一条 Workflow 运行日志。

日志包含：

- 工作流名称
- 阶段
- 状态
- 分数
- 节省分钟
- 节省金额
- 预警数量
- 是否需要老板审批
- 证明文本
- 创建时间

当前日志先保存在内存中，用于验证口径。正式商家试点前，需要等数据库设计确认后落到 Supabase。

## 更新后的下一步

1. 建立直播数据导入模板。
2. 把直播 Workflow 日志迁移到 Supabase 持久化表。
3. 把每次检查结果持续写入 Savings Engine。
4. 接入真实抖店或淘宝直播数据。
5. 在老板日报里展示直播异常和第二天建议。