-- Migration 007: Update metrics schema to include ctr_percent, retention_3s_percent, completion_rate_percent, conversion_count, and reward_score.
-- SQLite ALTER TABLE support is limited, but ADD COLUMN is supported.
-- If the column already exists, this might fail, so we ignore duplicates.
ALTER TABLE metrics ADD COLUMN ctr_percent REAL;
ALTER TABLE metrics ADD COLUMN retention_3s_percent REAL;
ALTER TABLE metrics ADD COLUMN completion_rate_percent REAL;
ALTER TABLE metrics ADD COLUMN conversion_count INTEGER;
ALTER TABLE metrics ADD COLUMN reward_score REAL;
