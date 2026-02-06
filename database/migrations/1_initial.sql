--- upgrade
CREATE TABLE links(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_url TEXT NOT NULL UNIQUE,
    original_url TEXT NOT NULL UNIQUE,
    clicks INTEGER NOT NULL DEFAULT 0,
    short_url_length INTEGER NOT NULL,
    banned INTEGER DEFAULT 0,
    banned_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_links_short_url ON links(short_url);
CREATE TABLE clicks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link_id INTEGER NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (link_id) REFERENCES links(id) ON DELETE CASCADE
);

CREATE INDEX idx_clicks_created_at ON clicks(created_at);
CREATE INDEX idx_clicks_link_id ON clicks(link_id);

--- downgrade
DROP TABLE IF EXISTS clicks;
DROP TABLE IF EXISTS links;