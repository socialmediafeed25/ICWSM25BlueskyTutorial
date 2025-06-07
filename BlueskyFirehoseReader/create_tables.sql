CREATE TABLE IF NOT EXISTS posts (
    did      TEXT,
    rkey     TEXT,
    time_us TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes    INTEGER DEFAULT 0,
    repost   INTEGER DEFAULT 0,
    comments  INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_events_created_at ON posts(time_us DESC);
CREATE INDEX IF NOT EXISTS idx_rkey_at ON posts(rkey DESC);
CREATE INDEX IF NOT EXISTS idx_did_at ON posts(did);