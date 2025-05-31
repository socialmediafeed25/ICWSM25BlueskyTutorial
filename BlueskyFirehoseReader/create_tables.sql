CREATE TABLE IF NOT EXISTS posts (
    did      TEXT,
    rkey     TEXT,
    time_us TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    likes    INTEGER DEFAULT 0,
    repost   INTEGER DEFAULT 0,
    comments  INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_events_created_at ON posts(time_us DESC);