# 项目接入映射

- `manifest.json` → 知识库版本清单与导入校验。
- `knowledge_nodes.json` → 知识节点、学习路径与画像掌握度。
- `knowledge_edges.json` → 前置、支持、对比、易混与约束关系。
- `rag_chunks.json` → 检索语料与证据引用。
- `practical_tasks.json` → 实操指南与工程任务。
- `question_bank.json` → 分阶测试题。
- `evaluation_cases.json` → 检索、生成、拒答、画像适配和工作流评测。

导入后必须生成不可变 `knowledge_base_version_id`，所有学习会话与评测记录绑定该版本。
