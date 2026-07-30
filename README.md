# 挑战杯项目：所有成员只看这一份说明

这份文件是整个仓库的统一入口。

**你不需要把仓库里所有文件都读完。** 每个人只需要先看自己的个人目录，再根据任务卡查看对应接口、字段和模拟数据。

---

## 一、先理解这个仓库是做什么的

这是一个面向企业培训的多智能体个性化学习平台。

系统大致流程是：

```text
企业上传资料
→ 系统构建知识库
→ 学习者开始学习
→ 多个智能体共同诊断、规划、生成资料、出题、审核和仲裁
→ 前端展示学习资料、测评、画像和决策过程
→ 根据学习结果更新下一步学习路径
```

项目的重点不是普通页面，而是：

```text
多智能体如何传递数据
多智能体如何产生不同意见
如何审核和纠偏
如何根据证据进行最终决策
如何形成学习反馈闭环
```

---

## 二、你只需要按这个顺序看文件

每个人统一按以下顺序阅读：

```text
1. README.md（就是当前文件）
2. members/自己的目录/00_完整开发文件.md
3. members/自己的目录/openapi_scope.yaml
4. members/自己的目录/internal_scope.yaml
5. members/自己的目录/mock_index.yaml
6. 根据任务卡查看对应的 Schema 和 Mock
```

不要一开始就看全部 66 个接口，也不要把整个 `docs/` 目录全部读完。

---

## 三、每个人具体看哪个目录

| 成员 | 主要职责 | 个人入口 |
|---|---|---|
| 张英赫 | 总架构、编排器、仲裁智能体、总集成 | `members/P1_张英赫/00_完整开发文件.md` |
| 李佳乐 | 知识工程、RAG、智能体运行框架、审核智能体 | `members/P2_李佳乐/00_完整开发文件.md` |
| 杨欣怡 | 诊断智能体、路径规划、画像和学习闭环 | `members/P3_杨欣怡/00_完整开发文件.md` |
| 陈尧 | 前端架构、决策可视化、评测分析 | `members/P4_陈尧/00_完整开发文件.md` |
| 郑翘楚 | 学习资料生成智能体、学习资料页面 | `members/P5_郑翘楚/00_完整开发文件.md` |
| 李汝萱 | 测评智能体、答题和测评结果页面 | `members/P6_李汝萱/00_完整开发文件.md` |
| 陈严谨 | 管理端、知识库和培训项目的基础接口与页面 | `members/P7_陈严谨/00_完整开发文件.md` |
| X | 学习端页面、学习任务、资料、测评、画像、决策回放 | `members/P8_X/00_完整开发文件.md` |
| 斯汀 | 测试、评测数据、缺陷记录、回归和演示材料 | `members/P9_斯汀/00_完整开发文件.md` |

每个人只需要先进入自己的目录，不需要同时阅读别人的完整开发文件。

---

## 四、个人目录里的四个文件分别是什么意思

### 1. `00_完整开发文件.md`

这是你最重要的开发说明，里面已经写明：

- 你负责什么；
- 你不负责什么；
- 你允许修改哪些目录；
- 你必须遵守哪些接口；
- 你使用哪些字段名；
- 你需要哪些模拟数据；
- 每个阶段做什么；
- 提交前如何验收。

开始任务前必须先看这个文件。

### 2. `openapi_scope.yaml`

这是你涉及的前后端接口清单。

里面会告诉你：

```text
接口地址
使用 GET 还是 POST
请求要传哪些字段
返回哪些字段
哪些字段必填
字段是什么类型
对应的模拟数据在哪里
```

普通成员只看自己目录里的接口切片，不需要先读完整的 `api/openapi.yaml`。

### 3. `internal_scope.yaml`

这是你涉及的智能体或内部服务连接规则。

里面会告诉你：

```text
你的模块接收什么数据
你的模块输出什么数据
对应哪个 JSON Schema
允许重试几次
超时时间是多少
由谁审核
```

### 4. `mock_index.yaml`

这是你需要使用的模拟数据索引。

模拟数据的作用是：即使其他成员的后端或智能体还没有写完，你也能先开发自己的页面或模块。

---

## 五、仓库中最重要的文件是什么

发生冲突时，以下文件按顺序决定谁是正确的：

```text
1. api/openapi.yaml
2. api/internal_agent_interfaces.yaml
3. contracts/jsonschema/
4. api/field_dictionary.yaml
5. api/error_codes.yaml
6. database/schema.sql
7. mocks/
8. 个人开发说明
```

含义如下：

### `api/openapi.yaml`

前端和后端之间的正式接口总表。

接口路径、请求方式、请求字段、返回字段有争议时，以它为准。

### `api/internal_agent_interfaces.yaml`

六个智能体和内部服务之间的正式连接规则。

### `contracts/jsonschema/`

规定一份数据必须有哪些字段、字段类型是什么。

智能体或后端输出的数据必须通过对应 Schema 校验。

### `api/field_dictionary.yaml`

字段词典，解释所有跨模块变量的含义。

### `api/error_codes.yaml`

统一错误码和错误返回格式。

### `database/schema.sql`

数据库表结构基线。

### `mocks/`

已经准备好的模拟请求、模拟响应和错误情况。

---

## 六、什么变量可以自己改，什么变量绝对不能改

### 模块内部变量

每个人自己模块内部的临时变量可以自行命名，例如：

```text
result
draft
data
current_item
```

### 跨模块传输变量

数据只要要传给其他成员的模块、后端、前端或智能体，就必须使用已经冻结的名称。

常见冻结字段包括：

```text
organization_id
knowledge_base_id
knowledge_base_version_id
document_id
build_run_id
training_program_id
assignment_id
learner_id
session_id
decision_cycle_id
agent_run_id
proposal_id
review_id
decision_id
resource_draft_id
resource_id
assessment_draft_id
assessment_id
attempt_id
profile_snapshot_id
evidence_id
correlation_id
idempotency_key
action_type
reference_id
```

禁止自行把它们改成另一套名字。

例如正式字段是：

```text
session_id
```

不能在跨模块数据中改成：

```text
sessionId
session
study_session
```

模块内部可以使用其他名称，但在接口入口和出口必须转换回正式字段。

---

## 七、接口、Schema 和 Mock 应该怎么配合使用

开始一个任务时，按下面顺序做：

```text
先在个人 openapi_scope.yaml 找到接口
→ 查看请求字段和响应字段
→ 查看对应 JSON Schema
→ 查看 mock_index.yaml
→ 打开对应 Mock
→ 先按 Mock 完成页面或模块
→ 后端完成后再替换真实接口
```

例如开发学习资料页面：

```text
先找到 list_session_resources 或 get_learning_resource
→ 看返回字段
→ 打开对应 response.json
→ 按这个结构开发页面
→ 不要自己发明字段
```

---

## 八、每个成员每天的开发流程

所有成员统一执行：

```text
1. 打开 GitHub Desktop
2. 切换到 develop
3. Pull 最新代码
4. 根据任务卡确认本次任务
5. 从 develop 创建自己的功能分支
6. 打开个人完整开发文件
7. 确认本次使用的接口、Schema 和 Mock
8. 编写代码
9. 本地测试
10. 检查是否修改了冻结字段
11. Commit
12. Push
13. 创建 PR，目标分支选择 develop
14. 等待审核
15. 按审核意见修改
16. 审核通过后合并
```

禁止直接在 `main` 或 `develop` 上开发业务功能。

---

## 九、分支怎么命名

建议格式：

```text
feature/姓名-模块名称
fix/姓名-问题名称
test/姓名-测试名称
```

例如：

```text
feature/zhengqiaochu-resource-page
feature/liruxuan-assessment-agent
feature/chenyanjin-admin-console
fix/x-learning-session-error
```

---

## 十、接口不够用时怎么办

不能直接改接口，也不能先改代码再通知别人。

必须执行：

```text
1. 填写 templates/API_CHANGE_REQUEST.md
2. 写清楚为什么要改
3. 写清楚影响哪些模块和成员
4. 由接口负责人审核
5. 先修改 OpenAPI、Schema 和 Mock
6. 再修改前后端和智能体代码
```

没有审批，不允许修改跨模块字段。

---

## 十一、使用 AI 写代码时必须告诉 AI 什么

把任务交给 AI 编码工具时，至少提供：

```text
你的任务是什么
允许修改哪些文件
禁止修改哪些文件
使用哪个接口
请求字段是什么
响应字段是什么
对应的 Schema 在哪里
对应的 Mock 在哪里
需要处理哪些状态
验收标准是什么
```

不能只说：

```text
帮我完成这个模块
```

否则 AI 很可能重新设计字段、重复创建接口或修改不属于你的代码。

---

## 十二、页面必须处理哪些状态

所有前端页面至少处理：

```text
加载中
正常数据
空数据
接口错误
权限不足
任务处理中
任务失败
```

涉及智能体或异步任务时，还要处理：

```text
等待运行
正在运行
审核中
被驳回
重新生成
人工审核
执行完成
```

---

## 十三、提交代码前必须检查

每个人提交前确认：

- 没有直接修改 `main` 或 `develop`；
- 没有修改不属于自己的公共接口；
- 没有擅自改跨模块字段名；
- 请求和响应符合 OpenAPI；
- 智能体输出符合 Schema；
- 页面按照 Mock 结构开发；
- 已处理加载、空数据和错误状态；
- 没有提交密钥、密码和 `.env`；
- 已完成本地测试；
- PR 目标分支是 `develop`。

---

## 十四、遇到问题找谁

| 问题类型 | 联系人 |
|---|---|
| 整体架构、编排、仲裁、接口冲突 | 张英赫 |
| 知识库、RAG、证据、审核智能体 | 李佳乐 |
| 诊断、路径、画像、学习业务逻辑 | 杨欣怡 |
| 前端结构、可视化、展示字段 | 陈尧 |
| 资源模块实现问题 | 郑翘楚，并由杨欣怡审核 |
| 测评模块实现问题 | 李汝萱，并由杨欣怡审核 |
| 管理端和简单接口问题 | 陈严谨，核心问题找李佳乐或杨欣怡 |
| 学习端页面问题 | X，页面规范找陈尧 |
| 测试、缺陷、验收问题 | 斯汀，最终验收找张英赫 |

---

## 十五、最简单的执行要求

每个成员只需要记住下面六句话：

```text
只看自己的个人目录。
先看接口，再写代码。
先用 Mock，不等其他成员。
跨模块字段不能改名。
接口不够先申请，不能私自修改。
代码通过 PR 合并到 develop。
```
