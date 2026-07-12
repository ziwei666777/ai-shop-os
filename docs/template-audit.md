# GitHub 模板审计记录

## 审计目标

优先复用成熟模板的通用能力，减少重复开发；同时保护 AI Shop OS 的长期架构，不让模板反向决定业务模型。

## 已审计模板

| 模板 | 结论 | 原因 |
| --- | --- | --- |
| `Barty-Bart/nextjs-supabase-shadcn-boilerplate` | 部分复用思路 | Supabase SSR Auth 和主题切换思路有价值，但未发现明确许可证，不直接复制源码。 |
| `shadcn-examples/shadcn-ui-dashboard` | 不直接采用 | 依赖过重，包含 Paddle、GA、Umami、AI SDK 等非当前 Sprint 必需依赖，且未发现明确许可证。 |
| `horizon-ui/shadcn-nextjs-boilerplate` | 不直接采用 | MIT 许可可商用，但依赖过重，包含 Stripe、S3、OpenAI、service role 管理和 `preinstall` 脚本，不适合并入当前项目。 |
| `Marc-Kruiss/supabase_ssr_auth-nextjs_14-shadcn-template` | 不直接采用 | 认证思路可参考，但项目绑定 Prisma 且维护时间较旧，未发现明确许可证。 |

## 当前采用策略

- 不整套覆盖现有项目。
- 保留当前 monorepo、FastAPI、Clean Architecture、DDD 领域模型。
- 复用模板级能力：
  - 后台 App Shell 信息架构。
  - shadcn 风格组件拆分方式。
  - `next-themes` 暗色模式能力。
  - Supabase SSR Auth 的设计方向，后续单独实现。

## 安全边界

- 不复制没有明确许可证的模板源码。
- 不引入支付、广告统计、S3、service_role 管理等非必要依赖。
- 不执行模板里的初始化脚本、部署脚本或数据库重置脚本。
- 不把 `.env`、数据库密码、Supabase `service_role` 写入前端。
- 所有模板代码只作为参考，业务实现继续归入 AI Shop OS 自有模块。

## 本轮实际改进

- 新增 `next-themes`，用于稳定管理浅色、暗色和系统主题。
- 新增全局 `ThemeProvider`。
- 新增 `ThemeToggle`。
- 升级 `AppShell`：侧边栏图标、当前页高亮、移动端导航、顶部状态栏。
- 调整全局色彩为更中性的企业级界面，避免单一色系。
- 将 `next` 与 `eslint-config-next` 从 14 系升级到 15.5.18，消除 npm audit 中的高危 Next.js 风险。
- 新增 Supabase SSR Auth middleware，保护 Dashboard、AI Employees、Settings 等业务页面。
- 登录成功后会回到原访问路径，退出登录会回到 `/login`。
- 新增轻量表格原语和详情抽屉，吸收 dashboard 模板的列表/详情工作台形态，但不复制无许可证源码。
- AI客服、AI售后工作台升级为指标卡、搜索、筛选、表格、详情抽屉和商家动作记录。

## 依赖安全备注

- 当前 npm audit 剩余 2 个中危项，来源是 Next.js 内部锁定的 `postcss@8.4.31`。
- 已尝试使用 npm override 升级 PostCSS，但会导致 Next 依赖树进入 invalid 状态，因此已撤销。
- 暂不执行 `npm audit fix --force`，因为它会进行不可控的大版本降级或升级。
- 后续建议跟踪 Next.js 官方补丁线，等待 Next 内部 PostCSS 依赖升级后再处理。
- Next 15 已提示 `next lint` 会在 Next 16 移除；后续升级 Next 16 前，需要把 lint 脚本迁移到 ESLint CLI。
