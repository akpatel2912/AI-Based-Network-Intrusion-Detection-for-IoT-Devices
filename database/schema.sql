
CREATE TABLE IF NOT EXISTS predictions (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rst_count   DOUBLE PRECISION NOT NULL,
    icmp        DOUBLE PRECISION NOT NULL,
    min_size    DOUBLE PRECISION NOT NULL,
    avg_size    DOUBLE PRECISION NOT NULL,
    iat         DOUBLE PRECISION NOT NULL,
    number      DOUBLE PRECISION NOT NULL,
    variance    DOUBLE PRECISION NOT NULL,
    weight      DOUBLE PRECISION NOT NULL,
    prediction  VARCHAR(10) NOT NULL CHECK (prediction IN ('Normal', 'Attack')),
    confidence  DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1)
);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions (created_at DESC);
