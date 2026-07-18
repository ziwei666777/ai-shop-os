# Commerce Dataset V0.1

## 开发目标

Commerce Dataset 是 AI Commerce OS 的第一优先级基础能力。

本模块不做订单系统、商品系统、库存系统、ERP 或 CRM，而是把商家已有平台数据整理成 AI Customer、AI AfterSale、AI Operation 可以共同使用的标准数据集。

## 商业价值

- 让商家可以在 1 天内导入历史数据，开始看到 AI 是否能减少人工。
- 让 Replay Engine 可以用真实历史订单、消息和售后重新跑一遍 AI 决策。
- 让 Evaluation Engine 可以计算准确率、人工接管率、错误率和节省工时。
- 让 Training Center 可以收集商家修改样本，逐步沉淀 Memory、Knowledge 和 Workflow。

## 当前范围

第一批支持的数据类型：

- Products：商品基础信息。
- Orders：订单主表。
- Order Items：订单明细。
- Customers：客户基础信息。
- Shipments：物流信息。
- After Sales：售后、退款、退货、投诉和赔偿。

当前暂不开发：

- Reviews。
- Inventory。
- Coupons。
- Advertisements。
- Competitors。

这些数据会进入后续迭代，不能在本轮扩散。

## 输入格式

支持：

- CSV。
- Excel `.xlsx`。
- JSON。

JSON 只接受：

- 顶层数组。
- 或顶层对象中包含 `items`、`rows`、`data` 数组字段。

JSON 每一行必须是对象。复杂字段会转成 JSON 字符串进入预览，不执行任何脚本或公式。

## 数据库原则

本轮不修改数据库。

优先复用现有表：

- `products`
- `orders`
- `customers`
- `messages`
- `after_sale_cases`
- `shipments`
- `import_jobs`
- `learning_events`

如果未来需要 dataset 元数据表，必须先提交数据库设计并等待确认。

## Replay 方法

后续 Replay Engine 读取同一批标准数据：

1. 读取历史订单、消息、物流和售后。
2. 让 AI Customer、AI AfterSale、AI Operation 重新生成建议。
3. 对比历史人工结果和 AI 结果。
4. 输出准确率、人工接管率、错误率和节省时间。

## Evaluation 指标

本模块先输出数据可用性指标：

- 数据类型覆盖率。
- 必填字段完整率。
- 字段映射完成率。
- 文件预览成功率。
- 导入任务成功率。
- 单行错误率。
- 可用于 Replay 的记录数。

这些指标决定真实商家是否能连续使用 30 天。

## 数据准备度 API

当前已新增：

```text
GET /v1/commerce-dataset/readiness
```

该接口会把商品、订单、客户、客服消息、售后和物流统计成统一快照：

- 每类数据当前记录数。
- 每类数据准备度。
- 是否可以进入 Replay。
- 预计可回放样本数。
- 下一步导入建议。

`/commerce-dataset` 页面已经改为读取该接口，不再只展示静态百分比。

Evaluation Engine 也会读取这份准备度，把“真实数据是否足够”纳入 AI 团队评分。
