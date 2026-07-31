from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server.retriever import BASE, DomainRetriever


def evaluate(write_files: bool = True):
    retriever = DomainRetriever(BASE)
    cases = json.loads((BASE / "data/retrieval_eval_cases.json").read_text(encoding="utf-8"))
    hit1 = hit5 = 0
    rr_sum = 0.0
    case_results = []
    for case in cases:
        hits = retriever.search(case["query_text"], max(5, case["top_k"]), case.get("filters") or {})
        ranked = [h["knowledge_node_id"] for h in hits]
        expected = set(case["expected_knowledge_node_ids"])
        first_rank = next((i for i,nid in enumerate(ranked,1) if nid in expected), None)
        if first_rank == 1: hit1 += 1
        if first_rank is not None and first_rank <= 5: hit5 += 1
        if first_rank: rr_sum += 1.0 / first_rank
        case_results.append({"test_case_id":case["test_case_id"],"passed":bool(first_rank and first_rank<=5),"first_relevant_rank":first_rank,"ranked_node_ids":ranked})
    total = len(cases)
    report = {
        "evaluator":"bm25_char_ngram_metadata_baseline",
        "knowledge_base_version_id":retriever.domain["knowledge_base_version_id"],
        "case_count":total,
        "hit_rate_at_1":round(hit1/total,4),
        "hit_rate_at_5":round(hit5/total,4),
        "mean_reciprocal_rank":round(rr_sum/total,4),
        "target_hit_rate_at_5":retriever.domain["quality_targets"]["retrieval_hit_rate_at_5"],
        "target_met":hit5/total >= retriever.domain["quality_targets"]["retrieval_hit_rate_at_5"],
        "limitations":"词法+元数据基线；不代表稠密向量、重排器或真实生成模型的最终质量。",
        "case_results":case_results
    }
    if write_files:
        (BASE / "reports/retrieval_baseline_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        md = ["# 检索基线报告","",f"- 案例数：{total}",f"- Hit@1：{report['hit_rate_at_1']:.2%}",f"- Hit@5：{report['hit_rate_at_5']:.2%}",f"- MRR：{report['mean_reciprocal_rank']:.4f}",f"- 目标是否达到：{'是' if report['target_met'] else '否'}","","> 此结果仅代表本地词法+元数据基线，不替代生产向量与重排评测。"]
        (BASE / "reports/retrieval_baseline_report.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    return report

if __name__ == "__main__":
    print(json.dumps(evaluate(),ensure_ascii=False,indent=2))
