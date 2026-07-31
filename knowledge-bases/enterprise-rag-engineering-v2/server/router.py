from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class QueryAnalysis:
    query_type: str
    complexity: str
    risk_level: str
    selected_strategies: list[str]
    execution_mode: str
    reason_summary: str
    max_steps: int = 5
    max_retries: int = 2

RELATION_TERMS = ("前置", "依赖", "关系", "路径", "因果", "为什么先", "影响")
LONG_DOC_TERMS = ("章节", "长文档", "全文", "上下文", "多粒度")
COMPLEX_TERMS = ("为什么", "排查", "诊断", "比较", "权衡", "方案", "如何设计", "多个")
HIGH_RISK_TERMS = ("安全", "合规", "隐私", "越权", "生产", "发布")

def analyze_query(query: str, requested_filters: dict[str, Any] | None = None) -> QueryAnalysis:
    q = query.strip()
    filters = requested_filters or {}
    relation = any(x in q for x in RELATION_TERMS)
    long_doc = any(x in q for x in LONG_DOC_TERMS)
    complex_q = sum(1 for x in COMPLEX_TERMS if x in q) >= 1 or len(re.split(r"[，。；？！]", q)) >= 4
    risk = "high" if any(x in q for x in HIGH_RISK_TERMS) else "medium" if complex_q else "low"
    if complex_q:
        qtype = "complex_troubleshooting" if any(x in q for x in ("排查", "为什么", "错误", "不准确")) else "multi_component"
        strategies = ["metadata_filtered", "hybrid"]
        if relation:
            strategies.append("graph_assisted")
        elif long_doc:
            strategies.append("parent_child")
        mode = "agentic"
        reason = "问题包含多个分析维度，需要多策略检索并在证据不足时进行受限补检索。"
    elif relation:
        qtype, strategies, mode = "relation_or_path", ["metadata_filtered", "graph_assisted", "hybrid"], "parallel"
        reason = "问题涉及知识依赖或路径关系，需要图关系扩展并由混合检索补充文本证据。"
    elif long_doc:
        qtype, strategies, mode = "long_context", ["metadata_filtered", "parent_child", "hybrid"], "parallel"
        reason = "问题依赖章节上下文，需要父子层级扩展并保留局部证据。"
    else:
        qtype, strategies, mode = "single_topic", ["metadata_filtered", "hybrid"], "sequential"
        reason = "问题属于单知识点或普通事实查询，稳定混合检索即可满足。"
    return QueryAnalysis(qtype, "high" if complex_q else "medium" if relation or long_doc else "low", risk, strategies[:3], mode, reason)

def plan_dict(query: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    return asdict(analyze_query(query, filters))
