-- PostgreSQL V6 baseline. 正式开发应通过迁移工具维护。
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE organizations (
    organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_name VARCHAR(160) NOT NULL,
    organization_status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    display_name VARCHAR(120) NOT NULL,
    user_status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE learners (
    learner_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    user_id UUID REFERENCES users(user_id),
    learner_status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_learners_org ON learners(organization_id);

CREATE TABLE knowledge_bases (
    knowledge_base_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    knowledge_base_name VARCHAR(160) NOT NULL,
    description TEXT,
    knowledge_base_status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_knowledge_bases_org ON knowledge_bases(organization_id);

CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(knowledge_base_id),
    file_name TEXT NOT NULL,
    storage_key TEXT NOT NULL,
    content_sha256 VARCHAR(64),
    document_status VARCHAR(32) NOT NULL DEFAULT 'uploaded',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE build_runs (
    build_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(knowledge_base_id),
    build_status VARCHAR(32) NOT NULL DEFAULT 'queued',
    build_mode VARCHAR(32) NOT NULL DEFAULT 'full',
    idempotency_key VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    UNIQUE (organization_id, idempotency_key)
);

CREATE TABLE knowledge_base_versions (
    knowledge_base_version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(knowledge_base_id),
    build_run_id UUID NOT NULL REFERENCES build_runs(build_run_id),
    version_no INTEGER NOT NULL,
    version_status VARCHAR(32) NOT NULL DEFAULT 'draft',
    index_reference_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ,
    UNIQUE (knowledge_base_id, version_no)
);

CREATE TABLE training_programs (
    training_program_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(knowledge_base_id),
    knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_base_versions(knowledge_base_version_id),
    program_name VARCHAR(200) NOT NULL,
    program_status VARCHAR(32) NOT NULL DEFAULT 'draft',
    program_target_node_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE learner_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    training_program_id UUID NOT NULL REFERENCES training_programs(training_program_id),
    learner_id UUID NOT NULL REFERENCES learners(learner_id),
    assignment_status VARCHAR(32) NOT NULL DEFAULT 'assigned',
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE learner_profile_snapshots (
    profile_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    learner_id UUID NOT NULL REFERENCES learners(learner_id),
    profile_version_no INTEGER NOT NULL,
    mastery_items JSONB NOT NULL DEFAULT '[]'::jsonb,
    learning_preference_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    derived_from_decision_cycle_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, learner_id, profile_version_no)
);

CREATE TABLE learning_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    learner_id UUID NOT NULL REFERENCES learners(learner_id),
    assignment_id UUID NOT NULL REFERENCES learner_assignments(assignment_id),
    knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_base_versions(knowledge_base_version_id),
    profile_snapshot_id UUID NOT NULL REFERENCES learner_profile_snapshots(profile_snapshot_id),
    session_status VARCHAR(32) NOT NULL DEFAULT 'active',
    correlation_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE decision_cycles (
    decision_cycle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
    cycle_no INTEGER NOT NULL,
    decision_cycle_status VARCHAR(32) NOT NULL DEFAULT 'running',
    correlation_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    UNIQUE (session_id, cycle_no)
);

CREATE TABLE agent_runs (
    agent_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
    decision_cycle_id UUID NOT NULL REFERENCES decision_cycles(decision_cycle_id),
    agent_name VARCHAR(64) NOT NULL,
    agent_run_status VARCHAR(32) NOT NULL DEFAULT 'queued',
    correlation_id UUID NOT NULL,
    causation_id UUID,
    input_payload JSONB NOT NULL,
    output_payload JSONB,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

CREATE TABLE agent_proposals (
    proposal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    agent_run_id UUID NOT NULL REFERENCES agent_runs(agent_run_id),
    decision_cycle_id UUID NOT NULL REFERENCES decision_cycles(decision_cycle_id),
    proposal_type VARCHAR(64) NOT NULL,
    proposal_status VARCHAR(32) NOT NULL DEFAULT 'generated',
    payload JSONB NOT NULL,
    confidence NUMERIC(5,4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE proposal_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    reviewed_proposal_id UUID NOT NULL REFERENCES agent_proposals(proposal_id),
    review_result VARCHAR(32) NOT NULL,
    repair_action VARCHAR(64) NOT NULL,
    review_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE final_decisions (
    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
    decision_cycle_id UUID NOT NULL REFERENCES decision_cycles(decision_cycle_id),
    decision_type VARCHAR(64) NOT NULL,
    selected_proposal_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    supporting_evidence_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    decision_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE learning_resources (
    resource_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
    decision_cycle_id UUID NOT NULL REFERENCES decision_cycles(decision_cycle_id),
    proposal_id UUID NOT NULL REFERENCES agent_proposals(proposal_id),
    resource_payload JSONB NOT NULL,
    review_status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE assessments (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
    decision_cycle_id UUID NOT NULL REFERENCES decision_cycles(decision_cycle_id),
    proposal_id UUID NOT NULL REFERENCES agent_proposals(proposal_id),
    assessment_payload JSONB NOT NULL,
    review_status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE assessment_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    assessment_id UUID NOT NULL REFERENCES assessments(assessment_id),
    learner_id UUID NOT NULL REFERENCES learners(learner_id),
    attempt_status VARCHAR(32) NOT NULL DEFAULT 'submitted',
    answers JSONB NOT NULL,
    score_ratio NUMERIC(5,4),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    scored_at TIMESTAMPTZ
);

CREATE TABLE evidence_items (
    evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_base_versions(knowledge_base_version_id),
    document_id UUID NOT NULL REFERENCES documents(document_id),
    chunk_id UUID NOT NULL,
    content_excerpt TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE human_review_tasks (
    human_review_task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
    decision_cycle_id UUID NOT NULL REFERENCES decision_cycles(decision_cycle_id),
    reference_id UUID NOT NULL,
    task_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    resolution_code VARCHAR(32),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);
