-- Migration 006: Add variant_desc to experiments table
-- SQLite ALTER TABLE support is limited, but ADD COLUMN is supported.
-- If the column already exists, this might fail, so we ignore duplicates.
ALTER TABLE experiments ADD COLUMN variant_desc TEXT;
