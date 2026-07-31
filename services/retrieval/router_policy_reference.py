from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class RouteDecision:
    query_type: str
    execution_mode: str
    strategies: tuple[str, ...]
    reason_summary: str

def route(query: str) -> RouteDecision:
    relation_terms=("前置","依赖","路径","因果","关系")
    long_terms=("章节","长文档","全文","多粒度")
    complex_terms=("为什么","排查","诊断","权衡","比较","如何设计")
    if any(x in query for x in complex_terms):
        strategies=["metadata_filtered","hybrid"]
        if any(x in query for x in relation_terms): strategies.append("graph_assisted")
        elif any(x in query for x in long_terms): strategies.append("parent_child")
        return RouteDecision("complex_troubleshooting","agentic",tuple(strategies[:3]),"复杂问题使用有限多策略和补检索。")
    if any(x in query for x in relation_terms):
        return RouteDecision("relation_or_path","parallel",("metadata_filtered","graph_assisted","hybrid"),"关系问题需要图扩展与文本证据。")
    if any(x in query for x in long_terms):
        return RouteDecision("long_context","parallel",("metadata_filtered","parent_child","hybrid"),"长上下文问题需要父子检索。")
    return RouteDecision("single_topic","sequential",("metadata_filtered","hybrid"),"单知识点使用稳定混合检索。")
