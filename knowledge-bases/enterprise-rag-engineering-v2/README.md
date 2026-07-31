# Enterprise RAG Engineering Domain Pack v2.0.0

这是挑战杯项目的预建垂直领域知识库，领域为**企业级 RAG 系统工程与可信知识应用实训**。它是运行时可信知识资产，不依赖用户临时上传资料后再自动建库。

## 当前规模

| 资产 | 数量 |
|---|---:|
| 模块 | 8 |
| 知识节点 | 93 |
| 知识关系 | 252 |
| 可追溯切片 / Evidence | 372 / 372 |
| 概念卡 / FAQ / 误区 | 93 / 279 / 186 |
| 分阶题目 | 372 |
| 工程任务 / Rubric | 93 / 93 |
| 检索 / 生成评测案例 | 279 / 173 |

## 内容治理

- `trusted_core`：原 32 个商业级核心知识节点；
- `trusted_ai_generated`：第二份专业 AI 知识包扩展出的 61 个细粒度节点；
- 两层内容均可用于开发与运行时检索；
- 第二层保留 `pending_team_review`，表示团队仍需逐条复核，不能虚称专家审核完成；
- 所有专业结论必须绑定 `evidence_id`；
- 发布版本不可原地修改，新增内容通过导入、复核、回归、发布形成新版本。

## 自适应检索

知识服务支持：

1. Metadata-Filtered Retrieval；
2. Hybrid Retrieval；
3. Graph-Assisted Retrieval；
4. Parent-Child Retrieval；
5. 受限 Agentic Decomposition Retrieval。

RAG Router Agent 只负责生成结构化检索计划；`server/adaptive_retriever.py` 负责执行、融合和证据充分性判断。

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make validate
make compatibility
make eval
make test
make dry-import
make serve
```

Windows PowerShell：`.venv\Scripts\Activate.ps1`。

服务默认地址：`http://127.0.0.1:8090`，OpenAPI：`contracts/knowledge-api.yaml`。

## 真实性边界

本包已真实运行结构校验、固定检索评测、接口测试和数据库 dry-run。尚未接入最终生产 embedding、reranker 和生成模型，因此不虚构“幻觉率 <5%”或“难度适配率 >=85%”；这些指标必须在主系统冻结模型、Prompt、人工标注口径后实测。
