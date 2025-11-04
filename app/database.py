import pymysql
from contextlib import contextmanager
from app.config import settings

def get_db_connection():
    """Crea una conexión a la base de datos MySQL"""
    return pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@contextmanager
def get_db():
    """Context manager para manejar conexiones de base de datos"""
    connection = get_db_connection()
    try:
        yield connection
    finally:
        connection.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Ejecuta una query y retorna los resultados

    Args:
        query: SQL query a ejecutar
        params: Parámetros para la query
        fetch_one: Si True, retorna solo un resultado
        fetch_all: Si True, retorna todos los resultados

    Returns:
        Resultados de la query o None
    """
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
