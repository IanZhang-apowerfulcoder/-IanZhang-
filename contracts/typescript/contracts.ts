// Generated contract summary for v7.0. The JSON Schemas remain authoritative.
export type RetrievalStrategy = "metadata_filtered" | "hybrid" | "graph_assisted" | "parent_child" | "agentic_decomposition";
export type ExecutionMode = "sequential" | "parallel" | "agentic" | "refuse";
export type ReviewOutcome = "pass" | "revise" | "reject" | "human_review";
export type AgentName = "diagnosis" | "path_planning" | "rag_router" | "resource_coordinator" | "assessment_evaluation" | "review_coordinator" | "arbitration" | "explanation_generator" | "practice_generator" | "quiz_draft_generator" | "factuality_reviewer" | "difficulty_reviewer" | "assessment_quality_reviewer" | "safety_reviewer";
export interface QueryAnalysis { query_type: string; complexity: "low"|"medium"|"high"; risk_level: "low"|"medium"|"high"; execution_mode: ExecutionMode; selected_strategies: RetrievalStrategy[]; reason_summary: string; }
export interface WorkflowEvent { event_id:string; sequence_no:number; workflow_run_id:string; session_id:string; event_type:string; payload:Record<string,unknown>; correlation_id:string; created_at:string; }
