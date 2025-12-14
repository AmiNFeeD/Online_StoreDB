import psycopg2
from psycopg2.extras import RealDictCursor
from . import config

def get_connection():
    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        cursor_factory=RealDictCursor
    )
    return conn