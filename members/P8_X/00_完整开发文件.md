# X完整开发文件

> 成员编号：P8  
> 角色：学习端页面与决策回放实现  
> 能力层级：成长型成员  
> 契约基线：`frozen_v6`  
> 本文件版本：`V6.1`（只增强成员说明，不改变 V6 API、字段和 Schema）

## 1. 先理解：你到底根据什么开发

本文件把与你有关的接口、字段、Mock、开发阶段和禁止事项集中到一处，便于执行。但发生冲突时，按以下优先级判断：

1. `api/openapi.yaml`：前端与后端 HTTP 接口的唯一事实来源。
2. `api/internal_agent_interfaces.yaml`：六智能体函数、超时、重试和 Schema 路径的唯一事实来源。
3. `contracts/jsonschema/`：智能体与内部服务跨模块 JSON 字段的唯一事实来源。
4. `api/field_dictionary.yaml`：核心标识符含义与负责人。
5. `api/error_codes.yaml`：统一错误码。
6. `database/schema.sql`：数据库持久化结构。
7. `mocks/`：开发和联调样例；Mock 不能覆盖正式契约。
8. 本文件：上述正式契约的成员化说明和执行教程。

**模块内部变量可以自定义；只要数据离开本模块，就必须转换为本文件和正式契约规定的字段。**

## 2. 你的职责与管理关系

- 直接指导人：陈尧
- 代码审核人：陈尧、张英赫、杨欣怡
- 你负责的角色：学习端页面与决策回放实现
- 契约状态：`frozen_v6`

### 允许修改的代码范围

- `apps/web/src/features/learner/**`
- `apps/web/src/features/decision-trace/**`
- `tests/learner/**`

### 明确禁止

- 直接读取智能体原始输出
- 自行修改接口返回结构
- 修改后端业务规则
- 不得删除、重命名或改变冻结字段类型。
- 不得把大模型原始文本直接穿透给前端。
- 不得自行增加第二套接口、第二套 Mock 或第二套公共类型。
- 字段不够用时必须提交 `templates/API_CHANGE_REQUEST.md`，不能先改代码。

## 3. 开发前阅读顺序

1. `README.md`
2. `CONTRIBUTING.md`
3. `docs/01_项目重点与范围.md`
4. `docs/06_系统模块边界.md`
5. `docs/10_命名与字段契约.md`
6. `docs/11_接口所有权与变更流程.md`
7. `docs/14_测试与验收标准.md`
8. `docs/15_AI辅助开发约束.md`
9. `docs/16_任务卡与PR规则.md`
10. `docs/21_端到端用户流程与接口审计.md`
11. `docs/22_跨模块数据传输契约矩阵.md`
12. `docs/23_标识符与关联键生命周期.md`
13. `docs/25_异步任务轮询与状态规则.md`
14. `docs/26_字段冻结清单.md`
15. `docs/28_九成员开发文件总教程.md`
16. `docs/12_前端页面接口依赖.md`
17. `docs/18_演示与评测指标.md`
18. `api/openapi.yaml`
19. `project/boundary_contract_manifest.yaml`

然后阅读本目录中的：

1. `openapi_scope.yaml`
2. `internal_scope.yaml`
3. `mock_index.yaml`
4. 本文件后面的逐接口说明

## 4. 你的接口和内部接口总览

### 公开 HTTP 接口

- `cancel_learning_session`：取消学习会话
- `create_session_feedback`：提交学习反馈
- `get_assessment_attempt_result`：获取测评评分结果
- `get_assignment`：获取培训分配
- `get_current_action`：获取学习者当前动作
- `get_current_assessment`：获取当前测评
- `get_current_user`：获取当前用户
- `get_decision_cycle`：获取决策轮次
- `get_decision_trace`：获取完整联合决策轨迹
- `get_evidence`：获取证据详情
- `get_latest_decision`：获取最新最终决策
- `get_learner_profile`：获取最新学习画像
- `get_learning_path`：获取当前学习路径
- `get_learning_resource`：获取学习资源
- `get_learning_session`：获取学习会话
- `get_organization`：获取组织信息
- `list_decision_cycles`：查询决策轮次
- `list_learner_assignments`：查询学习者培训任务
- `list_learning_sessions`：查询学习会话
- `list_profile_history`：查询画像历史
- `list_session_events`：增量查询会话事件
- `list_session_resources`：查询会话学习资源
- `login`：用户登录
- `logout`：退出登录
- `record_behavior_events`：批量记录学习行为
- `refresh_token`：刷新访问令牌
- `start_learning_session`：启动学习会话
- `submit_assessment_attempt`：提交测评答案
- `update_resource_progress`：更新资源学习进度

### 智能体内部接口

- 无智能体内部接口

## 5. 你必须使用的核心跨模块变量名

下面只列出与你当前接口和智能体范围有关、且已经进入核心字段词典的冻结字段。字段拼写、类型和语义均不得自行修改。

| 字段 | 类型 | 含义 | 负责人 |
|---|---|---|---|
| `organization_id` | `uuid` | 组织租户标识 | 张英赫 |
| `knowledge_base_version_id` | `uuid` | 不可变知识库版本标识 | 李佳乐 |
| `document_id` | `uuid` | 上传文档标识 | 李佳乐 |
| `learner_id` | `uuid` | 学习者标识 | 杨欣怡 |
| `training_program_id` | `uuid` | 培训项目标识 | 杨欣怡 |
| `assignment_id` | `uuid` | 培训分配标识 | 杨欣怡 |
| `session_id` | `uuid` | 一次完整学习会话标识 | 张英赫 |
| `decision_cycle_id` | `uuid` | 会话内一轮联合决策标识 | 张英赫 |
| `agent_run_id` | `uuid` | 一次智能体运行标识 | 张英赫 |
| `proposal_id` | `uuid` | 智能体候选提案标识 | 张英赫 |
| `review_id` | `uuid` | 审核记录标识 | 李佳乐 |
| `decision_id` | `uuid` | 最终仲裁决策标识 | 张英赫 |
| `resource_id` | `uuid` | 审核发布后的学习资源标识 | 杨欣怡 |
| `assessment_id` | `uuid` | 审核发布后的测评标识 | 杨欣怡 |
| `attempt_id` | `uuid` | 一次作答记录标识 | 杨欣怡 |
| `profile_snapshot_id` | `uuid` | 不可变学习画像快照标识 | 杨欣怡 |
| `evidence_id` | `uuid` | 可追溯证据标识 | 李佳乐 |
| `idempotency_key` | `string` | 避免重复创建或重复提交的幂等键 | 张英赫 |

此外，所有公开接口统一遵守：

- JSON 字段：`snake_case`
- API 路径：小写英文加短横线
- TypeScript 类型：`PascalCase`
- 数据库字段：`snake_case`
- 枚举值：`lower_snake_case`
- 时间：ISO 8601 UTC 字符串
- 标识符：UUID 字符串
- 所有创建、提交类请求优先携带 `idempotency_key`
- 同一联合决策链路使用同一个 `correlation_id`

## 6. 逐个公开 API 开发说明

### `cancel_learning_session` — 取消学习会话

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/cancel`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`无请求体`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `idempotency_key` | 是 | `string` |  | 避免重复创建或重复提交的幂等键 | 张英赫 |

**成功响应结构：`ApiResponseLearningSession`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `LearningSessionView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |
| `training_program_id` | 是 | `string(uuid)` |  | 培训项目标识 | 杨欣怡 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `knowledge_base_version_id` | 是 | `string(uuid)` |  | 不可变知识库版本标识 | 李佳乐 |
| `profile_snapshot_id` | 是 | `string(uuid)` |  | 不可变学习画像快照标识 | 杨欣怡 |
| `session_status` | 是 | `string` | created, running, waiting_for_learner, human_review_required, completed, failed, cancelled |  |  |
| `current_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |
| `current_action_type` | 否 | `string \| null` |  |  |  |
| `started_at` | 是 | `string(date-time)` |  |  |  |
| `completed_at` | 否 | `string \| null(date-time)` |  |  |  |
| `updated_at` | 是 | `string(date-time)` |  |  |  |
| `error_code` | 否 | `string \| null` |  |  |  |
| `error_message` | 否 | `string \| null` |  |  |  |

**必须使用的 Mock**

- `mocks/http/cancel_learning_session/request.json`
- `mocks/http/cancel_learning_session/response.json`
- `mocks/http/cancel_learning_session/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `create_session_feedback` — 提交学习反馈

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/feedback`
- 契约负责人：杨欣怡
- 实现负责人：杨欣怡
- 展示负责人：无
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`FeedbackRequest`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `feedback_type` | 是 | `string` | resource_helpful, resource_not_helpful, question_ambiguous, decision_disagree, other |  |  |
| `reference_id` | 否 | `string \| null` |  |  |  |
| `rating_value` | 否 | `integer \| null` |  |  |  |
| `comment_text` | 否 | `string \| null` |  |  |  |
| `idempotency_key` | 是 | `string` |  | 避免重复创建或重复提交的幂等键 | 张英赫 |

**成功响应结构：`无 JSON 响应体`**

统一响应外壳：

无

响应 `data` 中的主要跨模块字段：

无

**必须使用的 Mock**

- `mocks/http/create_session_feedback/request.json`
- `mocks/http/create_session_feedback/response.json`
- `mocks/http/create_session_feedback/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_assessment_attempt_result` — 获取测评评分结果

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/assessment-attempts/{attempt_id}`
- 契约负责人：杨欣怡
- 实现负责人：李汝萱
- 展示负责人：陈尧
- 使用成员：X、斯汀、李汝萱
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:attempt_id` | 是 | `string(uuid)` |  | 一次作答记录标识 | 杨欣怡 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseAssessmentResult`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `AssessmentResultView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `attempt_id` | 是 | `string(uuid)` |  | 一次作答记录标识 | 杨欣怡 |
| `assessment_id` | 是 | `string(uuid)` |  | 审核发布后的测评标识 | 杨欣怡 |
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `attempt_status` | 是 | `string` | submitted, scoring, scored, scoring_failed |  |  |
| `total_awarded_score` | 是 | `number` |  |  |  |
| `total_score_points` | 是 | `number` |  |  |  |
| `score_ratio` | 是 | `number` |  |  |  |
| `question_results` | 是 | `array<QuestionResultView>` |  |  |  |
| `question_results[].question_id` | 是 | `string(uuid)` |  |  |  |
| `question_results[].is_correct` | 是 | `boolean` |  |  |  |
| `question_results[].awarded_score_points` | 是 | `number` |  |  |  |
| `question_results[].max_score_points` | 是 | `number` |  |  |  |
| `question_results[].error_type_codes` | 是 | `array<string>` |  |  |  |
| `question_results[].feedback_markdown` | 是 | `string` |  |  |  |
| `question_results[].knowledge_node_mastery_delta` | 是 | `object` |  |  |  |
| `scored_at` | 否 | `string \| null(date-time)` |  |  |  |
| `next_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_assessment_attempt_result/request.json`
- `mocks/http/get_assessment_attempt_result/response.json`
- `mocks/http/get_assessment_attempt_result/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_assignment` — 获取培训分配

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/assignments/{assignment_id}`
- 契约负责人：杨欣怡
- 实现负责人：陈严谨
- 展示负责人：无
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseLearnerAssignment`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `LearnerAssignmentView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `training_program_id` | 是 | `string(uuid)` |  | 培训项目标识 | 杨欣怡 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `assignment_status` | 是 | `string` | assigned, in_progress, completed, cancelled, expired |  |  |
| `due_at` | 否 | `string \| null(date-time)` |  |  |  |
| `assigned_by_user_id` | 是 | `string(uuid)` |  |  |  |
| `assigned_at` | 是 | `string(date-time)` |  |  |  |
| `started_at` | 否 | `string \| null(date-time)` |  |  |  |
| `completed_at` | 否 | `string \| null(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_assignment/request.json`
- `mocks/http/get_assignment/response.json`
- `mocks/http/get_assignment/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_current_action` — 获取学习者当前动作

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/current-action`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseCurrentAction`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `CurrentActionView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `action_type` | 是 | `string` | wait_for_processing, study_resource, complete_assessment, human_review_pending, session_completed, session_failed |  |  |
| `reference_id` | 否 | `string \| null(uuid)` |  |  |  |
| `action_status` | 是 | `string` | pending, available, in_progress, completed, blocked, failed |  |  |
| `display_message` | 是 | `string` |  |  |  |
| `poll_after_seconds` | 否 | `integer \| null` |  |  |  |
| `updated_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_current_action/request.json`
- `mocks/http/get_current_action/response.json`
- `mocks/http/get_current_action/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_current_assessment` — 获取当前测评

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/assessment`
- 契约负责人：杨欣怡
- 实现负责人：李汝萱
- 展示负责人：陈尧
- 使用成员：X、斯汀、李汝萱
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseAssessmentView`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `AssessmentView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `assessment_id` | 是 | `string(uuid)` |  | 审核发布后的测评标识 | 杨欣怡 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `proposal_id` | 是 | `string(uuid)` |  | 智能体候选提案标识 | 张英赫 |
| `assessment_type` | 是 | `string` | diagnostic, practice, checkpoint, final |  |  |
| `title` | 是 | `string` |  |  |  |
| `instructions` | 是 | `string` |  |  |  |
| `total_score_points` | 是 | `number` |  |  |  |
| `time_limit_seconds` | 否 | `integer \| null` |  |  |  |
| `questions` | 是 | `array<AssessmentQuestionView>` |  |  |  |
| `questions[].question_id` | 是 | `string(uuid)` |  |  |  |
| `questions[].question_order_no` | 是 | `integer` |  |  |  |
| `questions[].question_type` | 是 | `string` | single_choice, multiple_choice, true_false, short_answer, code_answer |  |  |
| `questions[].prompt_markdown` | 是 | `string` |  |  |  |
| `questions[].knowledge_node_ids` | 是 | `array<string>` |  |  |  |
| `questions[].difficulty_level` | 是 | `integer` |  |  |  |
| `questions[].score_points` | 是 | `number` |  |  |  |
| `questions[].options` | 是 | `array<AssessmentOptionView>` |  |  |  |
| `questions[].options[].option_id` | 是 | `string(uuid)` |  |  |  |
| `questions[].options[].option_label` | 是 | `string` |  |  |  |
| `questions[].options[].option_text` | 是 | `string` |  |  |  |
| `questions[].answer_constraints` | 是 | `object` |  |  |  |
| `questions[].answer_constraints.max_length` | 否 | `integer \| null` |  |  |  |
| `questions[].answer_constraints.code_language` | 否 | `string \| null` |  |  |  |
| `questions[].answer_constraints.max_selected_options` | 否 | `integer \| null` |  |  |  |
| `review_status` | 是 | `string` | pending, approved, revised, rejected |  |  |
| `assessment_status` | 是 | `string` | draft, available, closed |  |  |
| `created_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_current_assessment/request.json`
- `mocks/http/get_current_assessment/response.json`
- `mocks/http/get_current_assessment/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_current_user` — 获取当前用户

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/me`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：无
- 使用成员：X、斯汀、陈严谨
- 契约状态：`frozen_v6`

**路径与查询变量**

无

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseUser`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `UserView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `user_id` | 是 | `string(uuid)` |  | 用户标识 |  |
| `organization_id` | 是 | `string(uuid)` |  | 组织标识 | 张英赫 |
| `display_name` | 是 | `string` |  | 显示名称 |  |
| `email` | 是 | `string` |  | 邮箱 |  |
| `role_code` | 是 | `string` | platform_admin, organization_admin, trainer, reviewer, learner | 角色编码 |  |
| `learner_id` | 否 | `string \| null(uuid)` |  | 学习者标识 | 杨欣怡 |
| `account_status` | 是 | `string` | active, disabled, pending | 账号状态 |  |

**必须使用的 Mock**

- `mocks/http/get_current_user/request.json`
- `mocks/http/get_current_user/response.json`
- `mocks/http/get_current_user/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_decision_cycle` — 获取决策轮次

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/decision-cycles/{decision_cycle_id}`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `path:decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseDecisionCycle`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `DecisionCycleView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `cycle_no` | 是 | `integer` |  |  |  |
| `trigger_type` | 是 | `string` | session_started, resource_completed, assessment_submitted, manual_retry, human_review_resolved |  |  |
| `trigger_reference_id` | 否 | `string \| null` |  |  |  |
| `decision_cycle_status` | 是 | `string` | queued, collecting_context, running_agents, reviewing, arbitrating, action_ready, applied, human_review_required, failed |  |  |
| `started_at` | 是 | `string(date-time)` |  |  |  |
| `finished_at` | 否 | `string \| null(date-time)` |  |  |  |
| `failure_code` | 否 | `string \| null` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_decision_cycle/request.json`
- `mocks/http/get_decision_cycle/response.json`
- `mocks/http/get_decision_cycle/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_decision_trace` — 获取完整联合决策轨迹

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/decision-cycles/{decision_cycle_id}/trace`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `path:decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseDecisionTrace`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `DecisionTraceView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `decision_cycle` | 是 | `DecisionCycleView` |  |  |  |
| `decision_cycle.decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `decision_cycle.session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `decision_cycle.cycle_no` | 是 | `integer` |  |  |  |
| `decision_cycle.trigger_type` | 是 | `string` | session_started, resource_completed, assessment_submitted, manual_retry, human_review_resolved |  |  |
| `decision_cycle.trigger_reference_id` | 否 | `string \| null` |  |  |  |
| `decision_cycle.decision_cycle_status` | 是 | `string` | queued, collecting_context, running_agents, reviewing, arbitrating, action_ready, applied, human_review_required, failed |  |  |
| `decision_cycle.started_at` | 是 | `string(date-time)` |  |  |  |
| `decision_cycle.finished_at` | 否 | `string \| null(date-time)` |  |  |  |
| `decision_cycle.failure_code` | 否 | `string \| null` |  |  |  |
| `proposals` | 是 | `array<AgentProposalView>` |  |  |  |
| `proposals[].proposal_id` | 是 | `string(uuid)` |  | 智能体候选提案标识 | 张英赫 |
| `proposals[].agent_code` | 是 | `string` |  |  |  |
| `proposals[].agent_run_id` | 是 | `string(uuid)` |  | 一次智能体运行标识 | 张英赫 |
| `proposals[].proposal_type` | 是 | `string` | diagnosis, path_plan, resource, assessment, review, arbitration |  |  |
| `proposals[].summary_text` | 是 | `string` |  |  |  |
| `proposals[].confidence` | 是 | `number` |  |  |  |
| `proposals[].evidence_ids` | 是 | `array<string>` |  |  |  |
| `proposals[].proposal_status` | 是 | `string` | generated, accepted, rejected, revised, superseded |  |  |
| `proposals[].created_at` | 是 | `string(date-time)` |  |  |  |
| `reviews` | 是 | `array<ProposalReviewView>` |  |  |  |
| `reviews[].review_id` | 是 | `string(uuid)` |  | 审核记录标识 | 李佳乐 |
| `reviews[].reviewed_proposal_id` | 是 | `string(uuid)` |  |  |  |
| `reviews[].review_result` | 是 | `string` | approved, rejected, revision_required, human_review_required |  |  |
| `reviews[].risk_level` | 是 | `string` | low, medium, high, critical |  |  |
| `reviews[].issue_codes` | 是 | `array<string>` |  |  |  |
| `reviews[].created_at` | 是 | `string(date-time)` |  |  |  |
| `final_decision` | 是 | `oneOf(FinalDecisionView, null)` |  |  |  |
| `events` | 是 | `array<AgentEventView>` |  |  |  |
| `events[].event_id` | 是 | `string(uuid)` |  |  |  |
| `events[].organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `events[].session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `events[].decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `events[].agent_run_id` | 否 | `string \| null(uuid)` |  | 一次智能体运行标识 | 张英赫 |
| `events[].sequence_no` | 是 | `integer` |  |  |  |
| `events[].event_type` | 是 | `string` | cycle_started, context_collected, agent_started, agent_succeeded, agent_failed, proposal_created, review_completed, arbitration_completed, action_applied, human_review_requested, cycle_failed |  |  |
| `events[].agent_code` | 否 | `string \| null` |  |  |  |
| `events[].reference_id` | 否 | `string \| null` |  |  |  |
| `events[].summary_text` | 是 | `string` |  |  |  |
| `events[].occurred_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_decision_trace/request.json`
- `mocks/http/get_decision_trace/response.json`
- `mocks/http/get_decision_trace/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_evidence` — 获取证据详情

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/evidence/{evidence_id}`
- 契约负责人：李佳乐
- 实现负责人：李佳乐
- 展示负责人：陈尧
- 使用成员：X、斯汀、李汝萱、郑翘楚、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:evidence_id` | 是 | `string` |  | 可追溯证据标识 | 李佳乐 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseEvidenceDetail`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `EvidenceDetailView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `evidence_id` | 是 | `string` |  | 可追溯证据标识 | 李佳乐 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `evidence_type` | 是 | `string` |  |  |  |
| `source_reference_id` | 是 | `string` |  |  |  |
| `knowledge_base_version_id` | 否 | `string \| null(uuid)` |  | 不可变知识库版本标识 | 李佳乐 |
| `document_id` | 否 | `string \| null(uuid)` |  | 上传文档标识 | 李佳乐 |
| `chunk_id` | 否 | `string \| null` |  |  |  |
| `knowledge_node_id` | 否 | `string \| null` |  |  |  |
| `content_excerpt` | 是 | `string` |  |  |  |
| `content_hash` | 是 | `string` |  |  |  |
| `metadata` | 是 | `object` |  |  |  |
| `created_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_evidence/request.json`
- `mocks/http/get_evidence/response.json`
- `mocks/http/get_evidence/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_latest_decision` — 获取最新最终决策

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/decision`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseFinalDecision`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `FinalDecisionView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `decision_id` | 是 | `string(uuid)` |  | 最终仲裁决策标识 | 张英赫 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `proposal_id` | 是 | `string(uuid)` |  | 智能体候选提案标识 | 张英赫 |
| `decision_type` | 是 | `string` | present_resource, present_assessment, repeat_resource, adjust_difficulty, request_more_evidence, request_human_review, complete_session |  |  |
| `selected_reference_id` | 否 | `string \| null` |  |  |  |
| `target_knowledge_node_ids` | 是 | `array<string>` |  |  |  |
| `decision_summary` | 是 | `string` |  |  |  |
| `reasoning_summary` | 是 | `string` |  |  |  |
| `confidence` | 是 | `number` |  |  |  |
| `evidence_ids` | 是 | `array<string>` |  |  |  |
| `requires_human_review` | 是 | `boolean` |  |  |  |
| `decision_status` | 是 | `string` | proposed, approved, applied, superseded, failed |  |  |
| `created_at` | 是 | `string(date-time)` |  |  |  |
| `applied_at` | 否 | `string \| null(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_latest_decision/request.json`
- `mocks/http/get_latest_decision/response.json`
- `mocks/http/get_latest_decision/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_learner_profile` — 获取最新学习画像

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learners/{learner_id}/profile`
- 契约负责人：杨欣怡
- 实现负责人：杨欣怡
- 展示负责人：陈尧
- 使用成员：X、斯汀、李汝萱、郑翘楚、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseLearnerProfile`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `LearnerProfileView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `profile_snapshot_id` | 是 | `string(uuid)` |  | 不可变学习画像快照标识 | 杨欣怡 |
| `profile_version_no` | 是 | `integer` |  |  |  |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `overall_mastery_score` | 是 | `number` |  |  |  |
| `mastery_items` | 是 | `array<MasteryDimensionView>` |  |  |  |
| `mastery_items[].knowledge_node_id` | 是 | `string` |  |  |  |
| `mastery_items[].knowledge_node_name` | 是 | `string` |  |  |  |
| `mastery_items[].mastery_score` | 是 | `number` |  |  |  |
| `mastery_items[].confidence` | 是 | `number` |  |  |  |
| `mastery_items[].last_evidence_at` | 否 | `string \| null(date-time)` |  |  |  |
| `mastery_items[].weakness_tags` | 是 | `array<string>` |  |  |  |
| `learning_preference_tags` | 是 | `array<string>` |  |  |  |
| `risk_flags` | 是 | `array<string>` |  |  |  |
| `derived_from_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |
| `created_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_learner_profile/request.json`
- `mocks/http/get_learner_profile/response.json`
- `mocks/http/get_learner_profile/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_learning_path` — 获取当前学习路径

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learners/{learner_id}/learning-path`
- 契约负责人：杨欣怡
- 实现负责人：杨欣怡
- 展示负责人：陈尧
- 使用成员：X、斯汀、李汝萱、郑翘楚、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseLearningPath`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `LearningPathView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path_id` | 是 | `string(uuid)` |  |  |  |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `training_program_id` | 是 | `string(uuid)` |  | 培训项目标识 | 杨欣怡 |
| `path_version_no` | 是 | `integer` |  |  |  |
| `path_status` | 是 | `string` | active, completed, superseded |  |  |
| `steps` | 是 | `array<LearningPathStepView>` |  |  |  |
| `steps[].path_step_id` | 是 | `string(uuid)` |  |  |  |
| `steps[].step_order_no` | 是 | `integer` |  |  |  |
| `steps[].knowledge_node_id` | 是 | `string` |  |  |  |
| `steps[].action_type` | 是 | `string` | study, practice, assessment, review |  |  |
| `steps[].difficulty_level` | 是 | `integer` |  |  |  |
| `steps[].step_status` | 是 | `string` | pending, active, completed, skipped |  |  |
| `steps[].reference_id` | 否 | `string \| null(uuid)` |  |  |  |
| `generated_by_decision_cycle_id` | 是 | `string(uuid)` |  |  |  |
| `created_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_learning_path/request.json`
- `mocks/http/get_learning_path/response.json`
- `mocks/http/get_learning_path/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_learning_resource` — 获取学习资源

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/resources/{resource_id}`
- 契约负责人：杨欣怡
- 实现负责人：郑翘楚
- 展示负责人：陈尧
- 使用成员：X、斯汀、郑翘楚
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `path:resource_id` | 是 | `string(uuid)` |  | 审核发布后的学习资源标识 | 杨欣怡 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseResource`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `ResourceView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `resource_id` | 是 | `string(uuid)` |  | 审核发布后的学习资源标识 | 杨欣怡 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `proposal_id` | 是 | `string(uuid)` |  | 智能体候选提案标识 | 张英赫 |
| `resource_type` | 是 | `string` | concept_explanation, worked_example, code_walkthrough, micro_lesson, mixed |  |  |
| `title` | 是 | `string` |  |  |  |
| `summary` | 是 | `string` |  |  |  |
| `difficulty_level` | 是 | `integer` |  |  |  |
| `estimated_minutes` | 是 | `integer` |  |  |  |
| `target_knowledge_node_ids` | 是 | `array<string>` |  |  |  |
| `sections` | 是 | `array<ResourceSectionView>` |  |  |  |
| `sections[].resource_section_id` | 是 | `string(uuid)` |  |  |  |
| `sections[].section_order_no` | 是 | `integer` |  |  |  |
| `sections[].section_type` | 是 | `string` | concept, example, code, exercise_hint, summary |  |  |
| `sections[].heading` | 是 | `string` |  |  |  |
| `sections[].content_markdown` | 是 | `string` |  |  |  |
| `sections[].evidence_ids` | 是 | `array<string>` |  |  |  |
| `citations` | 是 | `array<EvidenceCitationView>` |  |  |  |
| `citations[].evidence_id` | 是 | `string` |  | 可追溯证据标识 | 李佳乐 |
| `citations[].evidence_type` | 是 | `string` | knowledge_chunk, assessment_result, behavior_event, profile_snapshot, agent_proposal, human_review |  |  |
| `citations[].source_reference_id` | 是 | `string` |  |  |  |
| `citations[].document_id` | 否 | `string \| null(uuid)` |  | 上传文档标识 | 李佳乐 |
| `citations[].knowledge_node_id` | 否 | `string \| null` |  |  |  |
| `citations[].citation_text` | 是 | `string` |  |  |  |
| `citations[].relevance_score` | 是 | `number` |  |  |  |
| `citations[].verified` | 是 | `boolean` |  |  |  |
| `review_status` | 是 | `string` | pending, approved, revised, rejected |  |  |
| `resource_status` | 是 | `string` | draft, available, completed, archived |  |  |
| `created_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_learning_resource/request.json`
- `mocks/http/get_learning_resource/response.json`
- `mocks/http/get_learning_resource/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_learning_session` — 获取学习会话

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseLearningSession`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `LearningSessionView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |
| `training_program_id` | 是 | `string(uuid)` |  | 培训项目标识 | 杨欣怡 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `knowledge_base_version_id` | 是 | `string(uuid)` |  | 不可变知识库版本标识 | 李佳乐 |
| `profile_snapshot_id` | 是 | `string(uuid)` |  | 不可变学习画像快照标识 | 杨欣怡 |
| `session_status` | 是 | `string` | created, running, waiting_for_learner, human_review_required, completed, failed, cancelled |  |  |
| `current_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |
| `current_action_type` | 否 | `string \| null` |  |  |  |
| `started_at` | 是 | `string(date-time)` |  |  |  |
| `completed_at` | 否 | `string \| null(date-time)` |  |  |  |
| `updated_at` | 是 | `string(date-time)` |  |  |  |
| `error_code` | 否 | `string \| null` |  |  |  |
| `error_message` | 否 | `string \| null` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_learning_session/request.json`
- `mocks/http/get_learning_session/response.json`
- `mocks/http/get_learning_session/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `get_organization` — 获取组织信息

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：无
- 使用成员：X、斯汀、陈严谨
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseOrganization`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `OrganizationView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `organization_name` | 是 | `string` |  |  |  |
| `organization_status` | 是 | `string` | active, suspended |  |  |
| `created_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/get_organization/request.json`
- `mocks/http/get_organization/response.json`
- `mocks/http/get_organization/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `list_decision_cycles` — 查询决策轮次

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/decision-cycles`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `query:page_no` | 否 | `integer` |  |  |  |
| `query:page_size` | 否 | `integer` |  |  |  |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseDecisionCycleList`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `object` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `items` | 是 | `array<DecisionCycleView>` |  |  |  |
| `items[].decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `items[].session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `items[].cycle_no` | 是 | `integer` |  |  |  |
| `items[].trigger_type` | 是 | `string` | session_started, resource_completed, assessment_submitted, manual_retry, human_review_resolved |  |  |
| `items[].trigger_reference_id` | 否 | `string \| null` |  |  |  |
| `items[].decision_cycle_status` | 是 | `string` | queued, collecting_context, running_agents, reviewing, arbitrating, action_ready, applied, human_review_required, failed |  |  |
| `items[].started_at` | 是 | `string(date-time)` |  |  |  |
| `items[].finished_at` | 否 | `string \| null(date-time)` |  |  |  |
| `items[].failure_code` | 否 | `string \| null` |  |  |  |
| `page` | 是 | `PageMeta` |  |  |  |
| `page.page_no` | 是 | `integer` |  | 页码 |  |
| `page.page_size` | 是 | `integer` |  | 每页数量 |  |
| `page.total_count` | 是 | `integer` |  | 总记录数 |  |
| `page.has_next` | 是 | `boolean` |  | 是否有下一页 |  |

**必须使用的 Mock**

- `mocks/http/list_decision_cycles/request.json`
- `mocks/http/list_decision_cycles/response.json`
- `mocks/http/list_decision_cycles/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `list_learner_assignments` — 查询学习者培训任务

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learners/{learner_id}/assignments`
- 契约负责人：杨欣怡
- 实现负责人：陈严谨
- 展示负责人：无
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `query:page_no` | 否 | `integer` |  |  |  |
| `query:page_size` | 否 | `integer` |  |  |  |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseLearnerAssignmentList`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `object` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `items` | 是 | `array<LearnerAssignmentView>` |  |  |  |
| `items[].assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |
| `items[].organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `items[].training_program_id` | 是 | `string(uuid)` |  | 培训项目标识 | 杨欣怡 |
| `items[].learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `items[].assignment_status` | 是 | `string` | assigned, in_progress, completed, cancelled, expired |  |  |
| `items[].due_at` | 否 | `string \| null(date-time)` |  |  |  |
| `items[].assigned_by_user_id` | 是 | `string(uuid)` |  |  |  |
| `items[].assigned_at` | 是 | `string(date-time)` |  |  |  |
| `items[].started_at` | 否 | `string \| null(date-time)` |  |  |  |
| `items[].completed_at` | 否 | `string \| null(date-time)` |  |  |  |
| `page` | 是 | `PageMeta` |  |  |  |
| `page.page_no` | 是 | `integer` |  | 页码 |  |
| `page.page_size` | 是 | `integer` |  | 每页数量 |  |
| `page.total_count` | 是 | `integer` |  | 总记录数 |  |
| `page.has_next` | 是 | `boolean` |  | 是否有下一页 |  |

**必须使用的 Mock**

- `mocks/http/list_learner_assignments/request.json`
- `mocks/http/list_learner_assignments/response.json`
- `mocks/http/list_learner_assignments/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `list_learning_sessions` — 查询学习会话

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `query:page_no` | 否 | `integer` |  |  |  |
| `query:page_size` | 否 | `integer` |  |  |  |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseLearningSessionList`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `object` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `items` | 是 | `array<LearningSessionView>` |  |  |  |
| `items[].session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `items[].organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `items[].assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |
| `items[].training_program_id` | 是 | `string(uuid)` |  | 培训项目标识 | 杨欣怡 |
| `items[].learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `items[].knowledge_base_version_id` | 是 | `string(uuid)` |  | 不可变知识库版本标识 | 李佳乐 |
| `items[].profile_snapshot_id` | 是 | `string(uuid)` |  | 不可变学习画像快照标识 | 杨欣怡 |
| `items[].session_status` | 是 | `string` | created, running, waiting_for_learner, human_review_required, completed, failed, cancelled |  |  |
| `items[].current_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |
| `items[].current_action_type` | 否 | `string \| null` |  |  |  |
| `items[].started_at` | 是 | `string(date-time)` |  |  |  |
| `items[].completed_at` | 否 | `string \| null(date-time)` |  |  |  |
| `items[].updated_at` | 是 | `string(date-time)` |  |  |  |
| `items[].error_code` | 否 | `string \| null` |  |  |  |
| `items[].error_message` | 否 | `string \| null` |  |  |  |
| `page` | 是 | `PageMeta` |  |  |  |
| `page.page_no` | 是 | `integer` |  | 页码 |  |
| `page.page_size` | 是 | `integer` |  | 每页数量 |  |
| `page.total_count` | 是 | `integer` |  | 总记录数 |  |
| `page.has_next` | 是 | `boolean` |  | 是否有下一页 |  |

**必须使用的 Mock**

- `mocks/http/list_learning_sessions/request.json`
- `mocks/http/list_learning_sessions/response.json`
- `mocks/http/list_learning_sessions/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `list_profile_history` — 查询画像历史

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learners/{learner_id}/profile-history`
- 契约负责人：杨欣怡
- 实现负责人：杨欣怡
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `query:page_no` | 否 | `integer` |  |  |  |
| `query:page_size` | 否 | `integer` |  |  |  |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseProfileHistoryList`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `object` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `items` | 是 | `array<ProfileHistoryItemView>` |  |  |  |
| `items[].profile_snapshot_id` | 是 | `string(uuid)` |  | 不可变学习画像快照标识 | 杨欣怡 |
| `items[].profile_version_no` | 是 | `integer` |  |  |  |
| `items[].overall_mastery_score` | 是 | `number` |  |  |  |
| `items[].changed_knowledge_node_ids` | 是 | `array<string>` |  |  |  |
| `items[].change_reason_code` | 是 | `string` |  |  |  |
| `items[].derived_from_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |
| `items[].created_at` | 是 | `string(date-time)` |  |  |  |
| `page` | 是 | `PageMeta` |  |  |  |
| `page.page_no` | 是 | `integer` |  | 页码 |  |
| `page.page_size` | 是 | `integer` |  | 每页数量 |  |
| `page.total_count` | 是 | `integer` |  | 总记录数 |  |
| `page.has_next` | 是 | `boolean` |  | 是否有下一页 |  |

**必须使用的 Mock**

- `mocks/http/list_profile_history/request.json`
- `mocks/http/list_profile_history/response.json`
- `mocks/http/list_profile_history/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `list_session_events` — 增量查询会话事件

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/events`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀、陈尧
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `query:after_sequence_no` | 否 | `integer` |  |  |  |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseAgentEventList`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `object` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `items` | 是 | `array<AgentEventView>` |  |  |  |
| `items[].event_id` | 是 | `string(uuid)` |  |  |  |
| `items[].organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `items[].session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `items[].decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `items[].agent_run_id` | 否 | `string \| null(uuid)` |  | 一次智能体运行标识 | 张英赫 |
| `items[].sequence_no` | 是 | `integer` |  |  |  |
| `items[].event_type` | 是 | `string` | cycle_started, context_collected, agent_started, agent_succeeded, agent_failed, proposal_created, review_completed, arbitration_completed, action_applied, human_review_requested, cycle_failed |  |  |
| `items[].agent_code` | 否 | `string \| null` |  |  |  |
| `items[].reference_id` | 否 | `string \| null` |  |  |  |
| `items[].summary_text` | 是 | `string` |  |  |  |
| `items[].occurred_at` | 是 | `string(date-time)` |  |  |  |
| `last_sequence_no` | 是 | `integer` |  |  |  |

**必须使用的 Mock**

- `mocks/http/list_session_events/request.json`
- `mocks/http/list_session_events/response.json`
- `mocks/http/list_session_events/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `list_session_resources` — 查询会话学习资源

- 你的关系：**调用/展示方**
- 方法与路径：`GET /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/resources`
- 契约负责人：杨欣怡
- 实现负责人：郑翘楚
- 展示负责人：陈尧
- 使用成员：X、斯汀、郑翘楚
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `query:page_no` | 否 | `integer` |  |  |  |
| `query:page_size` | 否 | `integer` |  |  |  |

**请求体结构：`无请求体`**

无

**成功响应结构：`ApiResponseResourceList`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `object` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `items` | 是 | `array<ResourceView>` |  |  |  |
| `items[].resource_id` | 是 | `string(uuid)` |  | 审核发布后的学习资源标识 | 杨欣怡 |
| `items[].organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `items[].session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `items[].decision_cycle_id` | 是 | `string(uuid)` |  | 会话内一轮联合决策标识 | 张英赫 |
| `items[].proposal_id` | 是 | `string(uuid)` |  | 智能体候选提案标识 | 张英赫 |
| `items[].resource_type` | 是 | `string` | concept_explanation, worked_example, code_walkthrough, micro_lesson, mixed |  |  |
| `items[].title` | 是 | `string` |  |  |  |
| `items[].summary` | 是 | `string` |  |  |  |
| `items[].difficulty_level` | 是 | `integer` |  |  |  |
| `items[].estimated_minutes` | 是 | `integer` |  |  |  |
| `items[].target_knowledge_node_ids` | 是 | `array<string>` |  |  |  |
| `items[].sections` | 是 | `array<ResourceSectionView>` |  |  |  |
| `items[].sections[].resource_section_id` | 是 | `string(uuid)` |  |  |  |
| `items[].sections[].section_order_no` | 是 | `integer` |  |  |  |
| `items[].sections[].section_type` | 是 | `string` | concept, example, code, exercise_hint, summary |  |  |
| `items[].sections[].heading` | 是 | `string` |  |  |  |
| `items[].sections[].content_markdown` | 是 | `string` |  |  |  |
| `items[].sections[].evidence_ids` | 是 | `array<string>` |  |  |  |
| `items[].citations` | 是 | `array<EvidenceCitationView>` |  |  |  |
| `items[].citations[].evidence_id` | 是 | `string` |  | 可追溯证据标识 | 李佳乐 |
| `items[].citations[].evidence_type` | 是 | `string` | knowledge_chunk, assessment_result, behavior_event, profile_snapshot, agent_proposal, human_review |  |  |
| `items[].citations[].source_reference_id` | 是 | `string` |  |  |  |
| `items[].citations[].document_id` | 否 | `string \| null(uuid)` |  | 上传文档标识 | 李佳乐 |
| `items[].citations[].knowledge_node_id` | 否 | `string \| null` |  |  |  |
| `items[].citations[].citation_text` | 是 | `string` |  |  |  |
| `items[].citations[].relevance_score` | 是 | `number` |  |  |  |
| `items[].citations[].verified` | 是 | `boolean` |  |  |  |
| `items[].review_status` | 是 | `string` | pending, approved, revised, rejected |  |  |
| `items[].resource_status` | 是 | `string` | draft, available, completed, archived |  |  |
| `items[].created_at` | 是 | `string(date-time)` |  |  |  |
| `page` | 是 | `PageMeta` |  |  |  |
| `page.page_no` | 是 | `integer` |  | 页码 |  |
| `page.page_size` | 是 | `integer` |  | 每页数量 |  |
| `page.total_count` | 是 | `integer` |  | 总记录数 |  |
| `page.has_next` | 是 | `boolean` |  | 是否有下一页 |  |

**必须使用的 Mock**

- `mocks/http/list_session_resources/request.json`
- `mocks/http/list_session_resources/response.json`
- `mocks/http/list_session_resources/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `login` — 用户登录

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/auth/login`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：无
- 使用成员：X、斯汀、陈严谨
- 契约状态：`frozen_v6`

**路径与查询变量**

无

**请求体结构：`LoginRequest`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `email` | 是 | `string` |  | 邮箱 |  |
| `password` | 是 | `string` |  | 密码 |  |

**成功响应结构：`ApiResponseToken`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `TokenView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `access_token` | 是 | `string` |  |  |  |
| `refresh_token` | 是 | `string` |  |  |  |
| `token_type` | 是 | `string` | bearer |  |  |
| `expires_in_seconds` | 是 | `integer` |  |  |  |
| `user` | 是 | `UserView` |  |  |  |
| `user.user_id` | 是 | `string(uuid)` |  | 用户标识 |  |
| `user.organization_id` | 是 | `string(uuid)` |  | 组织标识 | 张英赫 |
| `user.display_name` | 是 | `string` |  | 显示名称 |  |
| `user.email` | 是 | `string` |  | 邮箱 |  |
| `user.role_code` | 是 | `string` | platform_admin, organization_admin, trainer, reviewer, learner | 角色编码 |  |
| `user.learner_id` | 否 | `string \| null(uuid)` |  | 学习者标识 | 杨欣怡 |
| `user.account_status` | 是 | `string` | active, disabled, pending | 账号状态 |  |

**必须使用的 Mock**

- `mocks/http/login/request.json`
- `mocks/http/login/response.json`
- `mocks/http/login/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `logout` — 退出登录

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/auth/logout`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：无
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

无

**请求体结构：`无请求体`**

无

**成功响应结构：`无 JSON 响应体`**

统一响应外壳：

无

响应 `data` 中的主要跨模块字段：

无

**必须使用的 Mock**

- `mocks/http/logout/request.json`
- `mocks/http/logout/response.json`
- `mocks/http/logout/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `record_behavior_events` — 批量记录学习行为

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/behavior-events:batch`
- 契约负责人：杨欣怡
- 实现负责人：杨欣怡
- 展示负责人：无
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`BehaviorEventBatchRequest`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `events` | 是 | `array<BehaviorEventInput>` |  |  |  |
| `events[].client_event_id` | 是 | `string` |  |  |  |
| `events[].event_type` | 是 | `string` | page_viewed, resource_opened, resource_section_viewed, resource_completed, assessment_started, question_answered, assessment_submitted, help_requested, session_paused, session_resumed |  |  |
| `events[].session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `events[].resource_id` | 否 | `string \| null(uuid)` |  | 审核发布后的学习资源标识 | 杨欣怡 |
| `events[].resource_section_id` | 否 | `string \| null(uuid)` |  |  |  |
| `events[].assessment_id` | 否 | `string \| null(uuid)` |  | 审核发布后的测评标识 | 杨欣怡 |
| `events[].question_id` | 否 | `string \| null(uuid)` |  |  |  |
| `events[].duration_seconds` | 否 | `integer \| null` |  |  |  |
| `events[].event_payload` | 是 | `object` |  |  |  |
| `events[].occurred_at` | 是 | `string(date-time)` |  |  |  |

**成功响应结构：`无 JSON 响应体`**

统一响应外壳：

无

响应 `data` 中的主要跨模块字段：

无

**必须使用的 Mock**

- `mocks/http/record_behavior_events/request.json`
- `mocks/http/record_behavior_events/response.json`
- `mocks/http/record_behavior_events/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `refresh_token` — 刷新访问令牌

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/auth/refresh`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：无
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

无

**请求体结构：`RefreshTokenRequest`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `refresh_token` | 是 | `string` |  |  |  |

**成功响应结构：`ApiResponseToken`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `TokenView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `access_token` | 是 | `string` |  |  |  |
| `refresh_token` | 是 | `string` |  |  |  |
| `token_type` | 是 | `string` | bearer |  |  |
| `expires_in_seconds` | 是 | `integer` |  |  |  |
| `user` | 是 | `UserView` |  |  |  |
| `user.user_id` | 是 | `string(uuid)` |  | 用户标识 |  |
| `user.organization_id` | 是 | `string(uuid)` |  | 组织标识 | 张英赫 |
| `user.display_name` | 是 | `string` |  | 显示名称 |  |
| `user.email` | 是 | `string` |  | 邮箱 |  |
| `user.role_code` | 是 | `string` | platform_admin, organization_admin, trainer, reviewer, learner | 角色编码 |  |
| `user.learner_id` | 否 | `string \| null(uuid)` |  | 学习者标识 | 杨欣怡 |
| `user.account_status` | 是 | `string` | active, disabled, pending | 账号状态 |  |

**必须使用的 Mock**

- `mocks/http/refresh_token/request.json`
- `mocks/http/refresh_token/response.json`
- `mocks/http/refresh_token/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `start_learning_session` — 启动学习会话

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/organizations/{organization_id}/learning-sessions`
- 契约负责人：张英赫
- 实现负责人：张英赫
- 展示负责人：陈尧
- 使用成员：X、斯汀
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |

**请求体结构：`StartLearningSessionRequest`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |
| `idempotency_key` | 是 | `string` |  | 避免重复创建或重复提交的幂等键 | 张英赫 |
| `client_context` | 否 | `object` |  |  |  |
| `client_context.timezone` | 否 | `string \| null` |  |  |  |
| `client_context.locale` | 否 | `string \| null` |  |  |  |
| `client_context.device_type` | 否 | `string \| null` |  |  |  |

**成功响应结构：`ApiResponseLearningSession`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `LearningSessionView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `assignment_id` | 是 | `string(uuid)` |  | 培训分配标识 | 杨欣怡 |
| `training_program_id` | 是 | `string(uuid)` |  | 培训项目标识 | 杨欣怡 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `knowledge_base_version_id` | 是 | `string(uuid)` |  | 不可变知识库版本标识 | 李佳乐 |
| `profile_snapshot_id` | 是 | `string(uuid)` |  | 不可变学习画像快照标识 | 杨欣怡 |
| `session_status` | 是 | `string` | created, running, waiting_for_learner, human_review_required, completed, failed, cancelled |  |  |
| `current_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |
| `current_action_type` | 否 | `string \| null` |  |  |  |
| `started_at` | 是 | `string(date-time)` |  |  |  |
| `completed_at` | 否 | `string \| null(date-time)` |  |  |  |
| `updated_at` | 是 | `string(date-time)` |  |  |  |
| `error_code` | 否 | `string \| null` |  |  |  |
| `error_message` | 否 | `string \| null` |  |  |  |

**必须使用的 Mock**

- `mocks/http/start_learning_session/request.json`
- `mocks/http/start_learning_session/response.json`
- `mocks/http/start_learning_session/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `submit_assessment_attempt` — 提交测评答案

- 你的关系：**调用/展示方**
- 方法与路径：`POST /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/assessment-attempts`
- 契约负责人：杨欣怡
- 实现负责人：李汝萱
- 展示负责人：陈尧
- 使用成员：X、斯汀、李汝萱
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |

**请求体结构：`SubmitAssessmentAttemptRequest`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `assessment_id` | 是 | `string(uuid)` |  | 审核发布后的测评标识 | 杨欣怡 |
| `answers` | 是 | `array<AssessmentAnswerInput>` |  |  |  |
| `answers[].question_id` | 是 | `string(uuid)` |  |  |  |
| `answers[].answer_type` | 是 | `string` | selected_options, boolean, text, code |  |  |
| `answers[].selected_option_ids` | 是 | `array<string(uuid)>` |  |  |  |
| `answers[].boolean_value` | 否 | `boolean \| null` |  |  |  |
| `answers[].text_value` | 否 | `string \| null` |  |  |  |
| `answers[].code_value` | 否 | `string \| null` |  |  |  |
| `answers[].code_language` | 否 | `string \| null` |  |  |  |
| `answers[].client_answered_at` | 是 | `string(date-time)` |  |  |  |
| `started_at` | 是 | `string(date-time)` |  |  |  |
| `submitted_at` | 是 | `string(date-time)` |  |  |  |
| `idempotency_key` | 是 | `string` |  | 避免重复创建或重复提交的幂等键 | 张英赫 |

**成功响应结构：`ApiResponseAssessmentResult`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `AssessmentResultView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `attempt_id` | 是 | `string(uuid)` |  | 一次作答记录标识 | 杨欣怡 |
| `assessment_id` | 是 | `string(uuid)` |  | 审核发布后的测评标识 | 杨欣怡 |
| `session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `attempt_status` | 是 | `string` | submitted, scoring, scored, scoring_failed |  |  |
| `total_awarded_score` | 是 | `number` |  |  |  |
| `total_score_points` | 是 | `number` |  |  |  |
| `score_ratio` | 是 | `number` |  |  |  |
| `question_results` | 是 | `array<QuestionResultView>` |  |  |  |
| `question_results[].question_id` | 是 | `string(uuid)` |  |  |  |
| `question_results[].is_correct` | 是 | `boolean` |  |  |  |
| `question_results[].awarded_score_points` | 是 | `number` |  |  |  |
| `question_results[].max_score_points` | 是 | `number` |  |  |  |
| `question_results[].error_type_codes` | 是 | `array<string>` |  |  |  |
| `question_results[].feedback_markdown` | 是 | `string` |  |  |  |
| `question_results[].knowledge_node_mastery_delta` | 是 | `object` |  |  |  |
| `scored_at` | 否 | `string \| null(date-time)` |  |  |  |
| `next_decision_cycle_id` | 否 | `string \| null(uuid)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/submit_assessment_attempt/request.json`
- `mocks/http/submit_assessment_attempt/response.json`
- `mocks/http/submit_assessment_attempt/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。

### `update_resource_progress` — 更新资源学习进度

- 你的关系：**调用/展示方**
- 方法与路径：`PATCH /api/v1/organizations/{organization_id}/learning-sessions/{session_id}/resources/{resource_id}/progress`
- 契约负责人：杨欣怡
- 实现负责人：郑翘楚
- 展示负责人：陈尧
- 使用成员：X、斯汀、郑翘楚
- 契约状态：`frozen_v6`

**路径与查询变量**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `path:organization_id` | 是 | `string(uuid)` |  | 组织租户标识 | 张英赫 |
| `path:session_id` | 是 | `string(uuid)` |  | 一次完整学习会话标识 | 张英赫 |
| `path:resource_id` | 是 | `string(uuid)` |  | 审核发布后的学习资源标识 | 杨欣怡 |

**请求体结构：`UpdateResourceProgressRequest`**

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `progress_status` | 是 | `string` | in_progress, completed, skipped |  |  |
| `progress_percent` | 是 | `integer` |  |  |  |
| `last_section_id` | 否 | `string \| null(uuid)` |  |  |  |
| `time_spent_delta_seconds` | 是 | `integer` |  |  |  |
| `idempotency_key` | 是 | `string` |  | 避免重复创建或重复提交的幂等键 | 张英赫 |

**成功响应结构：`ApiResponseResourceProgress`**

统一响应外壳：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `code` | 是 | `string` |  |  |  |
| `message` | 是 | `string` |  |  |  |
| `data` | 是 | `ResourceProgressView` |  |  |  |
| `meta` | 是 | `ResponseMeta` |  |  |  |

响应 `data` 中的主要跨模块字段：

| 字段 | 必填 | 类型 | 枚举/限制 | 含义 | 字段负责人 |
|---|---|---|---|---|---|
| `resource_id` | 是 | `string(uuid)` |  | 审核发布后的学习资源标识 | 杨欣怡 |
| `learner_id` | 是 | `string(uuid)` |  | 学习者标识 | 杨欣怡 |
| `progress_status` | 是 | `string` | not_started, in_progress, completed, skipped |  |  |
| `progress_percent` | 是 | `integer` |  |  |  |
| `last_section_id` | 否 | `string \| null(uuid)` |  |  |  |
| `time_spent_seconds` | 是 | `integer` |  |  |  |
| `updated_at` | 是 | `string(date-time)` |  |  |  |

**必须使用的 Mock**

- `mocks/http/update_resource_progress/request.json`
- `mocks/http/update_resource_progress/response.json`
- `mocks/http/update_resource_progress/error_response.json`

> 实现时不得根据页面便利改字段。若当前字段无法满足真实业务，先提交接口变更申请。


## 7. 逐个智能体内部接口说明

本成员没有直接智能体接口，但仍需遵守公开接口和跨模块字段契约。

## 8. 你的 Mock 已经固化在哪里

使用规则：

1. 页面开发先读取 HTTP `response.json` 的 `body`。
2. 后端实现用 `request.json` 验证输入，用 `response.json` 验证输出。
3. 智能体开发用对应 `request.json` 与 `response.json`。
4. 错误页面至少覆盖 `error_response.json`。
5. 禁止把 Mock 中的示例 UUID、文案或分数当成业务常量写死。
6. 真实接口完成后，只切换数据源，不改页面字段。

### HTTP 接口 Mock

- `mocks/http/cancel_learning_session/error_response.json`
- `mocks/http/cancel_learning_session/request.json`
- `mocks/http/cancel_learning_session/response.json`
- `mocks/http/create_session_feedback/error_response.json`
- `mocks/http/create_session_feedback/request.json`
- `mocks/http/create_session_feedback/response.json`
- `mocks/http/get_assessment_attempt_result/error_response.json`
- `mocks/http/get_assessment_attempt_result/request.json`
- `mocks/http/get_assessment_attempt_result/response.json`
- `mocks/http/get_assignment/error_response.json`
- `mocks/http/get_assignment/request.json`
- `mocks/http/get_assignment/response.json`
- `mocks/http/get_current_action/error_response.json`
- `mocks/http/get_current_action/request.json`
- `mocks/http/get_current_action/response.json`
- `mocks/http/get_current_assessment/error_response.json`
- `mocks/http/get_current_assessment/request.json`
- `mocks/http/get_current_assessment/response.json`
- `mocks/http/get_current_user/error_response.json`
- `mocks/http/get_current_user/request.json`
- `mocks/http/get_current_user/response.json`
- `mocks/http/get_decision_cycle/error_response.json`
- `mocks/http/get_decision_cycle/request.json`
- `mocks/http/get_decision_cycle/response.json`
- `mocks/http/get_decision_trace/error_response.json`
- `mocks/http/get_decision_trace/request.json`
- `mocks/http/get_decision_trace/response.json`
- `mocks/http/get_evidence/error_response.json`
- `mocks/http/get_evidence/request.json`
- `mocks/http/get_evidence/response.json`
- `mocks/http/get_latest_decision/error_response.json`
- `mocks/http/get_latest_decision/request.json`
- `mocks/http/get_latest_decision/response.json`
- `mocks/http/get_learner_profile/error_response.json`
- `mocks/http/get_learner_profile/request.json`
- `mocks/http/get_learner_profile/response.json`
- `mocks/http/get_learning_path/error_response.json`
- `mocks/http/get_learning_path/request.json`
- `mocks/http/get_learning_path/response.json`
- `mocks/http/get_learning_resource/error_response.json`
- `mocks/http/get_learning_resource/request.json`
- `mocks/http/get_learning_resource/response.json`
- `mocks/http/get_learning_session/error_response.json`
- `mocks/http/get_learning_session/request.json`
- `mocks/http/get_learning_session/response.json`
- `mocks/http/get_organization/error_response.json`
- `mocks/http/get_organization/request.json`
- `mocks/http/get_organization/response.json`
- `mocks/http/list_decision_cycles/error_response.json`
- `mocks/http/list_decision_cycles/request.json`
- `mocks/http/list_decision_cycles/response.json`
- `mocks/http/list_learner_assignments/error_response.json`
- `mocks/http/list_learner_assignments/request.json`
- `mocks/http/list_learner_assignments/response.json`
- `mocks/http/list_learning_sessions/error_response.json`
- `mocks/http/list_learning_sessions/request.json`
- `mocks/http/list_learning_sessions/response.json`
- `mocks/http/list_profile_history/error_response.json`
- `mocks/http/list_profile_history/request.json`
- `mocks/http/list_profile_history/response.json`
- `mocks/http/list_session_events/error_response.json`
- `mocks/http/list_session_events/request.json`
- `mocks/http/list_session_events/response.json`
- `mocks/http/list_session_resources/error_response.json`
- `mocks/http/list_session_resources/request.json`
- `mocks/http/list_session_resources/response.json`
- `mocks/http/login/error_response.json`
- `mocks/http/login/request.json`
- `mocks/http/login/response.json`
- `mocks/http/logout/error_response.json`
- `mocks/http/logout/request.json`
- `mocks/http/logout/response.json`
- `mocks/http/record_behavior_events/error_response.json`
- `mocks/http/record_behavior_events/request.json`
- `mocks/http/record_behavior_events/response.json`
- `mocks/http/refresh_token/error_response.json`
- `mocks/http/refresh_token/request.json`
- `mocks/http/refresh_token/response.json`
- `mocks/http/start_learning_session/error_response.json`
- `mocks/http/start_learning_session/request.json`
- `mocks/http/start_learning_session/response.json`
- `mocks/http/submit_assessment_attempt/error_response.json`
- `mocks/http/submit_assessment_attempt/request.json`
- `mocks/http/submit_assessment_attempt/response.json`
- `mocks/http/update_resource_progress/error_response.json`
- `mocks/http/update_resource_progress/request.json`
- `mocks/http/update_resource_progress/response.json`
### 完整流程 Mock

- `mocks/workflows/learner_agent_loop_flow.json`

## 9. 分阶段开发任务

1. 阶段0：学习端接口切片和Mock
2. 阶段1：任务、会话、当前动作和基础时间线
3. 阶段2：知识来源与构建状态提示
4. 阶段3：画像、路径和任务页面
5. 阶段4：资源与测评页面导航联调
6. 阶段5：分歧、证据、审核和最终决策回放
7. 阶段6：响应式和性能修复
8. 阶段7：演示操作配合

每个阶段只能在上一个阶段验收通过后进入下一阶段。页面成员优先完成 Mock 闭环；智能体成员优先完成 Schema 校验和确定性 Mock，再接真实模型。

## 10. 每个任务的固定执行步骤

1. 从最新 `develop` 创建独立功能分支。
2. 阅读任务卡，确认允许修改目录、operation_id、Schema 和 Mock。
3. 先用 Mock 或确定性实现跑通，不直接连接真实模型。
4. 编写实现，不改变跨模块字段。
5. 覆盖成功、空数据、错误、超时/重试或重复提交情况。
6. 运行类型检查、单元测试、契约校验和构建。
7. 在 PR 中写明使用的 operation_id、Schema、Mock 和跨模块边界编号。
8. 审核人批准且自动测试通过后才能合并。

## 11. 给 AI 编码工具的固定提示词

将下面文字放在每次 Codex 或其他 AI 编码任务开头，再追加具体任务：

```text
你正在完成挑战杯项目中“学习端页面与决策回放实现”相关任务。必须遵守以下规则：
1. 只修改任务卡允许的目录：apps/web/src/features/learner/**, apps/web/src/features/decision-trace/**, tests/learner/**。
2. HTTP 接口只使用本文件列出的 operation_id、方法、路径和字段；不得自行改名。
3. 智能体或内部服务输出必须通过指定 JSON Schema 校验。
4. 跨模块 JSON 字段使用 snake_case；TypeScript 类型名使用 PascalCase。
5. 不得修改 api/openapi.yaml、api/internal_agent_interfaces.yaml、contracts/jsonschema/，除非接口变更申请已批准。
6. 必须使用对应 Mock 完成正常、空数据、错误、超时/重试状态。
7. 输出代码后列出：修改文件、使用的 operation_id、使用的 Schema、运行的测试命令。
```

## 12. 提交前验收清单

- [ ] 当前分支不是 `main` 或 `develop`
- [ ] 只修改了允许目录和任务卡列出的文件
- [ ] 使用了正确的 operation_id、方法和路径
- [ ] 请求字段、响应字段、枚举值与契约完全一致
- [ ] 智能体/服务输出通过 JSON Schema 校验
- [ ] 没有把内部临时变量直接作为跨模块字段
- [ ] 没有把草稿编号当成正式编号
- [ ] 没有在前端泄露测评答案或内部推理原文
- [ ] 使用了指定 Mock，没有新建第二套 Mock
- [ ] 成功、空数据、错误、加载状态已测试
- [ ] 幂等、权限、组织隔离和异常恢复已按任务要求处理
- [ ] PR 已列出 operation_id、Schema、Mock、测试结果和截图/日志

## 13. 接口不够用时怎么办

不得直接改字段。填写 `templates/API_CHANGE_REQUEST.md`，至少说明：

- 当前 operation_id 或内部接口名称
- 现有字段为什么无法满足
- 建议新增、删除或修改的字段
- 生产方、消费方和受影响成员
- 对 OpenAPI、Schema、Mock、类型和数据库的影响
- 兼容方案与迁移方式

批准后按顺序修改：正式契约 → Schema → Mock → 类型 → 实现 → 测试。
