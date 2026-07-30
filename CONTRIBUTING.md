# 代码协作规则

## 分支

- `main`：稳定、可演示、可发布。
- `develop`：已审核的集成分支。
- `feature/<task-name>`：功能。
- `fix/<issue-name>`：缺陷修复。
- `test/<scope>`：评测或测试。
- `docs/<scope>`：文档。

所有正式代码通过 Pull Request 合入 `develop`。`develop` 通过完整回归后再合入 `main`。

## 成长型成员任务限制

- 一个任务一个分支一个 PR。
- 一个 PR 只解决一个明确问题。
- 默认不超过 5 个主要文件、300 行核心改动。
- 不得修改公共接口、公共类型、数据库核心表、智能体状态机和权限逻辑。
- 需要修改契约时，先提交 `templates/API_CHANGE_REQUEST.md`，批准后再编码。

## 提交格式

```text
feat: 新功能
fix: 修复问题
docs: 文档
test: 测试
refactor: 重构
chore: 工程配置
```

## 合并门禁

- 契约校验通过。
- 静态检查通过。
- 单元测试和构建通过。
- 对应负责人批准。
- 所有阻塞讨论已解决。
- 接口行为与 Mock、OpenAPI 和 JSON Schema 一致。
