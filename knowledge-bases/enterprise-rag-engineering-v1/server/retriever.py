from __future__ import annotations

import json
import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[1]


def tokenize(text: str) -> list[str]:
    text = text.lower()
    english = re.findall(r"[a-z0-9_+#.-]+", text)
    chinese = "".join(re.findall(r"[\u4e00-\u9fff]", text))
    chars = list(chinese)
    bigrams = ["".join(chars[i:i+2]) for i in range(max(0, len(chars)-1))]
    return english + chars + bigrams


class DomainRetriever:
    """可立即运行的BM25+元数据基线。生产环境可在保持返回契约不变的前提下替换为混合检索。"""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base = base_dir or BASE
        self.domain = json.loads((self.base / "data/domain.json").read_text(encoding="utf-8"))
        self.nodes = json.loads((self.base / "data/knowledge_nodes.json").read_text(encoding="utf-8"))
        self.node_map = {n["id"]: n for n in self.nodes}
        self.chunks = [json.loads(line) for line in (self.base / "data/rag_chunks.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.evidence_map = {c["evidence_id"]: c for c in self.chunks}
        self.docs = []
        self.df: Counter[str] = Counter()
        self.avgdl = 0.0
        for c in self.chunks:
            node = self.node_map[c["knowledge_node_id"]]
            misconception_text = " ".join(m["wrong"] + " " + m["correction"] for m in node.get("misconceptions", []))
            text = " ".join([c["title"], c["content"], node.get("summary", ""), misconception_text, " ".join(node.get("objectives", [])), " ".join(node.get("boundaries", [])), " ".join(c.get("aliases", [])), " ".join(c.get("tags", []))])
            tokens = tokenize(text)
            counts = Counter(tokens)
            self.docs.append((c, counts, len(tokens)))
            self.df.update(counts.keys())
        self.avgdl = sum(d[2] for d in self.docs) / max(1, len(self.docs))

    def _allowed(self, chunk: dict[str, Any], filters: dict[str, Any]) -> bool:
        if not filters:
            return True
        if filters.get("module_id") and chunk["module_id"] != filters["module_id"]:
            return False
        if filters.get("knowledge_node_ids") and chunk["knowledge_node_id"] not in filters["knowledge_node_ids"]:
            return False
        if filters.get("max_difficulty_level") and chunk["difficulty_level"] > int(filters["max_difficulty_level"]):
            return False
        if filters.get("is_core") is not None and chunk["is_core"] != bool(filters["is_core"]):
            return False
        if filters.get("language") and chunk["language"] != filters["language"]:
            return False
        if filters.get("source_tier") and chunk["source_tier"] not in set(filters["source_tier"]):
            return False
        return True

    def search(self, query: str, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        q_tokens = tokenize(query)
        q_counts = Counter(q_tokens)
        n_docs = len(self.docs)
        k1, b = 1.5, 0.75
        results = []
        query_lower = query.lower()
        for chunk, tf, dl in self.docs:
            if not self._allowed(chunk, filters):
                continue
            score = 0.0
            for term, qf in q_counts.items():
                freq = tf.get(term, 0)
                if not freq:
                    continue
                df = self.df.get(term, 0)
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                denom = freq + k1 * (1 - b + b * dl / max(self.avgdl, 1))
                score += idf * (freq * (k1 + 1) / denom) * min(qf, 2)
            node = self.node_map[chunk["knowledge_node_id"]]
            exact_terms = [node["name"], *node.get("aliases", [])]
            if any(t.lower() in query_lower for t in exact_terms if t):
                score += 8.0
            if chunk["title"].split("：")[-1].lower() in query_lower:
                score += 3.0
            if chunk["is_core"]:
                score += 0.15
            score += float(chunk.get("importance_score", 0.8)) * 0.1
            if score > 0:
                results.append((score, chunk))
        results.sort(key=lambda x: (-x[0], x[1]["chunk_id"]))
        top = results[:top_k]
        max_score = top[0][0] if top else 1.0
        return [{
            "evidence_id": c["evidence_id"],
            "chunk_id": c["chunk_id"],
            "document_id": c["document_id"],
            "knowledge_node_id": c["knowledge_node_id"],
            "content_excerpt": c["content_excerpt"],
            "relevance_score": round(min(1.0, max(0.0, s / max_score)), 6),
            "rank_no": i,
            "citation_text": c["citation_text"],
            "source_ids": c["source_ids"],
            "difficulty_level": c["difficulty_level"]
        } for i, (s, c) in enumerate(top, 1)]

    def compatible_response(self, request: dict[str, Any]) -> dict[str, Any]:
        if request["knowledge_base_version_id"] != self.domain["knowledge_base_version_id"]:
            raise ValueError("knowledge_base_version_id is not active for this Domain Pack")
        hits = self.search(request["query_text"], int(request["top_k"]), request.get("filters") or {})
        return {
            "retrieval_request_id": request["retrieval_request_id"],
            "evidence_items": [{k: h[k] for k in ["evidence_id","chunk_id","document_id","content_excerpt","relevance_score"]} for h in hits]
        }
