"""兼容入口。

正式业务模型应由 api/openapi.yaml 和 contracts/jsonschema 自动生成。
当前文件仅暴露冻结字段集合，禁止在这里手工创建另一套跨模块字段。
"""

from .frozen_fields import FROZEN_FIELD_NAMES

__all__ = ["FROZEN_FIELD_NAMES"]
