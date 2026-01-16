-- Migration: Add high-impact indexes for AI Playground performance optimization
-- Date: 2026-01-15
-- Purpose: Improve query performance for Agent Performance and Model Performance tables
--          These indexes optimize time-range queries with filters and grouping operations

-- 2. Index on agent_name for grouping operations
--    Speeds up Agent Performance table grouping by agent_name
CREATE INDEX `idx_alerts_agent_name` 
ON `t_alerts` (`agent_name`);

-- 3. Composite index for model_name + agent_name (HIGH IMPACT for Model Performance)
--    Speeds up Model Performance table grouping by both model_name and agent_name
CREATE INDEX `idx_alerts_model_agent` 
ON `t_alerts` (`model_name`, `agent_name`);

-- 4. Index on verification_state for AI judgment filtering
--    Speeds up filtering by verification_state (True_Positive, False_Positive, Unknown)
CREATE INDEX `idx_alerts_verification_state` 
ON `t_alerts` (`verification_state`);

-- 5. Index on is_ai_decision_correct for TP/FP/FN counting
--    Speeds up counting of Correct Decisions, False Positives, and False Negatives
CREATE INDEX `idx_alerts_ai_decision` 
ON `t_alerts` (`is_ai_decision_correct`);

-- Note: These indexes will automatically be used by the database optimizer
--       when executing queries that match the indexed columns. No code changes required.

