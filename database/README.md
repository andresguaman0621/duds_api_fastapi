# Database Schema

## Setup Instructions

1. Asegúrate de que la base de datos `catalogo` exista:
```sql
CREATE DATABASE IF NOT EXISTS catalogo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE catalogo;
```

2. Ejecuta el archivo de schema:
```bash
mysql -u root -p catalogo < database/schema.sql
```

O desde MySQL:
```sql
USE catalogo;
SOURCE database/schema.sql;
```

## Tablas

### categories
Almacena las categorías de productos con sus palabras clave para categorización automática.

**Estructura:**
- `id`: ID único de la categoría (AUTO_INCREMENT)
- `name`: Nombre de la categoría (único, NOT NULL)
- `keywords`: Array JSON de palabras clave para categorización (NOT NULL)
- `created_at`: Fecha de creación (automática)
- `updated_at`: Fecha de última actualización (automática)

**Ejemplo de uso:**
```sql
-- Crear una categoría
INSERT INTO categories (name, keywords) VALUES
('Camiseta Oversize', JSON_ARRAY('Camiseta', 'Oversize'));

-- La categorización funciona buscando TODAS las keywords en el nombre del producto
-- Si un producto se llama "Camiseta Oversize Negra - Talla M"
-- y la categoría tiene keywords ['Camiseta', 'Oversize']
-- entonces el producto será categorizado como 'Camiseta Oversize'
```

### catalog_product
Tabla de productos (debe existir previamente).

Ver documentación del proyecto original para su estructura.
