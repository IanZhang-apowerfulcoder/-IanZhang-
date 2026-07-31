# 企业级 RAG 专业知识库接入与验收

## 一、接入对象

本仓库已加入：

```text
knowledge-bases/enterprise-rag-engineering-v1/
```

它是比赛主闭环默认使用的、预先建设并验证的垂直领域专业知识库。自动知识工程只负责后续生成候选版本，不替代本版本，也不在学习者每次使用时重新构建知识库。

## 二、权威标识

- Domain Pack：`enterprise-rag-engineering-v1`
- 版本：`1.0.0`
- Knowledge Base ID：见 `knowledge-bases/enterprise-rag-engineering-v1/data/domain.json`
- Knowledge Base Version ID：见同文件；学习会话和检索请求必须使用该值或后续正式发布版本。

## 三、后端接入

1. 应用 `database/migrations/002_enterprise_rag_domain_pack.sql`；
2. 运行包内 `scripts/import_to_postgres.py --dry-run`；
3. 创建/映射 `knowledge_bases`、`build_runs`、`knowledge_base_versions` 基础记录；
4. 导入节点、关系、切片、题库、任务和评测集；
5. 后端在训练项目和学习会话中固定 `knowledge_base_version_id`；
6. Retrieval 模块按照现有 V6 `retrieval_request.schema.json` 与 `retrieval_response.schema.json` 返回证据；
7. 生成、测评、审核和仲裁智能体只能引用 evidence_id，不直接读取本地文件路径。

## 四、接口标准

- 现有业务接口仍以 `api/openapi.yaml` 为准；
- 现有六智能体接口仍以 `api/internal_agent_interfaces.yaml` 和 `contracts/jsonschema/` 为准；
- 知识包独立服务参考接口见 `api/knowledge_domain_api.yaml`；
- 若知识包接口与现有冻结契约冲突，优先保持 V6 既有字段，通过适配器转换，不得由成员自行改名。

## 五、验收命令

```bash
cd knowledge-bases/enterprise-rag-engineering-v1
python scripts/validate_pack.py
python scripts/run_retrieval_eval.py
pytest -q
```

必须同时满足：

- Schema 与引用校验通过；
- 32 个知识节点、128 个专业切片数量正确；
- 核心节点内容覆盖率 100%；
- 本地固定检索集 Hit@5 不低于 90%；
- 三组学习者案例通过现有 Agent 输出 Schema；
- 不存在伪造的向量和模型质量指标。

## 六、真实模型接入后的新增验收

以下指标必须由真实生成模型和固定评测集实际测量：

- 专业知识谬误率低于 5%；
- 画像—资源难度适配准确率不低于 85%；
- 核心知识点覆盖率不低于 90%；
- 引用正确率、拒答正确率和越权泄露率达到项目门禁。

在真实测量前，任何成员不得在材料中声称这些指标已经达成。
