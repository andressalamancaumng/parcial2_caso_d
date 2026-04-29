import psycopg2

from src.config import DB_HOST, DB_NAME, DB_USER, DB_PASS


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )