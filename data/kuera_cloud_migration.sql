-- KUERA Database Cloud Migration Script
-- Generated: 2026-04-07 16:12:11.103760

-- NOTE: Modify data types for target database

-- Table: interactions
DROP TABLE IF EXISTS interactions CASCADE;
CREATE TABLE interactions (
    id INTEGER,
    timestamp TIMESTAMP,
    session_id TEXT,
    user_id TEXT,
    user_message TEXT,
    kuera_response TEXT,
    model_used TEXT,
    confidence FLOAT,
    latency_ms FLOAT,
    user_feedback INTEGER,
    feedback_reason TEXT,
    intent TEXT,
    emotion TEXT,
    location TEXT,
    metadata TEXT
);

-- Table: user_profiles
DROP TABLE IF EXISTS user_profiles CASCADE;
CREATE TABLE user_profiles (
    user_id TEXT,
    created_at TIMESTAMP,
    last_active TIMESTAMP,
    name TEXT,
    age_group TEXT,
    location TEXT,
    province TEXT,
    preferred_language TEXT,
    total_interactions INTEGER,
    satisfaction_rate FLOAT,
    personality_profile TEXT,
    preferences TEXT
);

-- Table: model_metrics
DROP TABLE IF EXISTS model_metrics CASCADE;
CREATE TABLE model_metrics (
    id INTEGER,
    timestamp TIMESTAMP,
    model_version TEXT,
    metric_name TEXT,
    metric_value FLOAT,
    dataset_size INTEGER,
    training_duration_seconds FLOAT,
    notes TEXT
);

-- Table: knowledge_base
DROP TABLE IF EXISTS knowledge_base CASCADE;
CREATE TABLE knowledge_base (
    id INTEGER,
    created_at TIMESTAMP,
    category TEXT,
    title TEXT,
    content TEXT,
    keywords TEXT,
    source TEXT,
    last_updated TIMESTAMP,
    usage_count INTEGER
);

-- Table: sessions
DROP TABLE IF EXISTS sessions CASCADE;
CREATE TABLE sessions (
    session_id TEXT,
    user_id TEXT,
    created_at TIMESTAMP,
    last_activity TIMESTAMP,
    context TEXT,
    is_active INTEGER
);

-- Table: analytics_daily
DROP TABLE IF EXISTS analytics_daily CASCADE;
CREATE TABLE analytics_daily (
    date TEXT,
    total_interactions INTEGER,
    unique_users INTEGER,
    avg_satisfaction FLOAT,
    avg_response_time_ms FLOAT,
    top_intent TEXT,
    error_count INTEGER
);
