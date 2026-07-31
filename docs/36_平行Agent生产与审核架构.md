# 平行 Agent 生产与审核架构

## 平行生成

Explanation、Practice、Quiz 三个 Agent 使用同一 Evidence Bundle，但目标、模板和输出 Schema 不同。Resource Coordinator 负责一致性、引用映射、顺序和完整性；某分支失败只重跑该分支。

## 平行审核

Factuality、Difficulty、Assessment Quality、Safety 四个 Reviewer 独立运行。Review Coordinator 根据硬规则聚合：任何事实无证据、答案错误、越权或高风险问题可直接 REJECT/HUMAN_REVIEW；一般难度或排版问题返回 REVISE。

## 唯一仲裁

平行 Agent 只提出候选或审查结论。最终动作由 Arbitration Agent 在确定性状态机和业务规则约束下选择，后端验证后写入数据库。

## 质量对照

必须比较单路生成/单审核与平行生成/多维审核的覆盖率、事实错误、适配准确率、冗余、成本和延迟，证明复杂度带来真实收益。
