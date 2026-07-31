type RetrievalRequest = {
  retrieval_request_id: string;
  knowledge_base_version_id: string;
  query_text: string;
  top_k: number;
  filters: Record<string, unknown>;
};

const body: RetrievalRequest = {
  retrieval_request_id: "b8c16593-d680-5c5d-aa29-16a1a071b2db",
  knowledge_base_version_id: "fd400183-2242-50aa-8b83-d670c1ce5a1f",
  query_text: "RAG 与微调的边界和选择依据是什么？",
  top_k: 5,
  filters: { max_difficulty_level: 3, core_only: true },
};

const response = await fetch("http://127.0.0.1:8090/api/v1/retrieval/search", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify(body),
});
if (!response.ok) throw new Error(`retrieval failed: ${response.status}`);
console.log(JSON.stringify(await response.json(), null, 2));
