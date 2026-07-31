# 自适应多策略 RAG 接入规范

## 分工

- RAG Router Agent：分析问题并输出 Retrieval Plan；
- Retrieval Engine：执行具体策略；
- Evidence Fusion：去重、归一化、重排和冲突标记；
- Evidence Sufficiency Judge：判断是否补检索、拒答或转人工；
- Generation / Review：消费和验证 Evidence Bundle。

## 第一版策略

| 策略 | 适用问题 |
|---|---|
| metadata_filtered | 指定模块、难度、节点、资源类型或审核状态 |
| hybrid | 普通事实、定义和单知识点问答 |
| graph_assisted | 前置关系、依赖、因果和多跳路径 |
| parent_child | 长文档、章节上下文和多粒度证据 |
| agentic_decomposition | 复杂故障、多个子问题或首轮证据不足 |

## 硬约束

最多 5 个规划步骤、2 次补检索、3 条并行策略；证据不足不得强行生成；所有最终专业结论绑定 evidence_id；只保存结构化路由原因，不保存模型隐藏思维链。
