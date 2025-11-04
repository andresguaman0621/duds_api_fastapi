import json
from fastapi import APIRouter, HTTPException
from app.database import execute_query
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryDB,
    CategoryListResponse
)
from app.models import Category

router = APIRouter()

@router.get("/categories-crud", response_model=CategoryListResponse, summary="Listar todas las categorías")
def get_all_categories():
    """Obtener todas las categorías con sus palabras clave"""
    query = "SELECT id, name, keywords, created_at, updated_at FROM categories ORDER BY name"
    results = execute_query(query)

    categories = []
    for row in results:
        # Parsear JSON keywords
        keywords = json.loads(row['keywords']) if isinstance(row['keywords'], str) else row['keywords']

        categories.append(CategoryDB(
            id=row['id'],
            name=row['name'],
            keywords=keywords,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        ))

    return CategoryListResponse(
        categories=categories,
        total=len(categories)
    )

@router.get("/categories-crud/{category_id}", response_model=CategoryDB, summary="Obtener una categoría por ID")
def get_category(category_id: int):
    """Obtener una categoría específica por su ID"""
    query = "SELECT id, name, keywords, created_at, updated_at FROM categories WHERE id = %s"
    result = execute_query(query, (category_id,), fetch_one=True, fetch_all=False)

    if not result:
        raise HTTPException(status_code=404, detail=f"Categoría con ID {category_id} no encontrada")

    # Parsear JSON keywords
    keywords = json.loads(result['keywords']) if isinstance(result['keywords'], str) else result['keywords']

    return CategoryDB(
        id=result['id'],
        name=result['name'],
        keywords=keywords,
        created_at=result['created_at'],
        updated_at=result['updated_at']
    )

@router.post("/categories-crud", response_model=CategoryDB, status_code=201, summary="Crear una nueva categoría")
def create_category(category: CategoryCreate):
    """Crear una nueva categoría"""

    # Verificar si ya existe una categoría con ese nombre
    check_query = "SELECT id FROM categories WHERE name = %s"
    existing = execute_query(check_query, (category.name,), fetch_one=True, fetch_all=False)

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una categoría con el nombre '{category.name}'"
        )

    # Insertar nueva categoría
    keywords_json = json.dumps(category.keywords)
    insert_query = """
        INSERT INTO categories (name, keywords)
        VALUES (%s, %s)
    """

    category_id = execute_query(
        insert_query,
        (category.name, keywords_json),
        fetch_one=False,
        fetch_all=False
    )

    # Obtener la categoría creada
    return get_category(category_id)

@router.put("/categories-crud/{category_id}", response_model=CategoryDB, summary="Actualizar una categoría")
def update_category(category_id: int, category: CategoryUpdate):
    """Actualizar una categoría existente"""

    # Verificar que la categoría existe
    check_query = "SELECT id FROM categories WHERE id = %s"
    existing = execute_query(check_query, (category_id,), fetch_one=True, fetch_all=False)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Categoría con ID {category_id} no encontrada")

    # Construir query dinámica basada en los campos proporcionados
    update_fields = []
    params = []

    if category.name is not None:
        # Verificar que no exista otra categoría con ese nombre
        name_check = "SELECT id FROM categories WHERE name = %s AND id != %s"
        duplicate = execute_query(name_check, (category.name, category_id), fetch_one=True, fetch_all=False)
        if duplicate:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe otra categoría con el nombre '{category.name}'"
            )
        update_fields.append("name = %s")
        params.append(category.name)

    if category.keywords is not None:
        update_fields.append("keywords = %s")
        params.append(json.dumps(category.keywords))

    if not update_fields:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")

    # Ejecutar actualización
    params.append(category_id)
    update_query = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = %s"
    execute_query(update_query, tuple(params), fetch_one=False, fetch_all=False)

    # Retornar categoría actualizada
    return get_category(category_id)

@router.delete("/categories-crud/{category_id}", status_code=204, summary="Eliminar una categoría")
def delete_category(category_id: int):
    """Eliminar una categoría"""

    # Verificar que la categoría existe
    check_query = "SELECT id FROM categories WHERE id = %s"
    existing = execute_query(check_query, (category_id,), fetch_one=True, fetch_all=False)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Categoría con ID {category_id} no encontrada")

    # Eliminar categoría
    delete_query = "DELETE FROM categories WHERE id = %s"
    execute_query(delete_query, (category_id,), fetch_one=False, fetch_all=False)

    return None
