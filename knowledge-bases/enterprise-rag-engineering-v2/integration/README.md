# 主项目接入说明

本 Domain Pack v2 与主项目 v7 契约兼容。主项目不再使用“六智能体 + 自动建库”旧主线，而是使用七核心 Agent、平行生成/审核和自适应检索。

接入顺序：

1. 运行数据库迁移；
2. 执行 `scripts/import_to_postgres.py --dry-run`；
3. 启动知识服务或将数据导入主 PostgreSQL；
4. 后端通过 Internal API 创建 Retrieval Plan / Run；
5. Agent Runtime 消费 Evidence Bundle；
6. 运行 3 组兼容样例和主项目全量契约校验。
