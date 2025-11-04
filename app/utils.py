import requests
import os
import uuid
import json
from PIL import Image
from io import BytesIO
from app.config import settings
from app.database import execute_query

def categorize_product(name: str) -> str:
    """
    Categoriza un producto basado en su nombre usando la base de datos.

    Args:
        name: Nombre del producto

    Returns:
        Categoría del producto o "Sin categoría"
    """
    if not name:
        return "Sin categoría"

    # Obtener todas las categorías de la base de datos
    query = "SELECT name, keywords FROM categories ORDER BY name"
    try:
        categories = execute_query(query)
    except Exception as e:
        print(f"Error obteniendo categorías de la base de datos: {str(e)}")
        return "Sin categoría"

    # Buscar coincidencia de categoría
    name_lower = name.lower()
    for category_row in categories:
        category_name = category_row['name']
        keywords_data = category_row['keywords']

        # Parsear keywords (puede venir como string JSON o ya como lista)
        if isinstance(keywords_data, str):
            try:
                keywords = json.loads(keywords_data)
            except json.JSONDecodeError:
                continue
        else:
            keywords = keywords_data

        # Verificar si todas las keywords están en el nombre del producto
        if all(keyword.lower() in name_lower for keyword in keywords):
            return category_name

    return "Sin categoría"

def download_image(url: str, timeout: int = 10) -> Image.Image:
    """
    Descarga una imagen desde una URL y la optimiza.

    Args:
        url: URL de la imagen
        timeout: Tiempo límite para la descarga

    Returns:
        Imagen optimizada o imagen por defecto en caso de error
    """
    try:
        if not url:
            raise Exception("URL vacía")

        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        # Abrir imagen desde bytes
        img = Image.open(BytesIO(response.content))

        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # Optimizar tamaño manteniendo calidad
        img.thumbnail((1300, 1300), Image.Resampling.LANCZOS)

        return img

    except Exception as e:
        print(f"Error descargando imagen {url}: {str(e)}")
        # Retornar imagen por defecto
        return Image.new('RGB', (800, 800), 'white')

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
