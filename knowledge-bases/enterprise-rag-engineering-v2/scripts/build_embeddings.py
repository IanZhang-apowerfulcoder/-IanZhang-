from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate embeddings with an explicitly selected provider/model")
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--dimension", type=int, required=True)
    parser.add_argument("--provider", choices=["sentence-transformers","openai-compatible"], required=True)
    args = parser.parse_args()
    manifest_path = BASE / "indexes/embedding_manifest.json"
    if args.provider == "sentence-transformers":
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise SystemExit("Install sentence-transformers for this provider") from exc
        model = SentenceTransformer(args.model_id)
        chunks = [json.loads(x) for x in (BASE / "data/rag_chunks.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        vectors = model.encode([c["content"] for c in chunks], normalize_embeddings=True).tolist()
        out = [{"chunk_id":c["chunk_id"],"embedding":v} for c,v in zip(chunks,vectors)]
        (BASE / "indexes/embeddings.jsonl").write_text("\n".join(json.dumps(x,separators=(",",":")) for x in out)+"\n",encoding="utf-8")
    else:
        raise SystemExit("OpenAI-compatible provider is intentionally left as an adapter: implement it using your chosen API and secret management; do not commit API keys.")
    manifest = {"status":"generated","provider":args.provider,"model_id":args.model_id,"dimension":args.dimension,"normalized":True,"distance":"cosine"}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
