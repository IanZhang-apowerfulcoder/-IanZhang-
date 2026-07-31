# GitHub 协作规则

## 分支

- `main`：稳定、可演示、可发布；
- `develop`：通过阶段内验收的集成分支；
- `feature/<task-id>-<name>`：功能；
- `fix/<task-id>-<name>`：缺陷；
- `test/<task-id>-<scope>`：评测；
- `docs/<task-id>-<scope>`：文档。

## 核心原则

1. 一个任务卡对应一个分支和一个 PR；
2. 公共 API、Schema、状态机、Agent Blueprint、数据库主表和知识版本不得口头修改；
3. Agent 模块必须按统一输入输出 Schema 开发；
4. 前端不得直连模型、Agent 或数据库；
5. Agent 不得直接写权威业务表；
6. 所有专业结论必须绑定 `evidence_id`；
7. 平行 Agent 只能提交候选结果，不能各自写最终决策；
8. 所有核心 PR 至少 1 名 Owner + 1 名跨模块 Reviewer；
9. 指标必须由固定数据集和脚本复现。

## PR 必须包含

- 任务卡编号；
- 修改范围与不修改范围；
- 依赖的 API/Schema 版本；
- 自动测试结果；
- 接口请求/响应样例或 UI 录屏；
- 已知限制；
- 回滚方案；
- 对验收标准逐条自检。
