import requests
import os
import uuid
import json
import re
from PIL import Image
from io import BytesIO
from app.config import settings
from app.database import execute_query

# Pre-compilar regex para optimización de URLs (se ejecuta solo una vez)
_dimension_pattern = re.compile(r'-\d+x\d+\.(jpg|jpeg|png|webp)', re.IGNORECASE)
_extension_pattern = re.compile(r'\.(jpg|jpeg|png|webp)', re.IGNORECASE)

# Cache global de categorías (se carga una sola vez)
_categories_cache = None

def load_categories_cache():
    """Carga las categorías desde la base de datos una sola vez"""
    global _categories_cache

    if _categories_cache is not None:
        return _categories_cache

    query = "SELECT name, keywords FROM categories ORDER BY name"
    try:
        categories = execute_query(query)
        _categories_cache = []

        for category_row in categories:
            keywords_data = category_row['keywords']
            # Parsear keywords
            if isinstance(keywords_data, str):
                try:
                    keywords = json.loads(keywords_data)
                except json.JSONDecodeError:
                    continue
            else:
                keywords = keywords_data

            _categories_cache.append({
                'name': category_row['name'],
                'keywords': [kw.lower() for kw in keywords]  # Pre-lowercase
            })

        return _categories_cache
    except Exception:
        # Error al cargar categorías, retornar lista vacía
        return []

def categorize_product(name: str) -> str:
    """
    Categoriza un producto basado en su nombre usando cache de categorías.
    OPTIMIZADO: Ya no hace query por cada producto.

    Args:
        name: Nombre del producto

    Returns:
        Categoría del producto o "Sin categoría"
    """
    if not name:
        return "Sin categoría"

    # Obtener categorías del cache (solo 1 query total)
    categories = load_categories_cache()

    # Buscar coincidencia de categoría
    name_lower = name.lower()
    for category in categories:
        # Las keywords ya están en lowercase
        if all(keyword in name_lower for keyword in category['keywords']):
            return category['name']

    return "Sin categoría"

def clear_categories_cache():
    """Limpia el cache de categorías (útil después de crear/actualizar categorías)"""
    global _categories_cache
    _categories_cache = None

def get_wordpress_optimized_url(original_url: str) -> str:
    """
    Convierte una URL original de WordPress a su versión optimizada
    con las dimensiones específicas 1070x1536.
    OPTIMIZADO: Usa regex pre-compilados.

    Args:
        original_url: URL original de WordPress

    Returns:
        URL optimizada con dimensiones 1070x1536
    """
    if not original_url:
        return original_url

    # Verificar si la URL ya tiene dimensiones (está optimizada)
    if _dimension_pattern.search(original_url):
        return original_url

    # Extraer la extensión del archivo
    match = _extension_pattern.search(original_url)
    if not match:
        return original_url

    extension = match.group(1)
    base_url = original_url.rsplit('.', 1)[0]

    # Construir la URL optimizada con las dimensiones específicas
    optimized_url = f"{base_url}-1070x1536.{extension}"
    return optimized_url

def download_image(url: str, timeout: int = 10) -> Image.Image:
    """
    Descarga una imagen usando la versión optimizada de WordPress (1070x1536).
    OPTIMIZADO: Intenta primero la versión optimizada, luego fallback a original.

    Args:
        url: URL de la imagen (puede ser original o optimizada)
        timeout: Tiempo límite para la descarga

    Returns:
        Imagen descargada o imagen por defecto blanca en caso de error
    """
    if not url:
        return Image.new('RGB', (1070, 1536), 'white')

    # URLs a intentar: primero optimizada, luego original
    urls_to_try = [get_wordpress_optimized_url(url), url]

    for attempt_url in urls_to_try:
        try:
            response = requests.get(attempt_url, timeout=timeout)
            response.raise_for_status()

            # Abrir imagen desde bytes
            img = Image.open(BytesIO(response.content))

            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            return img

        except requests.exceptions.RequestException:
            continue  # Intentar con la siguiente URL
        except Exception:
            continue  # Para errores de PIL u otros

    # Si todas las URLs fallan, devolver imagen por defecto
    return Image.new('RGB', (1070, 1536), 'white')

def save_temp_image(img: Image.Image, prefix: str = "temp_img") -> str:
    """
    Guarda una imagen temporalmente y retorna la ruta.

    Args:
        img: Imagen a guardar
        prefix: Prefijo para el nombre del archivo

    Returns:
        Ruta del archivo temporal
    """
    # Generar nombre único
    filename = f"{prefix}_{uuid.uuid4().hex}.jpg"
    temp_path = os.path.join(settings.TEMP_IMAGE_DIR, filename)

    # Guardar imagen
    img.save(temp_path, "JPEG", quality=85, optimize=True)

    return temp_path

def cleanup_temp_file(file_path: str):
    """
    Elimina un archivo temporal de forma segura.

    Args:
        file_path: Ruta del archivo a eliminar
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error eliminando archivo temporal {file_path}: {str(e)}")

def format_color_name(color: str) -> str:
    """
    Formatea el nombre del color para mejor presentación.

    Args:
        color: Color original

    Returns:
        Color formateado
    """
    if not color:
        return ""

    # Reemplazar guiones por espacios y capitalizar cada palabra
    formatted = color.replace('-', ' ')
    return ' '.join(word.capitalize() for word in formatted.split())

def get_available_sizes() -> list:
    """
    Retorna una lista de todas las tallas disponibles en orden.

    Returns:
        Lista de tallas ordenadas
    """
    size_order = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL']
    return size_order
