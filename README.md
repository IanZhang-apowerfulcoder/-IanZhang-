# 挑战杯多 Agent 个性化实训平台 GitHub 施工基线 v0.7

本仓库包是团队协作、接口冻结、Agent 实现、阶段任务和验收的唯一基线。v0.7 的核心治理原则是：

> **M01 先定义并冻结 Agent System Blueprint；成员只在冻结的节点、输入输出、工具权限和分支规则内实现各自 Agent。**

成员可以提交优化建议，但不能在代码中自行改变 Agent 数量、工作流边、共享状态、最终决策权或数据库写入权。

## 先阅读

- 项目负责人：`docs/00_leader_master_control.md`
- 全员：`docs/02_team_roles_and_boundaries.md`、`docs/13_stage_plan_and_quality_gates.md`、`docs/17_github_collaboration.md`
- Agent 开发者：`docs/07_agent_system_blueprint.md`、`docs/08_agent_module_implementation.md`
- 前端：`docs/04_frontend_pages_and_features.md`、`contracts/public-api.yaml`
- 后端：`docs/05_backend_service_construction.md`、两套 OpenAPI
- 数据：`docs/06_database_and_storage.md`
- RAG：`docs/09_adaptive_rag_and_knowledge_build.md`

## 本地架构

浏览器 → 两个 Web 前端 → Public API → 业务后端 → Internal API → Agent Runtime → 专业 Agent/工具 → PostgreSQL/pgvector、Redis、本地文件存储。

开发阶段通过 Docker Compose 启动 PostgreSQL/pgvector 和 Redis；Web、后端和 Agent 服务可本机热更新。GitHub 不保存密钥、真实上传文件、数据库卷和运行日志。

## 文件优先级

1. 当前已批准的阶段任务卡；
2. `contracts/` 中 OpenAPI、JSON Schema 和 Agent Workflow YAML；
3. `docs/07_agent_system_blueprint.md` 与 ADR；
4. 专项施工文档；
5. 角色长期任务书；
6. 原型、示例、会议和聊天记录。

发生冲突时必须停止相关开发并提交变更申请，禁止自行创建第二套标准。
