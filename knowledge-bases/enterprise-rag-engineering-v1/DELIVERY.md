# 知识库子系统交付说明

## 1. 交付定位

本包交付一个可直接接入项目的预建专业 Domain Pack，而不是临时让大模型凭空生成知识库。运行时流程为：学习者画像/前测 -> Agent 诊断 -> 从已发布知识库检索证据 -> 生成个性化资源 -> 审核/测评/决策。

## 2. 领域

- 名称：企业级 RAG 系统工程与可信知识应用实训知识库
- 垂直领域：特定软件开发 / 人工智能工程
- 目标：能够设计、实现、评测并部署一个可追溯、可审核、可迭代的企业级RAG系统。
- 版本：1.0.0

## 3. 内容规模

| 内容 | 数量 |
|---|---:|
| 模块 | 8 |
| 知识节点 | 32 |
| 核心知识节点 | 26 |
| 专业切片 | 128 |
| 来源登记 | 14 |
| FAQ | 96 |
| 误区/错误案例 | 64 |
| 题目 | 128 |
| 工程任务 | 32 |
| 检索评测案例 | 96 |
| 生成评测案例 | 32 |
| 差异化学习者完整案例 | 3 |

## 4. 可直接使用的入口

- 机器数据：`data/`
- 专业讲义：`data/documents/`
- 知识服务：`server/app.py`
- OpenAPI：`contracts/knowledge-api.yaml`
- 数据库迁移：`db/migrations/001_domain_pack_extension.sql`
- 现有仓库兼容说明：`integration/README.md`
- 比赛提交材料：`submission/`
- 可视化浏览器：`prototypes/knowledge-base-browser.html`
- 质量报告：`reports/knowledge_quality_report.md`
- 后续扩展模板：`templates/`
- 新增内容流程：`docs/12_知识库新增内容施工流程.md`

## 5. 运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/validate_pack.py
python scripts/validate_project_compatibility.py
python scripts/run_retrieval_eval.py
pytest -q
uvicorn server.app:app --host 127.0.0.1 --port 8090
```

Windows PowerShell 激活命令为 `.venv\Scripts\Activate.ps1`。

## 6. 尚需在主项目中冻结的事项

- 生产 embedding 模型、维度和版本；
- 是否接入 reranker；
- 真实生成模型及 Prompt 版本；
- 人工专家标注后的幻觉率和难度适配率；
- 正式发布状态从 `candidate_validated` 切换到 `published` 的审批记录。
