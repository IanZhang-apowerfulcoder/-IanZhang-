-- Challenge Cup adaptive parallel RAG v7.0 PostgreSQL baseline.
-- 正式开发通过迁移工具维护；Agent 不得直接写权威业务表。
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE organizations (
  organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_name VARCHAR(160) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(320) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  display_name VARCHAR(120) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE organization_members (
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  user_id UUID NOT NULL REFERENCES users(user_id),
  role_code VARCHAR(32) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (organization_id,user_id)
);
CREATE TABLE learners (
  learner_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  user_id UUID REFERENCES users(user_id),
  background JSONB NOT NULL DEFAULT '{}'::jsonb,
  learning_goals JSONB NOT NULL DEFAULT '[]'::jsonb,
  preferences JSONB NOT NULL DEFAULT '[]'::jsonb,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_learners_org ON learners(organization_id);

CREATE TABLE knowledge_bases (
  knowledge_base_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  name VARCHAR(200) NOT NULL,
  description TEXT,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  active_version_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE knowledge_versions (
  knowledge_base_version_id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(knowledge_base_id),
  version_label VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  parent_version_id UUID REFERENCES knowledge_versions(knowledge_base_version_id),
  manifest_sha256 VARCHAR(64),
  counts JSONB NOT NULL DEFAULT '{}'::jsonb,
  quality_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_by UUID REFERENCES users(user_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ,
  activated_at TIMESTAMPTZ,
  UNIQUE(knowledge_base_id,version_label)
);
ALTER TABLE knowledge_bases ADD CONSTRAINT fk_active_kb_version FOREIGN KEY(active_version_id) REFERENCES knowledge_versions(knowledge_base_version_id);
CREATE TABLE knowledge_sources (
  source_id VARCHAR(160) NOT NULL,
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  title TEXT NOT NULL,
  organization TEXT,
  source_type VARCHAR(64) NOT NULL,
  authority_tier VARCHAR(16),
  url TEXT,
  local_reference TEXT,
  trust_tier VARCHAR(64) NOT NULL,
  review_status VARCHAR(32) NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY(knowledge_base_version_id,source_id)
);
CREATE TABLE knowledge_nodes (
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  knowledge_node_id VARCHAR(160) NOT NULL,
  parent_node_id VARCHAR(160),
  module_id VARCHAR(64) NOT NULL,
  name TEXT NOT NULL,
  difficulty_level SMALLINT NOT NULL CHECK(difficulty_level BETWEEN 1 AND 5),
  is_core BOOLEAN NOT NULL DEFAULT false,
  summary TEXT NOT NULL,
  payload JSONB NOT NULL,
  PRIMARY KEY(knowledge_base_version_id,knowledge_node_id)
);
CREATE TABLE knowledge_edges (
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  edge_id UUID NOT NULL,
  source_knowledge_node_id VARCHAR(160) NOT NULL,
  target_knowledge_node_id VARCHAR(160) NOT NULL,
  relation_type VARCHAR(64) NOT NULL,
  reason TEXT,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY(knowledge_base_version_id,edge_id)
);
CREATE TABLE knowledge_chunks (
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  chunk_id VARCHAR(160) NOT NULL,
  evidence_id UUID NOT NULL,
  knowledge_node_id VARCHAR(160) NOT NULL,
  document_id VARCHAR(160),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  citation_text TEXT NOT NULL,
  difficulty_level SMALLINT NOT NULL,
  content_status VARCHAR(64) NOT NULL,
  review_status VARCHAR(64),
  runtime_enabled BOOLEAN NOT NULL DEFAULT true,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding vector,
  embedding_model_id VARCHAR(200),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(knowledge_base_version_id,chunk_id),
  UNIQUE(knowledge_base_version_id,evidence_id)
);
CREATE INDEX idx_chunks_node ON knowledge_chunks(knowledge_base_version_id,knowledge_node_id);
CREATE INDEX idx_chunks_metadata ON knowledge_chunks USING gin(metadata);
CREATE TABLE knowledge_questions (
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  question_id VARCHAR(160) NOT NULL,
  knowledge_node_id VARCHAR(160) NOT NULL,
  payload JSONB NOT NULL,
  review_status VARCHAR(32) NOT NULL,
  PRIMARY KEY(knowledge_base_version_id,question_id)
);
CREATE TABLE knowledge_tasks (
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  task_id VARCHAR(160) NOT NULL,
  knowledge_node_id VARCHAR(160) NOT NULL,
  payload JSONB NOT NULL,
  review_status VARCHAR(32) NOT NULL,
  PRIMARY KEY(knowledge_base_version_id,task_id)
);
CREATE TABLE knowledge_rubrics (
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  rubric_id VARCHAR(160) NOT NULL,
  payload JSONB NOT NULL,
  PRIMARY KEY(knowledge_base_version_id,rubric_id)
);
CREATE TABLE knowledge_import_runs (
  import_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(knowledge_base_id),
  base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  candidate_version_id UUID REFERENCES knowledge_versions(knowledge_base_version_id),
  import_format VARCHAR(32) NOT NULL,
  storage_reference TEXT NOT NULL,
  dry_run BOOLEAN NOT NULL,
  conflict_policy VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  diff_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  conflicts JSONB NOT NULL DEFAULT '[]'::jsonb,
  requested_by UUID REFERENCES users(user_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);
CREATE TABLE knowledge_review_items (
  review_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  reference_type VARCHAR(32) NOT NULL,
  reference_id VARCHAR(160) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  priority VARCHAR(16) NOT NULL DEFAULT 'P1',
  payload JSONB NOT NULL,
  reviewer_id UUID REFERENCES users(user_id),
  decision VARCHAR(32),
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  reviewed_at TIMESTAMPTZ
);
CREATE TABLE knowledge_index_runs (
  index_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  index_type VARCHAR(64) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  config JSONB NOT NULL,
  metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE learner_profile_snapshots (
  profile_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  learner_id UUID NOT NULL REFERENCES learners(learner_id),
  version_no INTEGER NOT NULL,
  background_snapshot JSONB NOT NULL,
  mastery_items JSONB NOT NULL,
  preferences JSONB NOT NULL,
  risk_flags JSONB NOT NULL,
  source_decision_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(learner_id,version_no)
);
CREATE TABLE profile_mastery_events (
  mastery_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learner_id UUID NOT NULL REFERENCES learners(learner_id),
  profile_snapshot_id UUID NOT NULL REFERENCES learner_profile_snapshots(profile_snapshot_id),
  knowledge_node_id VARCHAR(160) NOT NULL,
  old_score NUMERIC(5,4),
  new_score NUMERIC(5,4) NOT NULL,
  confidence NUMERIC(5,4) NOT NULL,
  evidence_refs JSONB NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE learning_sessions (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  learner_id UUID NOT NULL REFERENCES learners(learner_id),
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  profile_snapshot_id UUID NOT NULL REFERENCES learner_profile_snapshots(profile_snapshot_id),
  goal TEXT NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  correlation_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);
CREATE TABLE workflow_runs (
  workflow_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(organization_id),
  session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
  workflow_key VARCHAR(80) NOT NULL,
  workflow_version VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  current_state VARCHAR(80) NOT NULL,
  idempotency_key VARCHAR(160) NOT NULL,
  correlation_id UUID NOT NULL,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  UNIQUE(organization_id,idempotency_key)
);
CREATE TABLE workflow_events (
  event_id UUID PRIMARY KEY,
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
  sequence_no BIGINT NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  status VARCHAR(32),
  agent_run_id UUID,
  retrieval_run_id UUID,
  parallel_group_id UUID,
  payload JSONB NOT NULL,
  correlation_id UUID NOT NULL,
  causation_id UUID,
  created_at TIMESTAMPTZ NOT NULL,
  UNIQUE(workflow_run_id,sequence_no)
);
CREATE INDEX idx_workflow_events_run_seq ON workflow_events(workflow_run_id,sequence_no);
CREATE TABLE workflow_checkpoints (
  checkpoint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  state_name VARCHAR(80) NOT NULL,
  state_payload JSONB NOT NULL,
  sequence_no BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE agent_runs (
  agent_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
  agent_name VARCHAR(100) NOT NULL,
  agent_version VARCHAR(40) NOT NULL,
  prompt_version VARCHAR(80),
  model_id VARCHAR(160),
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  outcome VARCHAR(32),
  input_payload JSONB NOT NULL,
  output_payload JSONB,
  token_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
  latency_ms NUMERIC,
  retry_count INTEGER NOT NULL DEFAULT 0,
  correlation_id UUID NOT NULL,
  causation_id UUID,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);
CREATE TABLE parallel_groups (
  parallel_group_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  group_type VARCHAR(32) NOT NULL,
  minimum_success_count INTEGER NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  aggregation_payload JSONB,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);
CREATE TABLE parallel_group_members (
  parallel_group_id UUID NOT NULL REFERENCES parallel_groups(parallel_group_id),
  agent_run_id UUID NOT NULL REFERENCES agent_runs(agent_run_id),
  branch_name VARCHAR(80) NOT NULL,
  branch_order INTEGER NOT NULL,
  PRIMARY KEY(parallel_group_id,agent_run_id)
);
CREATE TABLE tool_calls (
  tool_call_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_run_id UUID NOT NULL REFERENCES agent_runs(agent_run_id),
  tool_name VARCHAR(100) NOT NULL,
  status VARCHAR(32) NOT NULL,
  request_payload JSONB NOT NULL,
  response_payload JSONB,
  latency_ms NUMERIC,
  error_code VARCHAR(80),
  started_at TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ
);

CREATE TABLE retrieval_runs (
  retrieval_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  retrieval_request_id UUID NOT NULL,
  query_text TEXT NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  current_retry INTEGER NOT NULL DEFAULT 0,
  total_latency_ms NUMERIC,
  correlation_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);
CREATE TABLE retrieval_plans (
  retrieval_plan_id UUID PRIMARY KEY,
  retrieval_run_id UUID NOT NULL REFERENCES retrieval_runs(retrieval_run_id),
  query_analysis JSONB NOT NULL,
  selected_strategies JSONB NOT NULL,
  execution_mode VARCHAR(32) NOT NULL,
  budgets JSONB NOT NULL,
  reason_summary TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE retrieval_steps (
  retrieval_step_id UUID PRIMARY KEY,
  retrieval_plan_id UUID NOT NULL REFERENCES retrieval_plans(retrieval_plan_id),
  sequence_no INTEGER NOT NULL,
  strategy VARCHAR(64) NOT NULL,
  query_text TEXT NOT NULL,
  filters JSONB NOT NULL,
  top_k INTEGER NOT NULL,
  parallel_group_id UUID REFERENCES parallel_groups(parallel_group_id),
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  retry_no INTEGER NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ
);
CREATE TABLE retrieval_strategy_results (
  strategy_result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  retrieval_step_id UUID NOT NULL REFERENCES retrieval_steps(retrieval_step_id),
  status VARCHAR(32) NOT NULL,
  hit_count INTEGER NOT NULL DEFAULT 0,
  result_payload JSONB NOT NULL,
  latency_ms NUMERIC,
  error_code VARCHAR(80),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE retrieval_evidence_links (
  retrieval_run_id UUID NOT NULL REFERENCES retrieval_runs(retrieval_run_id),
  evidence_id UUID NOT NULL,
  knowledge_base_version_id UUID NOT NULL REFERENCES knowledge_versions(knowledge_base_version_id),
  chunk_id VARCHAR(160) NOT NULL,
  knowledge_node_id VARCHAR(160) NOT NULL,
  fused_score NUMERIC NOT NULL,
  rank_no INTEGER NOT NULL,
  strategy_contributions JSONB NOT NULL,
  selected_for_context BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY(retrieval_run_id,evidence_id)
);
CREATE TABLE evidence_sufficiency_results (
  sufficiency_result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  retrieval_run_id UUID NOT NULL REFERENCES retrieval_runs(retrieval_run_id),
  check_no INTEGER NOT NULL,
  sufficient BOOLEAN NOT NULL,
  coverage_score NUMERIC(5,4) NOT NULL,
  quality_score NUMERIC(5,4) NOT NULL,
  conflict_score NUMERIC(5,4) NOT NULL,
  missing_aspects JSONB NOT NULL,
  recommended_action VARCHAR(64) NOT NULL,
  reason_summary TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(retrieval_run_id,check_no)
);

CREATE TABLE agent_proposals (
  proposal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_run_id UUID NOT NULL REFERENCES agent_runs(agent_run_id),
  proposal_type VARCHAR(64) NOT NULL,
  payload JSONB NOT NULL,
  confidence NUMERIC(5,4),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE review_results (
  review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  target_type VARCHAR(32) NOT NULL,
  target_id VARCHAR(160) NOT NULL,
  outcome VARCHAR(32) NOT NULL,
  dimension_results JSONB NOT NULL,
  blocking_issues JSONB NOT NULL,
  repair_instructions JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE final_decisions (
  decision_id UUID PRIMARY KEY,
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
  action_type VARCHAR(64) NOT NULL,
  selected_proposal_ids JSONB NOT NULL,
  rejected_proposal_ids JSONB NOT NULL,
  supporting_evidence_ids JSONB NOT NULL,
  decision_payload JSONB NOT NULL,
  reason_summary TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ux_final_decision_per_workflow_terminal ON final_decisions(workflow_run_id) WHERE action_type IN ('publish_resource','advance','reinforce','remediate','refuse','fail');
CREATE TABLE learning_resources (
  resource_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  resource_version_no INTEGER NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  difficulty_level SMALLINT NOT NULL,
  personalization_reason TEXT NOT NULL,
  payload JSONB NOT NULL,
  evidence_ids JSONB NOT NULL,
  review_id UUID REFERENCES review_results(review_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(session_id,resource_version_no)
);
CREATE TABLE assessments (
  assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES learning_sessions(session_id),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  private_payload JSONB NOT NULL,
  public_payload JSONB NOT NULL,
  review_id UUID REFERENCES review_results(review_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE assessment_attempts (
  attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(assessment_id),
  learner_id UUID NOT NULL REFERENCES learners(learner_id),
  answers JSONB NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'submitted',
  score_ratio NUMERIC(5,4),
  result_payload JSONB,
  idempotency_key VARCHAR(160) NOT NULL,
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  scored_at TIMESTAMPTZ,
  UNIQUE(assessment_id,idempotency_key)
);
CREATE TABLE human_review_tasks (
  human_review_task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_run_id UUID NOT NULL REFERENCES workflow_runs(workflow_run_id),
  reference_type VARCHAR(32) NOT NULL,
  reference_id VARCHAR(160) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  assigned_to UUID REFERENCES users(user_id),
  resolution_code VARCHAR(64),
  reason TEXT NOT NULL,
  resolution_payload JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at TIMESTAMPTZ
);
CREATE TABLE evaluation_runs (
  evaluation_run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  evaluation_type VARCHAR(64) NOT NULL,
  dataset_version VARCHAR(80) NOT NULL,
  system_version VARCHAR(80) NOT NULL,
  config JSONB NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  metrics JSONB,
  artifact_reference TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);
CREATE TABLE metric_snapshots (
  metric_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_scope VARCHAR(64) NOT NULL,
  metric_name VARCHAR(120) NOT NULL,
  metric_value NUMERIC NOT NULL,
  dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,
  dataset_version VARCHAR(80),
  system_version VARCHAR(80),
  measured_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE audit_logs (
  audit_log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID REFERENCES organizations(organization_id),
  actor_type VARCHAR(32) NOT NULL,
  actor_id VARCHAR(160),
  action VARCHAR(120) NOT NULL,
  reference_type VARCHAR(64),
  reference_id VARCHAR(160),
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
