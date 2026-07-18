# mall-app-web 参考吸收记录

## 结论

`mall-app-web` 是一个成熟的移动端商城前台项目，技术栈是 `uni-app + Vue3 + TypeScript`。

本项目不直接引入它的框架、页面、环境变量和支付/购物车逻辑。

本次只吸收它对 AI Commerce OS 有价值的电商字段和流程。

## 已吸收内容

### 订单字段

已加入导入字段自动识别：

- `orderSn` → 平台订单号。
- `memberUsername` / `memberNickname` / `receiverName` → 客户名称。
- `payAmount` / `totalAmount` → 订单金额。
- `paymentTime` / `createTime` → 付款或创建时间。

商业价值：

- AI客服可以更容易查订单。
- Replay Engine 可以用历史订单复盘 AI 判断。
- Evaluation 可以统计订单数据准备度。

### 商品字段

已加入导入字段自动识别：

- `productName` → 商品名称。
- `productSkuCode` / `productSn` → SKU 或商家编码。
- `productPrice` / `productRealPrice` → 价格。
- `realStock` → 可售库存。

商业价值：

- AI客服回答商品咨询更稳。
- AI运营后续能发现商品详情、库存、价格问题。

### 售后字段

已加入导入字段自动识别：

- `orderSn` → 关联订单号。
- `reason` / `description` → 售后原因。
- `proofPics` → 售后凭证图片。

商业价值：

- AI售后可以判断售后证据是否完整。
- 高风险退款、赔偿、投诉可以进入人工审批。
- Replay 可以对比历史人工售后处理和 AI 建议。

## 未吸收内容

不吸收：

- uni-app / Vue 架构。
- 购物车。
- 支付。
- 收货地址管理。
- 消费者端会员中心。
- `.env` 环境文件。
- 图片素材和品牌资源。

原因：

AI Commerce OS 的核心不是做商城，而是让 AI 员工帮助商家工作。

订单、商品、库存、支付等系统应优先对接成熟平台或 ERP，不重复开发。

## 对 Replay / Evaluation 的作用

吸收这些字段后，商家上传成熟商城或 ERP 导出的 JSON / CSV / Excel 时，系统能更准确地自动匹配字段。

这会提升：

- 导入成功率。
- 字段完整率。
- 可回放样本数。
- AI客服查单准确率。
- AI售后风险判断准确率。

## 下一步

下一步可以继续参考成熟商城的：

- 订单状态枚举。
- 退货原因枚举。
- 商品属性结构。
- 物流状态结构。

但仍然只吸收字段和流程，不吸收框架。
