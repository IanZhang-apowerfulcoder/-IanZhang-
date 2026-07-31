# HTTP 调用示例

先启动服务：

```bash
uvicorn server.app:app --host 127.0.0.1 --port 8090
```

健康检查：

```bash
curl http://127.0.0.1:8090/health
```

兼容检索：

```bash
curl -X POST http://127.0.0.1:8090/api/v1/retrieval/search \
  -H 'Content-Type: application/json' \
  --data @examples/http/retrieval_request.json
```

扩展检索：

```bash
curl -X POST 'http://127.0.0.1:8090/api/v1/retrieval/search:extended' \
  -H 'Content-Type: application/json' \
  --data @examples/http/retrieval_request.json
```
