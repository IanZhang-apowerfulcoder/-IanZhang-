-- Governance records for trusted AI generated imports in Domain Pack v2.
CREATE TABLE IF NOT EXISTS knowledge_import_packages (
    import_package_id UUID PRIMARY KEY,
    domain_pack_id UUID NOT NULL,
    origin_package_id TEXT NOT NULL,
    origin_version TEXT NOT NULL,
    trust_tier TEXT NOT NULL CHECK (trust_tier IN ('trusted_core','trusted_ai_generated')),
    runtime_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    review_status TEXT NOT NULL CHECK (review_status IN ('pending_team_review','partially_reviewed','team_reviewed','rejected','retired')),
    manifest JSONB NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_content_reviews (
    review_id UUID PRIMARY KEY,
    import_package_id UUID REFERENCES knowledge_import_packages(import_package_id),
    record_type TEXT NOT NULL,
    record_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('approved','rework','rejected')),
    source_verified BOOLEAN NOT NULL,
    technical_accuracy_verified BOOLEAN NOT NULL,
    boundary_verified BOOLEAN NOT NULL,
    assessment_quality_verified BOOLEAN NOT NULL,
    reviewer TEXT NOT NULL,
    notes TEXT,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(import_package_id, record_type, record_id, reviewer)
);
CREATE INDEX IF NOT EXISTS idx_knowledge_content_reviews_record ON knowledge_content_reviews(record_type, record_id);
