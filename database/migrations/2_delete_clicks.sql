--- upgrade
ALTER TABLE links
    DROP COLUMN clicks;

--- downgrade
ALTER TABLE links
    ADD COLUMN clicks INTEGER NOT NULL DEFAULT 0;