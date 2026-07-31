-- Extension tables for Enterprise RAG Engineering Domain Pack v1.0
-- Apply after the existing V6 database/schema.sql.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS domain_pack_imports (
    domain_pack_id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    knowledge_base_id UUID NOT NULL,
    knowledge_base_version_id UUID NOT NULL,
    pack_slug VARCHAR(160) NOT NULL,
    pack_version VARCHAR(32) NOT NULL,
    manifest JSONB NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_nodes_ext (
    knowledge_base_version_id UUID NOT NULL,
    knowledge_node_id VARCHAR(64) NOT NULL,
    module_id VARCHAR(32) NOT NULL,
    node_name VARCHAR(240) NOT NULL,
    difficulty_level INTEGER NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
    is_core BOOLEAN NOT NULL,
    node_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (knowledge_base_version_id, knowledge_node_id)
);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_ext_module ON knowledge_nodes_ext(knowledge_base_version_id, module_id);

CREATE TABLE IF NOT EXISTS knowledge_edges_ext (
    edge_id UUID PRIMARY KEY,
    knowledge_base_version_id UUID NOT NULL,
    source_knowledge_node_id VARCHAR(64) NOT NULL,
    target_knowledge_node_id VARCHAR(64) NOT NULL,
    relation_type VARCHAR(64) NOT NULL,
    edge_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_ext_source ON knowledge_edges_ext(knowledge_base_version_id, source_knowledge_node_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_ext_target ON knowledge_edges_ext(knowledge_base_version_id, target_knowledge_node_id);

CREATE TABLE IF NOT EXISTS knowledge_chunks_ext (
    chunk_id UUID PRIMARY KEY,
    evidence_id UUID NOT NULL UNIQUE,
    knowledge_base_version_id UUID NOT NULL,
    document_id UUID NOT NULL,
    knowledge_node_id VARCHAR(64) NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
    is_core BOOLEAN NOT NULL,
    embedding vector,
    embedding_model_id TEXT,
    metadata JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_ext_node ON knowledge_chunks_ext(knowledge_base_version_id, knowledge_node_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_ext_metadata ON knowledge_chunks_ext USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_ext_fts ON knowledge_chunks_ext USING gin(to_tsvector('simple', title || ' ' || content));

CREATE TABLE IF NOT EXISTS knowledge_questions_ext (
    question_id UUID PRIMARY KEY,
    knowledge_base_version_id UUID NOT NULL,
    knowledge_node_id VARCHAR(64) NOT NULL,
    difficulty_level INTEGER NOT NULL CHECK (difficulty_level BETWEEN 1 AND 5),
    question_type VARCHAR(32) NOT NULL,
    question_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_tasks_ext (
    task_id UUID PRIMARY KEY,
    knowledge_base_version_id UUID NOT NULL,
    knowledge_node_id VARCHAR(64) NOT NULL,
    rubric_id UUID NOT NULL,
    task_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_rubrics_ext (
    rubric_id UUID PRIMARY KEY,
    knowledge_base_version_id UUID NOT NULL,
    task_id UUID NOT NULL,
    rubric_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS retrieval_eval_cases_ext (
    test_case_id VARCHAR(96) PRIMARY KEY,
    knowledge_base_version_id UUID NOT NULL,
    query_text TEXT NOT NULL,
    expected_knowledge_node_ids JSONB NOT NULL,
    case_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS generation_eval_cases_ext (
    test_case_id VARCHAR(96) PRIMARY KEY,
    knowledge_base_version_id UUID NOT NULL,
    knowledge_node_id VARCHAR(64) NOT NULL,
    case_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
