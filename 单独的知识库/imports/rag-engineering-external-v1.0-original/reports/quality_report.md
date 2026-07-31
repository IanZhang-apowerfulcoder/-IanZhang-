# RAG工程实训知识库自动审查报告

- 结构校验：通过
- 错误：0
- 警告：0

## 规模
- `source_count`：28
- `knowledge_node_count`：61
- `core_node_count`：38
- `knowledge_edge_count`：100
- `rag_chunk_count`：244
- `practical_task_count`：15
- `question_count`：183
- `evaluation_case_count`：141
- `learner_profile_count`：5
- `concept_card_count`：61
- `faq_count`：183
- `error_case_count`：122
- `comparison_case_count`：20
- `boundary_case_count`：61
- `code_case_count`：8
- `core_node_chunk_coverage`：1.0
- `core_node_question_coverage`：1.0
- `core_node_evaluation_coverage`：1.0
- `source_reference_integrity`：1.0
- `cross_reference_integrity`：1.0

## 已执行检查
- 8个可导入顶层文件均可解析。
- 7类业务数据通过V8.1知识包JSON Schema。
- 来源、节点、关系、片段、任务、题目和评测引用完整性。
- manifest记录数和SHA-256校验。
- 核心节点片段、题目和评测覆盖。
- 重复标识符与完全重复片段检查。
- 5组虚拟学习者画像与{len(EVALS)}组评测案例存在。

## 不能由静态包直接证明的指标
- 幻觉率低于5%。
- 学习者画像—资源难度适配准确率达到85%。
- 核心知识点覆盖率达到90%。
这些指标必须把知识包导入实际系统，在固定模型、提示词、检索配置和锁定测试集上运行后计算。
