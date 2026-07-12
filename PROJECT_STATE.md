# PROJECT_STATE

更新时间：2026-07-12

## 一、当前阶段

项目处于 V0.x。

当前不是完整可商用产品，而是 AI Commerce OS 的基础骨架和商家试用原型。

核心方向已经从“继续堆 Agent 页面”调整为“验证 AI 是否真的能替代电商岗位工作”。

## 二、当前产品形态

当前系统是一套浏览器里的 AI 电商员工控制台。

已有模块：

- Dashboard 老板首页。
- AI Employees AI员工框架。
- AI Customer 工作台。
- AI AfterSale 工作台。
- 订单、商品、客户基础表格。
- 平台集成入口。
- 淘宝、抖音、闲鱼数据导入入口。
- AI客服商家使用说明书。
- ToB 宣传网站 `/promo`。

## 三、当前架构

Monorepo：

- `apps/web`：Next.js 前端。
- `apps/api`：FastAPI 后端。
- `packages/shared`：共享常量与类型。
- `supabase/migrations`：数据库迁移。
- `docs`：架构、数据库、部署、说明文档。

已采用：

- Next.js
- React
- TypeScript
- TailwindCSS
- FastAPI
- SQLAlchemy
- Supabase PostgreSQL
- pgvector 预留
- Redis/RQ 预留
- LangGraph 预留

## 四、当前完成度

距离“替代深圳约 4 万/月电商团队”的目标：

- AI Customer：约 35%
- AI AfterSale：约 25%
- AI Operation：约 10%
- 整体：约 20% 到 25%

当前结论：已经有试用入口和数据结构，但还不能替代完整团队。

## 五、已完成能力

AI Customer：

- 平台消息收件箱。
- AI 回复草稿。
- 自动回复与人工确认状态。
- 人工接管。
- 商家修改记录。
- 使用说明书。
- 高风险问题暂停规则。

AI AfterSale：

- 售后工作台。
- 售后 case 列表。
- 风险等级。
- AI 判断和审批建议。
- 高风险售后必须人工确认。

Commerce Data：

- 淘宝、抖音、闲鱼导入结构。
- 商品、订单、客户、物流、售后导入接口。
- CSV、Excel 文件预览和导入基础能力。

文档：

- 架构文档。
- 数据库文档。
- Supabase 配置说明。
- 客服使用说明书。
- 部署形态说明。
- AI团队替代进度说明。

## 六、未完成关键能力

当前阻塞正式商用的能力：

- Supabase migration 尚未确认已执行到远程数据库。
- `DATABASE_URL` 仍需真实数据库密码。
- Redis/RQ Worker 尚未部署。
- 淘宝、抖音真实开放平台凭证尚未配置。
- 真实平台消息尚未自动进入 AI Customer。
- Memory、Knowledge、Workflow 尚未形成真实学习闭环。
- Replay Engine 尚未开发。
- Simulation Engine 尚未开发。
- Evaluation Engine 尚未开发。
- Training Center 尚未开发。
- AI Operation 仍处于预留和规划阶段。

## 十一、当前演示材料

当前主要演示入口：

```text
/promo
```

该页面用于 ToB 商务演示，包含：

- 产品定位。
- 成本痛点。
- AI客服、AI售后、AI运营说明。
- 可点击演示界面。
- 7 天试用流程。
- 验收指标。

PPT 文件继续保留，但不作为主要演示材料。此前手写 OpenXML PPT 在部分查看器中可能空白，因此优先用宣传网站进行演示。

## 七、当前最高优先级

下一阶段优先级：

1. Commerce Dataset
2. Replay Engine
3. Evaluation Engine
4. Training Center
5. Simulation Engine

暂时不要新增更多 Agent。

## 八、当前安全边界

AI 可以：

- 生成客服回复草稿。
- 判断是否需要人工。
- 标记售后风险。
- 输出运营建议草稿。
- 记录商家修改。

AI 不可以：

- 自动退款。
- 自动赔偿。
- 自动投广告。
- 自动调整预算。
- 自动承诺优惠金额。
- 自动导出客户隐私数据。
- 绕过平台官方授权抓取数据。

## 九、下一步验收指标

下一阶段必须开始围绕指标开发：

- 客服自动回复率。
- 客服错误率。
- 人工接管率。
- 售后分类准确率。
- 售后高风险拦截率。
- 运营建议采纳率。
- 每日节省人工分钟数。
- 预估节省人力成本。

## 十、交付包

当前已生成安全源码包：

```text
dist/AI-Shop-OS-current-package.zip
```

该包不包含真实 `.env`、`.env.local`、`.venv`、`node_modules`、`.next`、日志和密钥。
