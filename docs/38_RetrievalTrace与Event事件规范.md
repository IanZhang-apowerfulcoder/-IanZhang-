# Retrieval Trace 与 Event 事件规范

新增事件：

`retrieval_query_classified`、`retrieval_plan_created`、`parallel_group_started`、`retrieval_strategy_started/completed/failed`、`evidence_fused`、`evidence_insufficient`、`query_rewritten`、`retrieval_fallback_selected`、`retrieval_completed`、`generation_branch_*`、`review_branch_*`、`route_selected`。

事件必须包含 event_id、sequence_no、workflow_run_id、agent_run_id/ retrieval_run_id、parallel_group_id、event_type、timestamp、payload、correlation_id、causation_id。

前端展示结构化摘要、证据和状态，不展示隐藏思维链。历史回放必须能从事件重建状态；实时页面和回放页面必须明确区分。

## 可交互原型

离线观测台：`prototypes/adaptive-parallel-rag-observability.html`。固定事件：`prototypes/mock-adaptive-parallel-events.json`。正式实现必须由后端 Event Store 与 SSE 驱动，并明确标识实时运行和历史回放。
