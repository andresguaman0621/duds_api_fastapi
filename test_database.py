"""
Test de conexión a la base de datos MySQL
Ejecutar con: python test_database.py
"""

import pymysql
import sys
import json
from datetime import datetime

# Configuración de base de datos desde variables de entorno
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'database'),
    'charset': 'utf8mb4'
}

# Nombre de la vista de productos
PRODUCTS_VIEW = os.getenv('PRODUCTS_VIEW', 'vw_products_mariadb')

def print_header(text):
    """Imprime un encabezado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"✓ {text}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"✗ {text}")

def print_info(text):
    """Imprime información"""
    print(f"  {text}")

def test_connection():
    """Prueba la conexión básica a MySQL"""
    print_header("TEST 1: Conexión a MySQL")

    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )

        print_success(f"Conexión exitosa a MySQL en {DB_CONFIG['host']}:{DB_CONFIG['port']}")

        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print_info(f"Versión de MySQL: {version[0]}")

        connection.close()
        return True

    except pymysql.err.OperationalError as e:
        print_error("No se pudo conectar a MySQL")
        print_info(f"Error: {e}")
        print_info("\nPosibles causas:")
        print_info("  1. MySQL no está corriendo")
        print_info("  2. Host o puerto incorrectos")
        print_info("  3. Usuario o contraseña incorrectos")
        print_info(f"\nVerifica tu configuración:")
        print_info(f"  Host: {DB_CONFIG['host']}")
        print_info(f"  Puerto: {DB_CONFIG['port']}")
        print_info(f"  Usuario: {DB_CONFIG['user']}")
        return False

    except Exception as e:
        print_error(f"Error inesperado: {type(e).__name__}")
        print_info(f"Detalles: {e}")
        return False

def test_database():
    """Prueba la conexión a la base de datos específica"""
    print_header("TEST 2: Conexión a la base de datos 'catalogo'")

    try:
        connection = pymysql.connect(**DB_CONFIG)
        print_success(f"Conexión exitosa a la base de datos '{DB_CONFIG['database']}'")
        connection.close()
        return True

    except pymysql.err.OperationalError as e:
        error_code = e.args[0]

        if error_code == 1049:  # Unknown database
            print_error(f"La base de datos '{DB_CONFIG['database']}' no existe")
            print_info("\nPara crear la base de datos, ejecuta:")
            print_info(f"  mysql -u {DB_CONFIG['user']} -p")
            print_info(f"  CREATE DATABASE {DB_CONFIG['database']};")
        elif error_code == 1045:  # Access denied
            print_error("Acceso denegado: usuario o contraseña incorrectos")
            print_info(f"\nVerifica tus credenciales:")
            print_info(f"  Usuario: {DB_CONFIG['user']}")
            print_info(f"  Contraseña: {'*' * len(DB_CONFIG['password'])}")
        else:
            print_error(f"Error de conexión (código {error_code})")
            print_info(f"Detalles: {e}")

        return False

    except Exception as e:
        print_error(f"Error inesperado: {type(e).__name__}")
        print_info(f"Detalles: {e}")
        return False

def test_tables():
    """Verifica que la vista y tablas necesarias existan"""
    print_header("TEST 3: Verificación de vista y tablas")

    try:
        connection = pymysql.connect(**DB_CONFIG)

        with connection.cursor() as cursor:
            # Obtener todas las tablas y vistas
            cursor.execute("SHOW FULL TABLES")
            db_objects = cursor.fetchall()

            existing_tables = [obj[0] for obj in db_objects if obj[1] == 'BASE TABLE']
            existing_views = [obj[0] for obj in db_objects if obj[1] == 'VIEW']

        all_exist = True

        # Verificar vista de productos
        if PRODUCTS_VIEW in existing_views:
            print_success(f"Vista '{PRODUCTS_VIEW}' existe")
        else:
            print_error(f"Vista '{PRODUCTS_VIEW}' NO existe")
            print_info("\nLa vista de productos debe ser creada por el administrador de la base de datos.")
            print_info("Esta vista debe incluir los campos:")
            print_info("  - ID, clean_name, color_raw, talla_raw, stock_int, thumbnail_url")
            all_exist = False

        # Verificar tabla de categorías
        if 'categories' in existing_tables:
            print_success("Tabla 'categories' existe")
        else:
            print_error("Tabla 'categories' NO existe")
            print_info("\nPara crear la tabla de categorías, ejecuta:")
            print_info(f"  mysql -u {DB_CONFIG['user']} -p {DB_CONFIG['database']} < database/schema.sql")
            all_exist = False

        connection.close()
        return all_exist

    except Exception as e:
        print_error(f"Error al verificar tablas: {type(e).__name__}")
        print_info(f"Detalles: {e}")
        return False

def test_table_structure():
    """Verifica la estructura de la vista y tablas"""
    print_header("TEST 4: Estructura de vista y tablas")

    try:
        connection = pymysql.connect(**DB_CONFIG)

        # Verificar vista de productos
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW FULL TABLES LIKE '{PRODUCTS_VIEW}'")
            if cursor.fetchone():
                cursor.execute(f"DESCRIBE {PRODUCTS_VIEW}")
                columns = cursor.fetchall()
                print_success(f"Estructura de vista '{PRODUCTS_VIEW}':")
                for col in columns:
                    print_info(f"  - {col[0]}: {col[1]}")

        # Verificar tabla categories
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'categories'")
            if cursor.fetchone():
                cursor.execute("DESCRIBE categories")
                columns = cursor.fetchall()
                print_success("\nEstructura de tabla 'categories':")
                for col in columns:
                    print_info(f"  - {col[0]}: {col[1]}")

        connection.close()
        return True

    except Exception as e:
        print_error(f"Error al verificar estructura: {type(e).__name__}")
        print_info(f"Detalles: {e}")
        return False

def test_data():
    """Verifica si hay datos en la vista y tablas"""
    print_header("TEST 5: Datos en vista y tablas")

    try:
        connection = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            # Contar productos en la vista
            cursor.execute(f"SELECT COUNT(*) as count FROM {PRODUCTS_VIEW}")
            product_count = cursor.fetchone()['count']

            if product_count > 0:
                print_success(f"Vista '{PRODUCTS_VIEW}': {product_count} productos")

                # Mostrar algunos productos
                cursor.execute(f"""
                    SELECT
                        ID as id,
                        clean_name AS name,
                        CASE
                            WHEN talla_raw IS NOT NULL AND TRIM(talla_raw) != '' THEN
                                UPPER(SUBSTRING_INDEX(talla_raw, '-', -1))
                            ELSE 'Única'
                        END AS size,
                        stock_int AS stock
                    FROM {PRODUCTS_VIEW}
                    WHERE stock_int > 0
                    LIMIT 3
                """)
                products = cursor.fetchall()
                print_info("  Ejemplos:")
                for p in products:
                    print_info(f"    - {p['name']} (Talla: {p['size']}, Stock: {p['stock']})")
            else:
                print_info(f"Vista '{PRODUCTS_VIEW}': vacía (0 productos)")

            # Contar categorías
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            category_count = cursor.fetchone()['count']

            if category_count > 0:
                print_success(f"\nTabla 'categories': {category_count} categorías")

                # Mostrar categorías
                cursor.execute("SELECT id, name, keywords FROM categories LIMIT 5")
                categories = cursor.fetchall()
                print_info("  Categorías:")
                for c in categories:
                    keywords = json.loads(c['keywords']) if isinstance(c['keywords'], str) else c['keywords']
                    print_info(f"    - {c['name']}: {keywords}")
            else:
                print_info("\nTabla 'categories': vacía (0 categorías)")
                print_info("  Para agregar categorías, usa los endpoints CRUD o ejecuta:")
                print_info("  INSERT INTO categories (name, keywords) VALUES")
                print_info("  ('Camiseta Oversize', JSON_ARRAY('Camiseta', 'Oversize'));")

        connection.close()
        return True

    except Exception as e:
        print_error(f"Error al verificar datos: {type(e).__name__}")
        print_info(f"Detalles: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("  TEST DE CONEXIÓN A BASE DE DATOS - DUDS Catalog API")
    print("=" * 70)
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = []

    # Test 1: Conexión a MySQL
    results.append(("Conexión a MySQL", test_connection()))

    if not results[-1][1]:
        print_header("RESUMEN")
        print_error("No se pudo conectar a MySQL. Verifica que MySQL esté corriendo.")
        sys.exit(1)

    # Test 2: Conexión a la base de datos
    results.append(("Conexión a base de datos", test_database()))

    if not results[-1][1]:
        print_header("RESUMEN")
        print_error(f"La base de datos '{DB_CONFIG['database']}' no está disponible.")
        sys.exit(1)

    # Test 3: Verificar tablas
    results.append(("Tablas requeridas", test_tables()))

    # Test 4: Estructura de tablas
    if results[-1][1]:
        results.append(("Estructura de tablas", test_table_structure()))

    # Test 5: Datos
    if results[-1][1]:
        results.append(("Datos en tablas", test_data()))

    # Resumen
    print_header("RESUMEN DE TESTS")

    all_passed = True
    for test_name, passed in results:
        if passed:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
            all_passed = False

    print("\n" + "=" * 70)

    if all_passed:
        print("  ✓✓✓ TODOS LOS TESTS PASARON ✓✓✓")
        print("=" * 70)
        print("\n✓ La base de datos está lista para usar.")
        print("✓ Puedes iniciar la API con: uvicorn app.main:app --reload")
        print()
        sys.exit(0)
    else:
        print("  ✗✗✗ ALGUNOS TESTS FALLARON ✗✗✗")
        print("=" * 70)
        print("\n✗ Revisa los errores arriba y corrige los problemas.")
        print()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Test interrumpido por el usuario.")
        sys.exit(1)
    except Exception as e:
        print("\n\n" + "=" * 70)
        print("  ERROR CRÍTICO")
        print("=" * 70)
        print(f"✗ Error inesperado: {type(e).__name__}")
        print(f"✗ Detalles: {e}")
        print("=" * 70)
        sys.exit(1)
