# CHANGELOG

## 2026-07-12

### Added

- 新增 Sites 无依赖宣传站发布包脚本 `tools/create_sites_vinext_promo_archive.py`，用于线上部署 ToB 宣传页。

- 新增 `PROJECT_GUIDE.md`，固化 AI Commerce OS 长期开发原则。
- 新增 `PROJECT_STATE.md`，记录当前产品状态、完成度、阻塞点和安全边界。
- 新增 `NEXT_TASK.md`，明确下一阶段只开发 Commerce Dataset，不继续新增 Agent。
- 新增 `IDEAS.md`，用于收纳暂不开发的新想法。
- 新增产品宣传书 `docs/product-brochure.md`。
- 新增一页版宣传书 `docs/product-brochure-one-page.md`。
- 新增宣传主视觉图 `assets/marketing/ai-commerce-os-hero.png`。
- 新增中文宣传海报 `assets/marketing/ai-commerce-os-poster.svg`。
- 新增 ToB 商务版主视觉图 `assets/marketing/ai-commerce-os-b2b-hero.png`。
- 新增 ToB 商务版 PPT `assets/marketing/AI-Commerce-OS-B2B-Deck.pptx`。
- 新增 PPT 生成脚本 `tools/create_b2b_marketing_pptx.py`。
- 新增商务路演版 PPT `assets/marketing/AI-Commerce-OS-Business-Roadshow-Deck.pptx`。
- 新增商家成交版 PPT `assets/marketing/AI-Commerce-OS-Merchant-Sales-Deck.pptx`。
- 新增商家成交版 PPT 生成脚本 `tools/create_merchant_sales_pptx.py`。
- 新增 ToB 宣传网站页面 `/promo`。
- 新增可点击演示界面，支持切换 AI客服、AI售后、AI运营和老板审批。
- 新增前端公开营销素材 `apps/web/public/marketing/ai-commerce-os-b2b-hero.png`。

### Changed

- 将项目最高优先级调整为 Commerce Dataset、Replay Engine、Simulation Engine、Evaluation Engine、Training Center。
- 明确当前目标是节省电商人力成本，优先验证 AI Customer、AI AfterSale、AI Operation 是否能替代岗位工作。
- 将 PPT 从主要演示材料降级为辅助材料，优先使用 `/promo` 做商家演示。

### Notes

- 当前不修改数据库。
- 当前不重构目录。
- 当前不引入新框架。
- 当前不推倒重来。
