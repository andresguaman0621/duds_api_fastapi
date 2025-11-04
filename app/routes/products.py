from fastapi import APIRouter, HTTPException
from app.database import execute_query
from app.schemas import CategoriesListResponse, CategoryResponse, SizesListResponse, SizeResponse
from app.utils import categorize_product, get_available_sizes
from app.config import settings

router = APIRouter()

@router.get("/categories", response_model=CategoriesListResponse)
def get_categories():
    """Obtener todas las categorías disponibles"""
    # Obtener todos los productos con stock desde la vista
    query = f"SELECT ID as id, clean_name AS name FROM {settings.PRODUCTS_VIEW} WHERE stock_int >= 1"
    products = execute_query(query)

    # Contar productos por categoría
    category_counts = {}
    for product in products:
        category = categorize_product(product['name'])
        if category != "Sin categoría":
            category_counts[category] = category_counts.get(category, 0) + 1

    # Preparar respuesta
    categories_data = [
        CategoryResponse(name=category, count=count)
        for category, count in sorted(category_counts.items())
    ]

    return CategoriesListResponse(
        categories=categories_data,
        total_categories=len(categories_data)
    )

@router.get("/categories/{category}/sizes", response_model=SizesListResponse)
def get_sizes_by_category(category: str):
    """Obtener tallas disponibles por categoría"""
    # Obtener productos con stock desde la vista
    query = f"""
        SELECT
            ID as id,
            clean_name AS name,
            CASE
                WHEN talla_raw IS NOT NULL AND TRIM(talla_raw) != '' THEN
                    UPPER(SUBSTRING_INDEX(talla_raw, '-', -1))
                ELSE 'Única'
            END AS size
        FROM {settings.PRODUCTS_VIEW}
        WHERE stock_int >= 1
    """
    products = execute_query(query)

    # Filtrar por categoría
    category_products = [
        p for p in products
        if categorize_product(p['name']) == category
    ]

    if not category_products:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron productos para la categoría: {category}"
        )

    # Contar productos por talla
    size_counts = {}
    for product in category_products:
        if product['size']:
            size_counts[product['size']] = size_counts.get(product['size'], 0) + 1

    # Ordenar tallas según orden predefinido
    size_order = get_available_sizes()
    ordered_sizes = []

    for size in size_order:
        if size in size_counts:
            ordered_sizes.append(SizeResponse(size=size, count=size_counts[size]))

    # Agregar tallas no estándar al final
    for size, count in size_counts.items():
        if size not in size_order:
            ordered_sizes.append(SizeResponse(size=size, count=count))

    return SizesListResponse(
        category=category,
        sizes=ordered_sizes,
        total_sizes=len(ordered_sizes)
    )
