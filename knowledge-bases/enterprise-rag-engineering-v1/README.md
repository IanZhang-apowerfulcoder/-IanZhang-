# Enterprise RAG Engineering Domain Pack v1.0.0

面向挑战杯“领域知识个性化生成与多智能体协同决策系统研究”的预建专业知识库子系统。

## 立即使用

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make validate
make compatibility
make eval
make test
make serve
```

Windows PowerShell 使用 `.venv\Scripts\Activate.ps1`。

## 目录

- `data/`：知识节点、切片、题库、任务、Rubric、评测集和学习者样例；
- `data/documents/`：8份原创模块讲义；
- `contracts/`：OpenAPI、JSON Schema与现有仓库兼容契约；
- `server/`：可运行的FastAPI知识服务和BM25/字符n-gram检索基线；
- `scripts/`：校验、评测、向量生成和PostgreSQL导入；
- `db/`：现有数据库扩展迁移；
- `submission/`：比赛可提交的知识库切片和三组端到端样例；
- `integration/`：接入现有GitHub仓库的映射和主线修订；
- `reports/`：实际运行生成的质量报告；
- `prototypes/knowledge-base-browser.html`：无需服务器即可打开的知识库浏览器；
- `DELIVERY.md`：完整交付说明和接入入口；
- `examples/`：curl、Python 与 TypeScript 接入示例；
- `templates/`：后续新增来源、节点、切片、题目、任务和版本发布模板。

## 重要声明

本包已经提供完整专业内容与可运行词法检索。稠密向量、重排器和真实生成模型指标必须在项目选定具体模型后实际生成和测量；包内明确保留适配器与评测集，不伪造结果。
