# AI Commerce OS 验证引擎 V0.1

## 一、目标

本阶段不再继续堆 Agent，而是证明 AI 客服、AI 售后、AI 运营是否真的能替代一部分人工。

验证链路分为三层：

```text
Replay Engine
↓
Evaluation Engine
↓
Training Center
↓
Simulation Engine
```

## 二、Evaluation Engine

页面：

```text
/evaluation
```

接口：

```text
GET /v1/evaluation/summary
```

作用：

- 告诉老板 AI 团队今天几分。
- 告诉老板当前能省多少钱。
- 告诉老板哪里还不能放权。
- 把 Replay 结果转成老板能理解的评分。

当前指标：

- 判断准确率。
- 人工接管率。
- 高风险拦截。
- 4 万/月人工成本替代进度。
- 真实数据准备度。

Evaluation 当前会读取：

```text
GET /v1/commerce-dataset/readiness
```

如果商品、订单、客户、消息、售后、物流数据不足，AI 评分会明确提示不能承诺替代完整岗位。

Evaluation 当前也会读取真实 Replay 输出。Replay 已优先使用商家业务数据生成样本，而不是只依赖固定样例。

## 三、Training Center

页面：

```text
/training-center
```

接口：

```text
GET /v1/training-center/summary
```

作用：

- 收集老板修改 AI 回复的样本。
- 收集老板审批售后的样本。
- 把经验分类为 Memory、Knowledge、Workflow。
- 一旦系统产生真实 `learning_events`，训练中心会优先展示真实样本；没有真实样本时才显示 V0 样例。

当前规则：

- 客服话术修正优先进入 Memory。
- 商品、物流、优惠、FAQ 优先进入 Knowledge。
- 退款、赔偿、投诉、审批优先进入 Workflow。

当前真实学习规则：

- 客服消息修正会进入 Memory 或 Knowledge。
- 售后、退款、赔偿、投诉、审批相关样本会进入 Workflow。
- 被拒绝、内容过短、修改前后完全一致的样本会标记为待复核。

当前沉淀方式：

- Training Center 会为每条学习样本生成 Memory、Knowledge、Workflow 候选资产。
- 候选资产会展示业务价值和来源样本。
- 老板点击确认后，候选资产可以写入长期 Memory、Knowledge、Workflow 存储。
- Memory 会写入 `memories`。
- Knowledge 会写入 `knowledge_sources` 和 `knowledge_chunks`。
- Workflow 会写入 `workflows` 草稿。
- 未确认的候选不会直接进入长期存储，避免 AI 未经确认永久学习错误经验。

## 四、Simulation Engine

页面：

```text
/simulation
```

接口：

```text
GET /v1/simulation/summary
```

作用：

- 在真实商家上线前，用模拟客户压测 AI。
- 覆盖咨询、砍价、退款、投诉、私域跟进等场景。
- 验证 AI 是否会乱承诺、乱退款、乱投流。

当前安全规则：

- 物流、发货等低风险问题可以自动回复。
- 砍价、优惠金额必须人工确认。
- 退款、投诉、赔偿必须审批。
- 私域和投流建议可以生成草稿，但预算必须审批。

## 五、当前限制

当前 V0.1 使用固定样例，不调用真实 LLM，不自动执行平台动作，不修改数据库。

真实商家试用前必须继续完成：

- 接入真实历史消息、订单、售后数据。
- 把导入数据转换为 Replay 样本。
- 把老板修改写入 Training Center。
- 每天自动生成 Evaluation 评分。
