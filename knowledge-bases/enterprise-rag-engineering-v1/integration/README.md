# 与现有 `-IanZhang--main` 仓库的接入说明

本 Domain Pack 已按仓库 V6.1 的检索请求/响应和六智能体输出 Schema 制作兼容样例，不要求修改现有冻结字段。

## 推荐目录

```text
knowledge-bases/enterprise-rag-engineering-v1/
```

## 接入顺序

1. 先在独立目录执行校验和词法检索评测；
2. 后端应用扩展迁移并执行 dry-run 导入；
3. 创建或映射既有 `knowledge_bases`、`build_runs`、`knowledge_base_versions` 基础记录；
4. 导入节点、关系、切片、题库和评测集；
5. 通过现有 retrieval Schema 运行契约测试；
6. 把该版本绑定到训练项目；
7. 前端只显示后端返回的资源和证据，不直接读取包文件。

## 主线修正

现有仓库中“自动知识工程层”应降级为可选扩展。比赛主闭环默认使用本预建、验证并发布的Domain Pack；自动接入新资料时只生成候选版本，未经评测和人工批准不得激活。
