# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend for DUDS product catalog system that generates PDF catalogs. Migrated from Django REST Framework for simplicity and performance. The system categorizes clothing products, filters by size/category, and creates formatted PDF catalogs with product images.

## Database Configuration

Uses MySQL/MariaDB via pymysql (simple connection, no ORM):
- **Host**: BanaHosting (`hd-4928.banahosting.com`)
- **Database**: `bvbmzoeb_wp911`
- **Credentials**: in `.env.example`
- **Connection handler**: `app/database.py`
- **Data sources**:
  - `vw_products_mariadb` (VIEW - products with formatted data, must exist)
  - `categories` (TABLE - dynamic categories with keywords, created via `database/schema.sql`)

### Products View Structure
The API reads product data from `vw_products_mariadb` view which must provide:
- `ID` - Product identifier
- `clean_name` - Product name already cleaned (without variants)
- `color_raw` - Raw color value for formatting
- `talla_raw` - Raw size value for formatting
- `stock_int` - Available stock quantity
- `thumbnail_url` - Product image URL

## Common Commands

### Development
```bash
# Start development server (with auto-reload)
uvicorn app.main:app --reload

# Start on specific port
uvicorn app.main:app --reload --port 8080

# Start with custom host
uvicorn app.main:app --reload --host 0.0.0.0
```

### Production
```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Create categories table
mysql -u usuario -p -h hd-4928.banahosting.com bvbmzoeb_wp911 < database/schema.sql

# Test database connection (recommended)
python test_database.py
```

## Architecture

### Database Layer (`app/database.py`)
- **Simple pymysql wrapper** - No ORM, direct SQL queries
- `get_db_connection()`: Creates MySQL connection
- `get_db()`: Context manager for connection handling
- `execute_query()`: Helper for executing queries with automatic connection management
- Returns results as dictionaries (DictCursor)

### Models & Schemas
- **`app/models.py`**: Pydantic models representing database entities
  - `Product`: Model matching `vw_products_mariadb` view fields (id, name, color, size, stock, thumbnail_url)
    - Note: `sku` and `regular_price` removed as view doesn't provide them
    - `clean_name` property returns name as-is (view already provides clean name)
  - `Category`: Category model with name and keywords list
- **`app/schemas.py`**: Request/response schemas with validation
  - Uses Pydantic validators for input validation
  - Separate schemas for requests and responses
  - CRUD schemas: `CategoryCreate`, `CategoryUpdate`, `CategoryDB`, `CategoryListResponse`

### Product Categorization (`app/utils.py:10-50`)
- **Dynamic categorization** from database `categories` table
- `categorize_product()` function queries all categories from DB on each call
- Categories stored with JSON array of keywords
- **Matching logic**: ALL keywords must be present in product name (case-insensitive)
- Example: Category "Camiseta Oversize" with keywords `["Camiseta", "Oversize"]` matches product "Camiseta Oversize Negra - M"
- Returns "Sin categoría" if no match found
- Product name comes from `clean_name` field in view (already cleaned)

### API Routes

**`app/routes/categories.py`** (Categories CRUD):
- `GET /api/categories-crud` - List all categories with details
- `GET /api/categories-crud/{category_id}` - Get single category by ID
- `POST /api/categories-crud` - Create new category (body: `{name, keywords[]}`)
- `PUT /api/categories-crud/{category_id}` - Update category (partial updates allowed)
- `DELETE /api/categories-crud/{category_id}` - Delete category

**`app/routes/products.py`** (Products & Categories):
- `GET /api/categories` - List categories with product counts (queries `vw_products_mariadb`)
- `GET /api/categories/{category}/sizes` - Available sizes for category (formats size from `talla_raw`)

**`app/routes/pdf.py`** (PDFs & Health):
- `GET /api/health` - Health check
- `POST /api/generate-pdf` - Generate PDF catalogs (body: `{category, sizes[]}`)
- `GET /api/download-pdf/{filename}` - Download generated PDFs

### PDF Generation Flow (`app/routes/pdf.py:32-219`)
1. Validate request (category + sizes list)
2. Query products from `vw_products_mariadb` view with `stock_int >= 1`
3. Format color and size from raw fields in the query
4. Filter by category (using `categorize_product()`) and sizes
5. Single PDF for 1 size, multiple PDFs for multiple sizes
6. 6 products per page (2 columns × 3 rows)
7. Download product images, process with Pillow, embed with ReportLab
8. Temp files: `temp_images/`, PDFs: `temp_pdfs/`
9. Return download URLs

### Image Processing (`app/utils.py:40-106`)
- Download from product `thumbnail_url`
- Convert to RGB (handles RGBA/LA/P)
- Thumbnail to max 1300×1300px with LANCZOS
- Save as JPEG (85% quality)
- Auto-cleanup after PDF generation

### Configuration (`app/config.py`)
- Uses `pydantic-settings` for environment variables
- Loads from `.env` file
- Auto-creates `temp_pdfs/` and `temp_images/` directories
- Database, API, and directory settings

### Size Ordering
Standard order: `XXS, XS, S, M, L, XL, XXL` (defined in `utils.py:125-133`). Non-standard sizes appended at end.

### Database Schema

**`vw_products_mariadb` (View)**:
- Must exist in database (created by DB administrator)
- Required fields: `ID`, `clean_name`, `color_raw`, `talla_raw`, `stock_int`, `thumbnail_url`
- Data is already optimized and formatted for the API

**`categories` (Table)**:
- `id`: Auto-increment primary key
- `name`: Unique category name
- `keywords`: JSON array of keywords for matching
- `created_at`, `updated_at`: Automatic timestamps
- Created via `database/schema.sql`

## Key Differences from Django Version

1. **No ORM**: Direct SQL with pymysql instead of Django ORM
2. **No Migrations**: Database schema managed manually
3. **Pydantic**: Data validation instead of Django serializers
4. **Decorators**: FastAPI route decorators instead of Django views/viewsets
5. **Auto Docs**: Built-in Swagger UI at `/docs`
6. **Type Hints**: Automatic validation and documentation from Python types

## Development Notes

- Products read from `vw_products_mariadb` view (not direct table)
- Products filtered by `stock_int >= 1` for availability
- View provides pre-formatted data (`clean_name`, raw color/size values)
- Categories are **dynamically loaded from database** on each categorization call
- Category keywords must ALL match (AND logic, not OR)
- PDF generation uses ReportLab with custom layout
- CORS enabled for all origins in development (configure for production in `app/main.py:16-22`)
- Temporary files not auto-cleaned (implement cleanup for production)
- Images downloaded synchronously (consider async for better performance)
- Database hosted on BanaHosting (remote connection)

## Important Implementation Details

### Database Architecture
- Uses **database view** (`vw_products_mariadb`) instead of direct table access
- View must be created and maintained by database administrator
- View provides optimized, pre-formatted product data
- Reduces complexity in application layer (no SKU, no pricing calculations)

### Category Management
- Categories stored in MySQL `categories` table with JSON keywords
- No hardcoded categories in code
- Use CRUD endpoints (`/api/categories-crud`) to manage categories
- Categorization happens dynamically by querying DB on each product categorization
- Category names must be unique (enforced by DB constraint)

### Configuration
- Uses `settings.PRODUCTS_VIEW` to specify view name (configurable via `.env`)
- All database queries use the configured view name
- Connection to remote database (BanaHosting) - ensure network connectivity
