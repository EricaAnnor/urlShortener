from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load .env variables into environment
load_dotenv()

db_pool = pool.SimpleConnectionPool(
    minconn=0,
    maxconn=10,
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    cursor_factory=RealDictCursor

)


def get_connection():
    return db_pool.getconn()

def release_connection(conn):
    db_pool.putconn(conn)



