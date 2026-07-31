# 自适应多策略 RAG 与 RAG Router Agent

## 1. Router 输入

问题、任务类型、学习者摘要、目标知识点、知识库版本、风险、资源类型、最大难度和预算。

## 2. Router 输出

`query_type`、`complexity`、`risk_level`、`execution_mode`、`selected_strategies`、`sub_queries`、`filters`、`max_steps`、`max_retries`、`reason_summary`。

## 3. 路由规则

- 单点事实/定义：Metadata + Hybrid；
- 前置/依赖/路径：Metadata + Graph-Assisted + Hybrid，并行；
- 长文档/章节上下文：Metadata + Parent-Child + Hybrid，并行；
- 多组件故障/多跳/首轮不足：受限 Agentic 模式；
- 高风险或证据冲突：强制多维审核或人工。

## 4. Agentic 限制

最多 5 个规划步骤、2 次补检索、3 条并行策略、60 条融合前候选。达到上限仍不足则拒答或人工，不允许无限自反思。

## 5. Router 不是检索器

Router 负责选择和计划；P7 的 Retrieval Engine 执行策略；Evidence Fusion 去重和融合；Sufficiency 产出结构化充分性。这样可以独立评测“路由是否正确”和“检索是否有效”。
