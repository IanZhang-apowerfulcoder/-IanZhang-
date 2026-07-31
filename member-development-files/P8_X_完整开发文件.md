# P8 X 完整开发文件

## 长期角色

平行资源生成 Agent 与资源编排

## 长期负责

- Explanation Generator Agent
- Practice Generator Agent
- Quiz Draft Agent
- Resource Generation Coordinator
- 个性化讲义/实操/分阶题资源结构
- 审核打回后的定向修复

## 明确不负责

- 自行检索未授权知识
- 修改学习路径
- 自己批准自己的资源
- 把无 evidence_id 的专业结论发布

## 必读文件

- `docs/07_七核心智能体与平行Agent职责.md`
- `docs/09_数据流与调用链.md`
- `docs/14_测试与验收标准.md`
- `docs/36_平行Agent生产与审核架构.md`

## 必须遵守的契约

- `contracts/jsonschema/agents/resource_input.schema.json`
- `contracts/jsonschema/agents/explanation_output.schema.json`
- `contracts/jsonschema/agents/practice_output.schema.json`
- `contracts/jsonschema/agents/quiz_draft_output.schema.json`
- `contracts/jsonschema/agents/resource_output.schema.json`
- `contracts/jsonschema/services/evidence_bundle.schema.json`

## 主要复核人

P1, P3, P7, P9

## S0 范围、架构与契约冻结

### 任务
- 冻结三类平行生成 Agent 和 Coordinator 契约
- 定义修订指令字段

### 交付物
- Generation Schemas
- 资源模板

### 验收
- 三分支职责无重复
- 所有专业段落要求 evidence_ids
## S1 GitHub 骨架与全 Mock 闭环

### 任务
- 提供讲义/实操/题目分支 Mock 和聚合资源 Mock

### 交付物
- Generation Mock

### 验收
- 三类资源格式完整
- 聚合不丢引用
## S2 知识库 v2 与检索执行器

### 任务
- 使用 Domain Pack v2 样例验证资源模板和引用

### 交付物
- Grounded Resource Fixtures

### 验收
- 所有示例 evidence_id 有效
- 不引用未启用内容
## S3 RAG Router 与 Agentic Retrieval

### 任务
- 适配自适应 Evidence Bundle 和多子问题证据

### 交付物
- Evidence Adapter

### 验收
- 多策略来源合并不重复
- 证据不足时拒绝生成确定性结论
## S4 诊断、路径、平行生成与测评

### 任务
- 实现 Explanation/Practice/Quiz 三个平行 Agent 和 Resource Coordinator
- 实现定向修复

### 交付物
- Generation Agents v1

### 验收
- 三资源形态通过率 >=99%
- 内容覆盖目标知识点 >=90%
- 修订只重跑受影响分支
## S5 平行审核、仲裁与完整闭环

### 任务
- 接入四维审核和修订循环
- 优化一致性

### 交付物
- Reviewed Generation Flow

### 验收
- 审核打回后修复成功率 >=85%
- 最多重试 2 次
- 无自审
## S6 全站体验、可观测性与高强度验证

### 任务
- 质量、成本和延迟优化
- 生成单路/并行消融

### 交付物
- Generation Eval Report

### 验收
- 并行完整性显著优于单路基线
- P95 在预算内
- 重复率受控
## S7 发布、演示与比赛提交

### 任务
- 冻结演示资源和 Prompt 版本

### 交付物
- Generation Release

### 验收
- 演示资源可复现
- Prompt/模型版本记录完整
