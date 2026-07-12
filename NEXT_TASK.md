# NEXT_TASK

更新时间：2026-07-12

## 当前唯一任务

开发 Commerce Dataset 模块。

本轮不要开发新 Agent，不要重构目录，不要修改已确认的数据库设计。

## 为什么先做 Commerce Dataset

AI Commerce OS 当前最缺的不是页面，而是可验证的数据底座。

没有标准数据集，就无法做：

- Replay Engine
- Simulation Engine
- Evaluation Engine
- Training Center

因此下一步必须先统一电商数据集，让 AI Customer、AI AfterSale、AI Operation 都使用同一套标准数据。

## 本轮开发目标

建立 Commerce Dataset 的最小可用版本。

要求：

- 支持 CSV、Excel、JSON 导入。
- 支持导入预览。
- 支持字段映射。
- 支持导入校验。
- 支持导入结果统计。
- 支持作为 Replay Engine 的输入。

## 本轮数据范围

第一批数据类型：

- Products
- Orders
- Customers
- Messages
- Refunds
- Logistics
- Support Tickets

暂不做：

- Reviews
- Inventory
- Coupons
- Advertisements
- Competitors

这些放入后续迭代。

## 实施边界

允许：

- 在当前导入模块上增量扩展。
- 增加前端页面内部 tab 或区块。
- 增加后端应用层服务。
- 增加文档。
- 增加测试。

不允许：

- 推倒重来。
- 修改整体架构。
- 新增大量框架。
- 自研完整订单系统。
- 自研完整商品系统。
- 自动抓取闲鱼、淘宝、抖音非授权数据。

## 是否需要数据库修改

原则上先不修改数据库。

优先复用当前已有：

- products
- orders
- customers
- messages
- after_sale_cases
- shipments
- import_jobs
- learning_events

如果确实需要新增 dataset 元数据表，必须先提出数据库修改方案，等待确认。

## 技术设计要求

后端：

- 保持 Clean Architecture。
- 新增 Dataset service 不直接耦合具体 Agent。
- 文件解析继续使用当前 CSV、Excel 能力。
- JSON 导入必须做 schema 校验。
- 单行错误不能中断整批导入。

前端：

- 复用现有 `/settings/data-import`。
- 增加“标准数据集”视角。
- 用中文解释每类数据的用途。
- 显示导入质量和缺失字段。

## 验收标准

本轮完成后应能做到：

- 商家上传历史订单、客户、消息、售后数据。
- 系统识别数据类型。
- 系统预览字段和样例。
- 系统提示缺失字段和风险。
- 系统保存导入任务。
- 后续 Replay Engine 可以读取这些数据。

## 测试要求

必须执行：

- `npm.cmd run typecheck:web`
- `npm.cmd run lint:web`
- `npm.cmd run build:web`
- `npm run api:test`

至少新增或更新测试覆盖：

- CSV 导入。
- Excel 导入。
- JSON 导入。
- 缺失必填字段。
- 错误金额。
- 重复订单。
- 多平台同订单号不冲突。

## 完成后必须更新

开发完成后必须更新：

- `PROJECT_STATE.md`
- `CHANGELOG.md`
- 如产生新想法但未开发，写入 `IDEAS.md`
