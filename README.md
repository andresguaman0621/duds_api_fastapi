# DUDS Catalog API - FastAPI

API REST para gestión de catálogo de productos y generación de PDFs. Migrado desde Django REST Framework a FastAPI para mayor simplicidad y rendimiento.

## Características

- **FastAPI**: Framework moderno y rápido para APIs
- **MySQL**: Base de datos usando pymysql
- **CRUD de Categorías**: Gestión completa de categorías dinámicas
- **Categorización automática**: Productos organizados por categorías mediante keywords
- **Generación de PDFs**: Catálogos de productos con ReportLab
- **Filtrado por tallas**: Soporte para múltiples tallas

## Requisitos

- Python 3.8+
- Acceso a base de datos MySQL/MariaDB en BanaHosting
- Vista `vw_products_mariadb` configurada en la base de datos
- pip

## Instalación

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**

Copiar el archivo de ejemplo y configurar:
```bash
copy .env.example .env
```

Editar `.env` con tus credenciales de la base de datos BanaHosting:
```env
DB_HOST=hd-4928.banahosting.com
DB_PORT=3306
DB_USER=bvbmzoeb_andresguaman0621
DB_PASSWORD=Caravana.1*
DB_NAME=bvbmzoeb_wp911
PRODUCTS_VIEW=vw_products_mariadb
```

5. **Configurar la base de datos**

**Importante**: Esta API utiliza:
- **Vista de productos**: `vw_products_mariadb` (debe existir en la base de datos)
- **Tabla de categorías**: `categories` (crear con el script)

La vista `vw_products_mariadb` debe incluir los siguientes campos:
- `ID` - Identificador del producto
- `clean_name` - Nombre del producto limpio
- `color_raw` - Color sin formatear
- `talla_raw` - Talla sin formatear
- `stock_int` - Stock disponible
- `thumbnail_url` - URL de la imagen

**Crear tabla de categorías**:
```bash
# Desde la línea de comandos
mysql -u usuario -p -h hd-4928.banahosting.com bvbmzoeb_wp911 < database/schema.sql
```

O manualmente:
```sql
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    keywords JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);
```

6. **Crear categorías iniciales**

Usar los endpoints CRUD o insertar directamente:
```sql
INSERT INTO categories (name, keywords) VALUES
('Camiseta Oversize', JSON_ARRAY('Camiseta', 'Oversize')),
('Jogger', JSON_ARRAY('Jogger'));
```

7. **Probar la conexión a la base de datos** (recomendado)

```bash
python test_database.py
```

Este script verifica:
- ✓ Conexión a MySQL/MariaDB (BanaHosting)
- ✓ Existencia de la base de datos
- ✓ Existencia de la vista `vw_products_mariadb`
- ✓ Existencia de la tabla `categories`
- ✓ Estructura correcta
- ✓ Datos disponibles

Si todo está bien, verás: `✓✓✓ TODOS LOS TESTS PASARON ✓✓✓`

## Uso

### Iniciar el servidor de desarrollo

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints disponibles

#### Health Check
```http
GET /api/health
```

---

### Gestión de Categorías (CRUD)

#### Listar todas las categorías
```http
GET /api/categories-crud
```

Respuesta:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Camiseta Oversize",
      "keywords": ["Camiseta", "Oversize"],
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

#### Obtener una categoría por ID
```http
GET /api/categories-crud/{category_id}
```

#### Crear una categoría
```http
POST /api/categories-crud
Content-Type: application/json

{
  "name": "Camiseta Oversize",
  "keywords": ["Camiseta", "Oversize"]
}
```

**Nota**: Las keywords son palabras clave que deben estar TODAS presentes en el nombre del producto para que sea categorizado. Por ejemplo, si tienes keywords `["Camiseta", "Oversize"]`, el producto "Camiseta Oversize Negra - M" será categorizado correctamente.

#### Actualizar una categoría
```http
PUT /api/categories-crud/{category_id}
Content-Type: application/json

{
  "name": "Camiseta Oversize Premium",
  "keywords": ["Camiseta", "Oversize", "Premium"]
}
```

Puedes actualizar solo el nombre, solo las keywords, o ambos.

#### Eliminar una categoría
```http
DELETE /api/categories-crud/{category_id}
```

---

### Catálogo de Productos

#### Obtener categorías con conteo de productos
```http
GET /api/categories
```

Respuesta:
```json
{
  "categories": [
    {"name": "Camiseta Oversize", "count": 15},
    {"name": "Jogger", "count": 8}
  ],
  "total_categories": 2
}
```

#### Obtener tallas por categoría
```http
GET /api/categories/{category}/sizes
```

Ejemplo: `GET /api/categories/Camiseta%20Oversize/sizes`

Respuesta:
```json
{
  "category": "Camiseta Oversize",
  "sizes": [
    {"size": "S", "count": 5},
    {"size": "M", "count": 4}
  ],
  "total_sizes": 2
}
```

#### Generar PDF
```http
POST /api/generate-pdf
Content-Type: application/json

{
  "category": "Camiseta Oversize",
  "sizes": ["S", "M", "L"]
}
```

Respuesta (un solo tamaño):
```json
{
  "download_url": "http://localhost:8000/api/download-pdf/Camiseta_Oversize_S_abc123.pdf",
  "filename": "Camiseta_Oversize_S.pdf",
  "category": "Camiseta Oversize",
  "size": "S",
  "product_count": 5
}
```

Respuesta (múltiples tamaños):
```json
{
  "files": [
    {
      "download_url": "...",
      "filename": "Camiseta_Oversize_S.pdf",
      "category": "Camiseta Oversize",
      "size": "S",
      "product_count": 5
    },
    ...
  ],
  "message": "Se generaron 3 PDFs exitosamente",
  "total_files": 3
}
```

#### Descargar PDF
```http
GET /api/download-pdf/{filename}
```

## Estructura del Proyecto

```
final_duds_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── config.py            # Configuración (DB, directorios)
│   ├── database.py          # Conexión MySQL con pymysql
│   ├── models.py            # Modelos Pydantic
│   ├── schemas.py           # Schemas para request/response
│   ├── utils.py             # Utilidades (categorización, imágenes)
│   └── routes/
│       ├── __init__.py
│       ├── products.py      # Endpoints de productos/categorías
│       └── pdf.py           # Endpoints de generación PDF
├── temp_pdfs/               # PDFs generados (creado automáticamente)
├── temp_images/             # Imágenes temporales (creado automáticamente)
├── requirements.txt
├── .env.example
└── README.md
```

## Diferencias con Django

### Ventajas de FastAPI

- **Más rápido**: Alto rendimiento comparable con NodeJS
- **Menos código**: Sintaxis más simple y directa
- **Documentación automática**: Swagger/OpenAPI incluido
- **Type hints**: Validación automática con Pydantic
- **Async nativo**: Soporte para operaciones asíncronas

### Cambios principales

1. **Base de datos**: pymysql directo en lugar de Django ORM
2. **Modelos**: Pydantic en lugar de Django Models
3. **Validación**: Pydantic validators en lugar de Django serializers
4. **Rutas**: Decoradores FastAPI en lugar de Django views/viewsets
5. **Sin migrations**: Gestionas la estructura de BD manualmente

## Producción

Para despliegue en producción:

1. **Usar servidor de producción** (Gunicorn + Uvicorn):
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Configurar variables de entorno** apropiadas en `.env`

3. **Configurar CORS** específicamente en `app/main.py`:
```python
allow_origins=["https://tudominio.com"]
```

4. **Usar HTTPS** con reverse proxy (Nginx/Apache)

5. **Limpieza de archivos temporales**: Implementar limpieza periódica de `temp_pdfs/` y `temp_images/`

## Troubleshooting

### Error de conexión a MySQL

- Verificar que MySQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos `catalogo` existe

### Error al generar PDFs

- Verificar que las URLs de imágenes sean accesibles
- Verificar permisos de escritura en `temp_pdfs/` y `temp_images/`

### Dependencias

Si hay problemas instalando Pillow en Windows, instalar desde wheel:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow

## Soporte

Para más información sobre FastAPI: https://fastapi.tiangolo.com/
