-- App schema: 1:1 (users <-> profiles) and 1:N (customers -> orders).
-- PostgreSQL 18 idioms: GENERATED ALWAYS AS IDENTITY, timestamptz.

-- === 1:1 relationship: user <-> profile ===
CREATE TABLE users (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- The UNIQUE constraint on user_id enforces the 1:1 cardinality at the DB level.
CREATE TABLE profiles (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    BIGINT NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    full_name  TEXT NOT NULL,
    bio        TEXT
);

-- === 1:N relationship: customer -> orders ===
CREATE TABLE customers (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers (id) ON DELETE CASCADE,
    ordered_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    status      TEXT NOT NULL DEFAULT 'open',
    total_cents INT NOT NULL DEFAULT 0
);

CREATE INDEX idx_orders_customer_id ON orders (customer_id);
