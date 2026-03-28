import pymysql
import os

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppass"),
        database=os.getenv("DB_NAME", "propiedades_db"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def ejecutar_query(sql: str) -> list:
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()