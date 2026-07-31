from __future__ import annotations

from collections import defaultdict
from typing import Any

from .router import plan_dict

class AdaptiveRetriever:
    def __init__(self, retriever: Any) -> None:
        self.retriever = retriever
        self.edges = getattr(retriever, "edges", [])
        self.neighbors: dict[str, set[str]] = defaultdict(set)
        for e in self.edges:
            s = e["source_knowledge_node_id"]
            t = e["target_knowledge_node_id"]
            self.neighbors[s].add(t)
            self.neighbors[t].add(s)

    def _graph_expand(self, hits: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        node_ids = {x["knowledge_node_id"] for x in hits[:max(1, top_k // 2)]}
        expanded = set(node_ids)
        for node_id in list(node_ids):
            expanded.update(self.neighbors.get(node_id, set()))
        return self.retriever.search(" ".join(self.retriever.node_map[n]["name"] for n in expanded if n in self.retriever.node_map), top_k, {"knowledge_node_ids": list(expanded)})

    def _parent_child(self, hits: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        expanded = set()
        for hit in hits[:max(1, top_k // 2)]:
            node = self.retriever.node_map.get(hit["knowledge_node_id"], {})
            expanded.add(hit["knowledge_node_id"])
            parent = node.get("parent_node_id")
            if parent:
                expanded.add(parent)
            for n in self.retriever.nodes:
                if n.get("parent_node_id") == hit["knowledge_node_id"]:
                    expanded.add(n["id"])
        return self.retriever.search(" ".join(self.retriever.node_map[n]["name"] for n in expanded if n in self.retriever.node_map), top_k, {"knowledge_node_ids": list(expanded)})

    @staticmethod
    def _fuse(results: list[tuple[str, list[dict[str, Any]]]], top_k: int) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}
        for strategy, hits in results:
            for rank, hit in enumerate(hits, 1):
                key = hit["evidence_id"]
                row = merged.setdefault(key, dict(hit, strategy_contributions=[], fused_score=0.0))
                row["strategy_contributions"].append({"strategy": strategy, "rank": rank})
                row["fused_score"] += 1.0 / (60 + rank)
        return sorted(merged.values(), key=lambda x: x["fused_score"], reverse=True)[:top_k]

    def run(self, query: str, top_k: int = 8, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        filters = dict(filters or {})
        plan = plan_dict(query, filters)
        results: list[tuple[str, list[dict[str, Any]]]] = []
        base = self.retriever.search(query, max(top_k, 10), filters)
        for strategy in plan["selected_strategies"]:
            if strategy == "metadata_filtered":
                results.append((strategy, base))
            elif strategy == "hybrid":
                results.append((strategy, base))
            elif strategy == "graph_assisted":
                results.append((strategy, self._graph_expand(base, max(top_k, 10))))
            elif strategy == "parent_child":
                results.append((strategy, self._parent_child(base, max(top_k, 10))))
        fused = self._fuse(results, top_k)
        sufficient = len(fused) >= min(3, top_k) and any(x.get("relevance_score", 0) > 0 for x in fused)
        return {
            "query_analysis": plan,
            "retrieval_steps": [{"strategy": s, "hit_count": len(h)} for s, h in results],
            "evidence_sufficiency": {"sufficient": sufficient, "reason": "已取得多来源证据" if sufficient else "证据数量或相关性不足"},
            "evidence_items": fused,
        }
