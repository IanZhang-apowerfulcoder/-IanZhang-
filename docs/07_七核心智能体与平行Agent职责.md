# 七核心智能体与平行 Agent 职责

## 七个核心 Agent

1. Diagnosis Agent：定位已掌握、薄弱和误区；
2. Path Planning Agent：提出候选学习路径；
3. RAG Router Agent：分析问题并生成 Retrieval Plan；
4. Resource Generation Coordinator Agent：调度并整合三路生成；
5. Assessment/Evaluation Agent：生成或评价测评；
6. Review Coordinator Agent：调度并整合四路审核；
7. Arbitration Agent：在确定性状态机约束下给出唯一最终动作。

## 平行生成 Agent

- Explanation Generator：讲义、解释、类比、示例；
- Practice Generator：实操步骤、代码或工程任务；
- Quiz Draft Agent：分阶题目、答案草稿和 Rubric 草稿。

## 平行审核 Agent

- Factuality Reviewer：claim-evidence 对齐、事实和来源；
- Difficulty Reviewer：画像、难度、前置知识和认知负荷；
- Assessment Quality Reviewer：答案、干扰项、Rubric 和可判定性；
- Safety Reviewer：隐私、越权、Prompt Injection、危险操作和合规。

## 统一要求

- 所有 Agent 输入输出必须通过 JSON Schema；
- 输出只保留结构化理由摘要，不保存隐藏思维链；
- Agent 只能使用工具目录中授权的工具；
- 专业结论必须引用 evidence_id；
- 平行 Agent 不拥有最终决策权；
- 重试和循环由 Runtime 控制，Prompt 不得自行无限循环。
