# 挑战杯多智能体平台开发契约包 V6

本版本在 V5 完整用户流程基础上，进一步把九名成员各自需要阅读的文件、公开接口、内部智能体接口、跨模块边界、Mock、允许修改范围和阶段任务全部固化。

## 开始方式

每名成员只需要先进入自己的目录：

- `members/P1_张英赫/`
- `members/P2_李佳乐/`
- `members/P3_杨欣怡/`
- `members/P4_陈尧/`
- `members/P5_郑翘楚/`
- `members/P6_李汝萱/`
- `members/P7_陈严谨/`
- `members/P8_X/`
- `members/P9_斯汀/`

然后按顺序阅读：

1. `00_开始这里.md`
2. `openapi_scope.yaml`
3. `internal_scope.yaml`
4. `mock_index.yaml`

## 唯一事实来源

- 公开接口：`api/openapi.yaml`
- 每人公开接口切片：`members/*/openapi_scope.yaml`
- 智能体接口：`api/internal_agent_interfaces.yaml`
- 智能体字段：`contracts/jsonschema/agents/`
- 内部服务字段：`contracts/jsonschema/services/`
- 跨模块边界：`project/boundary_contract_manifest.yaml`
- API负责人：`project/api_ownership.yaml`
- Mock：`mocks/`
- 每人责任契约：`project/member_contracts/`

## 冻结原则

模块内部变量名不强制统一；任何数据一旦离开模块，必须转换为契约中规定的字段名和类型。任何跨模块字段变更，必须先修改契约、Mock、类型和影响清单，再修改实现。

## 自动检查

```bash
python scripts/validate_v6_contracts.py
```

检查通过后，才允许把本版本标记为正式开发基线。


## V6.1 成员独立开发入口

每名成员请优先阅读：`members/<自己的目录>/00_完整开发文件.md`。

九份完整文件索引：`docs/31_九成员独立开发文件说明.md`。

说明：V6.1 只增强成员教程，正式 API、字段、Schema 与 Mock 仍保持 `frozen_v6`。
