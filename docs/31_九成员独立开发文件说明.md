# 九名成员独立开发文件说明

本版本为 **V6.1 成员说明增强版**。它没有修改 V6 的 66 个公开接口、六智能体接口、字段名、JSON Schema 或 Mock，只是把每名成员必须遵守的内容分别写成一份可独立阅读的完整开发文件。

## 使用方法

1. 全体项目仍以 `api/openapi.yaml`、`api/internal_agent_interfaces.yaml`、`contracts/jsonschema/` 为正式契约。
2. 每名成员先阅读 `members/自己的目录/00_完整开发文件.md`。
3. 个人文件中已经逐个列出相关 API 的方法、路径、请求字段、响应字段、负责人和 Mock。
4. 个人包位于 `member-packs-v6.1/`，可以分别发给成员学习和开发。
5. 个人文件是从正式契约自动生成的快照；若发生冲突，正式契约优先，并应同步更新个人文件。

## 成员文件索引

| 成员 | 角色 | 完整开发文件 | 个人包 |
|---|---|---|---|
| 张英赫 | 项目负责人、总架构、编排与仲裁 | `member-development-files/P1_张英赫_完整开发文件.md` | `member-packs-v6.1/P1_张英赫_独立开发包.zip` |
| 李佳乐 | 智能体基础设施、自动知识工程、检索与审核纠偏 | `member-development-files/P2_李佳乐_完整开发文件.md` | `member-packs-v6.1/P2_李佳乐_独立开发包.zip` |
| 杨欣怡 | 诊断、学习路径、画像与学习业务契约 | `member-development-files/P3_杨欣怡_完整开发文件.md` | `member-packs-v6.1/P3_杨欣怡_独立开发包.zip` |
| 陈尧 | 前端架构、联合决策可视化与评测分析 | `member-development-files/P4_陈尧_完整开发文件.md` | `member-packs-v6.1/P4_陈尧_独立开发包.zip` |
| 郑翘楚 | 资源生成智能体与学习资料页面 | `member-development-files/P5_郑翘楚_完整开发文件.md` | `member-packs-v6.1/P5_郑翘楚_独立开发包.zip` |
| 李汝萱 | 测评智能体与练习页面 | `member-development-files/P6_李汝萱_完整开发文件.md` | `member-packs-v6.1/P6_李汝萱_独立开发包.zip` |
| 陈严谨 | 管理端、知识库页面与明确范围的简单接口 | `member-development-files/P7_陈严谨_完整开发文件.md` | `member-packs-v6.1/P7_陈严谨_独立开发包.zip` |
| X | 学习端页面与决策回放实现 | `member-development-files/P8_X_完整开发文件.md` | `member-packs-v6.1/P8_X_独立开发包.zip` |
| 斯汀 | 质量保障、评测数据与演示材料 | `member-development-files/P9_斯汀_完整开发文件.md` | `member-packs-v6.1/P9_斯汀_独立开发包.zip` |

## 强制规则

- 模块内部变量可以自行命名，跨模块字段必须使用冻结名称。
- 不得自行修改 API 路径、operation_id、Schema、枚举和 Mock 字段。
- 字段不够时，先提交接口变更申请。
- 前端不得直接消费智能体原始输出。
- 未审核内容使用草稿编号，审核通过后才生成正式资源或测评编号。
- 每个 PR 必须列出使用的 operation_id、Schema 和 Mock。
