# 知识库子系统 v2.0 交付说明

## 1. 交付目标

交付一个可以直接被 Diagnosis、RAG Router、Generation、Review、Assessment 和 Arbitration 模块使用的预建 Domain Pack，并支持团队持续维护和版本发布。

## 2. 运行主线

```text
学习者画像 / 训练任务
→ RAG Router 生成 Retrieval Plan
→ 多策略检索与 Evidence Fusion
→ 证据充分性判断
→ 并行生成讲义、实操和题目
→ 并行审核事实、难度、题目与安全
→ 唯一仲裁
```

## 3. 资产规模

- 93 个知识节点、252 条关系；
- 372 个切片和 372 个 evidence；
- 372 道题、93 个任务、93 套 Rubric；
- 279 个检索案例、173 个生成案例；
- 三组差异化学习者完整兼容样例。

## 4. 程序入口

- 数据：`data/`
- FastAPI：`server/app.py`
- 路由策略：`server/router.py`
- 自适应检索：`server/adaptive_retriever.py`
- OpenAPI：`contracts/knowledge-api.yaml`
- 数据库迁移：`db/migrations/`
- 比赛提交材料：`submission/`
- 验证报告：`reports/final_validation_report_v2.md`

## 5. 完成定义

知识库内容只有在以下条件全部通过后才可进入新发布版本：来源登记、节点映射、切片证据、题目和任务、Schema、固定检索回归、团队复核、版本审批和可回滚记录。
