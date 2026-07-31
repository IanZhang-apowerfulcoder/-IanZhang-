# 赛前人工复核清单

## 必须抽查
- 每章至少抽查2个核心知识节点及其4个检索片段。
- 每章至少抽查3道题的答案、解释和证据。
- 检查15个实操任务的步骤是否可执行、验收是否明确。
- 检查20个拒答案例是否符合项目风险边界。
- 检查全部来源标题、链接、许可说明和技术释义是否匹配。

## 签字后可修改manifest
仅在指导教师或具备RAG工程经验的负责人完成复核后，才可将：
- `content_readiness` 改为 `competition_ready`；
- `expert_review_status` 改为 `approved_for_training`；
- 填写 `reviewed_by` 与 `reviewed_at`；
随后必须重新计算manifest中的文件哈希并重新运行校验。
