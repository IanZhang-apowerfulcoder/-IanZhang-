# 七核心智能体与平行子 Agent 使用规范

## 核心 Agent

1. Diagnosis Agent：提出画像与盲区建议；
2. Path Planning Agent：提出学习目标和顺序；
3. RAG Router Agent：生成检索计划；
4. Resource Coordinator：调度讲义、实操、题目三个平行生成分支；
5. Assessment/Evaluation Agent：评价学员表现；
6. Review Coordinator：汇总事实、难度、题目、安全四个平行审核分支；
7. Arbitration Agent：唯一最终业务裁决。

## 知识库权限

- RAG Router 只读取元数据和策略目录；
- Retrieval Engine 读取切片、关系和索引；
- 生成分支只消费 Evidence Bundle，不自行检索或编造来源；
- 审核分支重新读取原始 evidence，不只相信生成 Agent 的摘要；
- Arbitration 读取结构化意见，但不能绕过后端权限和状态机；
- 任何 Agent 都不能直接写权威画像、路径、资源发布或知识版本表。

## 并行原则

有限并行、专业分工、统一融合、唯一仲裁。简单问题不得无条件启动全部检索和审核分支。
