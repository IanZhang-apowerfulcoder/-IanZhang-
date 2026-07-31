from pathlib import Path
import json, hashlib, sys
import jsonschema
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/"importable_package")
schemas=Path(__file__).resolve().parents[1]/"schemas"
files={"manifest.json":"manifest.schema.json","sources.json":"sources.schema.json","knowledge_nodes.json":"knowledge_nodes.schema.json","knowledge_edges.json":"knowledge_edges.schema.json","rag_chunks.json":"rag_chunks.schema.json","practical_tasks.json":"practical_tasks.schema.json","question_bank.json":"question_bank.schema.json","evaluation_cases.json":"evaluation_cases.schema.json"}
errors=[]
for fn,sn in files.items():
    try:
        obj=json.loads((root/fn).read_text(encoding="utf-8")); schema=json.loads((schemas/sn).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(obj)
    except Exception as e: errors.append(f"{fn}: {e}")
manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
for item in manifest["files"]:
    p=root/item["file_name"]; h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=item["sha256"]: errors.append(f"hash mismatch: {p.name}")
print("PASS" if not errors else "FAIL")
for e in errors: print("-",e)
sys.exit(1 if errors else 0)
