# 挑战杯 XH-202630 项目开发基线 v7.0.0

> 基于预构建、可持续迭代的专业知识库，通过 RAG Router Agent 按问题类型选择和组合检索策略，并利用有限平行 Agent 完成个性化资源生产、交叉审核、测评和唯一仲裁。

## 当前唯一执行基线

本仓库以用户指定的 `-IanZhang--main-2(1).zip` 为结构基础，完成以下升级：

1. 团队固定为 9 人；
2. 删除运行时“接收文件、分析文档、自动切片并自动建库”的 Agent 主线；
3. 保留知识库持续维护工具、结构化导入、版本审核、重建索引和回滚；
4. 合并两份专业 AI 生成的 RAG 工程知识库为 Domain Pack v2；
5. 新增 RAG Router Agent；
6. 新增 Hybrid、Metadata、Graph-Assisted、Parent-Child 和受限 Agentic Retrieval；
7. 新增讲义、实操、题目三路平行生成；
8. 新增事实、难度、题目、安全四路平行审核；
9. 最终决策仍由唯一 Arbitration Agent 和确定性状态机控制；
10. 所有检索、平行分支、审核、修订和仲裁均可通过 Event/Trace 回放。

## 运行时主闭环

```text
学习者画像/问题
→ Diagnosis / Path Context
→ RAG Router Agent
→ 一种或多种检索策略
→ Evidence Fusion + Sufficiency
→ 证据不足时有限 Agentic 补检索
→ 平行生成：讲义 / 实操 / 题目
→ Resource Coordinator
→ 平行审核：事实 / 难度 / 题目 / 安全
→ Review Coordinator
→ 唯一 Arbitration Agent
→ 发布、测评、画像更新和下一轮路径
```

## 目录入口

- 总索引：`docs/00_总索引.md`
- 项目范围：`docs/01_项目重点与范围.md`
- 九人分工：`docs/02_团队总分工.md`
- Agent 蓝图：`docs/07_七核心智能体与平行Agent职责.md`
- 自适应 RAG：`docs/35_自适应多策略RAG与路由Agent.md`
- 平行 Agent：`docs/36_平行Agent生产与审核架构.md`
- API：`api/openapi.yaml`、`api/internal_openapi.yaml`
- 数据库：`database/schema.sql`
- 知识库：`knowledge-bases/enterprise-rag-engineering-v2/`
- 成员入口：`members/Px_姓名/00_开始这里.md`
- 阶段任务：`tasks/S0` 至 `tasks/S7`

## 事实来源优先级

1. 当前批准的阶段任务卡；
2. `api/` 与 `contracts/jsonschema/`；
3. `database/schema.sql`；
4. Agent Blueprint、系统架构和 ADR；
5. 专项设计文档；
6. Mock、示例和原型；
7. 群聊或口头说明。

发生冲突时，不得自行猜测，任务应标记为 `BLOCKED` 并提交变更申请。


## 本地校验

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
make validate
```

完整知识库校验：

```bash
make validate-kb
```

重新生成九名成员开发包：

```bash
make build-member-packs
```

## 交付与验证

- 根项目验证：`reports/final_validation_report.md`；
- 已知限制：`reports/known_limitations.md`；
- API 清单：`reports/api_inventory.csv`；
- 成员独立包：`member-packs-v7.0/`；
- 可视化原型：`prototypes/adaptive-parallel-rag-observability.html`。

本仓库是可直接施工的统一基线，并包含可运行知识服务；学员端、管理端、业务后端和真实 Agent 仍需团队按照阶段任务完成，不能把契约和 Mock 冒充成最终生产系统。
