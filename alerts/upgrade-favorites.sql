-- Apply once to an existing radius-capable database. Fresh installs use schema.sql.
ALTER TABLE settings ADD COLUMN alert_mode TEXT NOT NULL DEFAULT 'all';
ALTER TABLE settings ADD COLUMN satellite_ids TEXT NOT NULL DEFAULT '[]';
