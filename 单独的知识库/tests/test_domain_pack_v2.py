from pathlib import Path
import json

from server.retriever import DomainRetriever
from server.router import analyze_query
from server.adaptive_retriever import AdaptiveRetriever

BASE = Path(__file__).resolve().parents[1]

def test_unified_counts():
    d = json.loads((BASE/'data/domain.json').read_text(encoding='utf-8'))
    assert d['version'] == '2.0.0'
    assert d['counts']['knowledge_nodes'] >= 90
    assert d['counts']['rag_chunks'] >= 350


def test_all_chunks_reference_nodes():
    nodes = {x['id'] for x in json.loads((BASE/'data/knowledge_nodes.json').read_text(encoding='utf-8'))}
    chunks = [json.loads(x) for x in (BASE/'data/rag_chunks.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    assert all(c['knowledge_node_id'] in nodes for c in chunks)
    assert all(c.get('runtime_enabled') is True for c in chunks)


def test_router_simple_and_complex():
    simple = analyze_query('Embedding是什么？')
    assert simple.execution_mode == 'sequential'
    complex_q = analyze_query('为什么RAG召回率很高但答案仍然错误，应该如何排查？')
    assert complex_q.execution_mode == 'agentic'
    assert 'hybrid' in complex_q.selected_strategies


def test_adaptive_search_returns_trace():
    retriever = DomainRetriever(BASE)
    result = AdaptiveRetriever(retriever).run('RAG的前置知识和学习路径是什么？', 5, {'max_difficulty_level': 5})
    assert result['query_analysis']['execution_mode'] in {'parallel','agentic'}
    assert result['retrieval_steps']
    assert result['evidence_items']
