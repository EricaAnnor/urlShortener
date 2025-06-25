from database import get_connection,release_connection

sql = """
CREATE TABLE IF NOT EXISTS urls (
    id BIGINT NOT NULL,
    original_url TEXT NOT NULL,
    short_code VARCHAR(20) NOT NULL,
    short_url TEXT NOT NULL,
    clicks INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL,
    method VARCHAR(10) NOT NULL,
    CONSTRAINT urls_pkey PRIMARY KEY (id),
    CONSTRAINT unique_cons UNIQUE (short_code, short_url, id),
    CONSTRAINT method_check CHECK (
        method IN ('base62', 'hash')
    )
);
ALTER TABLE urls OWNER TO postgres;
"""

def init_db():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            conn.commit()
        print(" Table created successfully.")
    except Exception as e:
        print("Error creating table:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            release_connection(conn)

if __name__ == "__main__":
    init_db()

