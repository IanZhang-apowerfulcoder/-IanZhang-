# 项目交付与使用说明 v7.0

## 1. 本仓库是什么

本仓库是以 `-IanZhang--main-2(1).zip` 为唯一最新基线，完成九人制重构后的统一 GitHub 施工包。它包含：

- 产品范围、总体架构、用户流程和数据流；
- 七个核心 Agent 与七个平行专业子 Agent 的冻结蓝图；
- 自适应多策略 RAG、有限 Agentic 补检索和唯一仲裁；
- Public、Internal、Knowledge API；
- JSON Schema、数据库、Mock、事件和 Trace；
- 九人长期职责、72 张阶段任务卡和 9 份独立开发包；
- 合并后的企业级 RAG 工程知识库 v2；
- 比赛提交映射、评测口径和演示原型。

## 2. 推荐使用顺序

### 项目负责人

1. 阅读 `README.md`；
2. 阅读 `docs/00_总索引.md`；
3. 审批 `project/agent_blueprint.yaml` 与 `project/learning_workflow.yaml`；
4. 依据 `docs/04_阶段开发计划.md` 下发当前阶段任务；
5. 依据 `docs/14_测试与验收标准.md` 决定 ACCEPTED 或 REWORK。

### 团队成员

1. 打开 `members/Px_姓名/00_开始这里.md`；
2. 阅读自己的长期开发文件；
3. 只执行当前阶段 `tasks/Sx/Px.md`；
4. 严格遵守自己的 API、Schema 和 Mock；
5. 通过 PR 提交代码、测试证据、限制和回滚说明。

## 3. 开发阶段运行方式

开发期优先本地运行：

```text
浏览器
→ 本地前端
→ 本地业务后端 Public API
→ 本地 Agent Runtime / Retrieval Engine
→ PostgreSQL + pgvector / Redis / 本地对象存储
```

部署时再把相同逻辑容器部署到 Linux 服务器。前端不得直接访问数据库、模型或专业 Agent。

## 4. 校验命令

```bash
pip install -r requirements-dev.txt
make validate
make validate-kb
```

## 5. 事实标准

1. 当前批准的任务卡；
2. `api/` 和 `contracts/jsonschema/`；
3. `database/schema.sql`；
4. `project/agent_blueprint.yaml` 和工作流；
5. 专项设计文档；
6. Mock、示例和原型；
7. 口头说明。

## 6. 交付状态

知识库服务可以独立运行和测试；其余业务应用是高完整度施工基线、契约和工程骨架，仍需九名成员按 S0-S7 实施。完整验证见 `reports/final_validation_report.md`，限制见 `reports/known_limitations.md`。
