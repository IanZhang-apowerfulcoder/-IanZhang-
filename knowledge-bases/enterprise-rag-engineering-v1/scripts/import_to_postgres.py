from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Domain Pack into the project PostgreSQL database")
    parser.add_argument("--dsn", help="PostgreSQL DSN, for example postgresql://user:pass@localhost:5432/app; dry-run时可省略")
    parser.add_argument("--organization-id", required=False)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    domain = json.loads((BASE / "data/domain.json").read_text(encoding="utf-8"))
    nodes = json.loads((BASE / "data/knowledge_nodes.json").read_text(encoding="utf-8"))
    edges = json.loads((BASE / "data/knowledge_edges.json").read_text(encoding="utf-8"))
    chunks = [json.loads(x) for x in (BASE / "data/rag_chunks.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    if args.dry_run:
        print(json.dumps({"domain":domain["slug"],"nodes":len(nodes),"edges":len(edges),"chunks":len(chunks)},ensure_ascii=False,indent=2))
        return 0
    if not args.dsn:
        raise SystemExit("--dsn is required unless --dry-run is used")
    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("Install psycopg[binary] before importing") from exc
    org_id = args.organization_id or domain["organization_id"]
    with psycopg.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            migration = (BASE / "db/migrations/001_domain_pack_extension.sql").read_text(encoding="utf-8")
            cur.execute(migration)
            cur.execute("""INSERT INTO domain_pack_imports(domain_pack_id,organization_id,knowledge_base_id,knowledge_base_version_id,pack_slug,pack_version,manifest)
                VALUES(%s,%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT(domain_pack_id) DO UPDATE SET manifest=EXCLUDED.manifest, imported_at=now()""",
                (domain["domain_pack_id"],org_id,domain["knowledge_base_id"],domain["knowledge_base_version_id"],domain["slug"],domain["version"],json.dumps(domain,ensure_ascii=False)))
            for n in nodes:
                cur.execute("""INSERT INTO knowledge_nodes_ext(knowledge_base_version_id,knowledge_node_id,module_id,node_name,difficulty_level,is_core,node_payload)
                    VALUES(%s,%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT(knowledge_base_version_id,knowledge_node_id) DO UPDATE SET node_payload=EXCLUDED.node_payload,node_name=EXCLUDED.node_name""",
                    (domain["knowledge_base_version_id"],n["id"],n["module_id"],n["name"],n["difficulty"],n["core"],json.dumps(n,ensure_ascii=False)))
            for e in edges:
                cur.execute("""INSERT INTO knowledge_edges_ext(edge_id,knowledge_base_version_id,source_knowledge_node_id,target_knowledge_node_id,relation_type,edge_payload)
                    VALUES(%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT(edge_id) DO UPDATE SET edge_payload=EXCLUDED.edge_payload""",
                    (e["edge_id"],domain["knowledge_base_version_id"],e["source_knowledge_node_id"],e["target_knowledge_node_id"],e["relation_type"],json.dumps(e,ensure_ascii=False)))
            for c in chunks:
                cur.execute("""INSERT INTO knowledge_chunks_ext(chunk_id,evidence_id,knowledge_base_version_id,document_id,knowledge_node_id,title,content,difficulty_level,is_core,metadata)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb) ON CONFLICT(chunk_id) DO UPDATE SET content=EXCLUDED.content,metadata=EXCLUDED.metadata""",
                    (c["chunk_id"],c["evidence_id"],c["knowledge_base_version_id"],c["document_id"],c["knowledge_node_id"],c["title"],c["content"],c["difficulty_level"],c["is_core"],json.dumps(c,ensure_ascii=False)))
        conn.commit()
    print("import completed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
