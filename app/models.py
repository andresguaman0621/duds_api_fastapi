from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class Product(BaseModel):
    """
    Modelo de Producto

    Los datos vienen de la vista vw_products_mariadb que ya incluye:
    - ID: identificador único
    - clean_name: nombre del producto ya limpio (sin variantes)
    - color: color ya formateado
    - size: talla ya formateada en mayúsculas
    - stock_int: cantidad disponible
    - thumbnail_url: URL de la imagen
    """
    id: Optional[int] = None
    name: Optional[str] = None  # Ya viene limpio de la vista (clean_name)
    color: Optional[str] = None  # Ya viene formateado de la vista
    size: Optional[str] = None  # Ya viene formateado de la vista
    stock: int = 0
    thumbnail_url: Optional[str] = None

    @property
    def clean_name(self) -> str:
        """
        Retorna el nombre del producto.
        Nota: La vista ya retorna el nombre limpio, así que este property
        solo retorna el nombre tal cual para mantener compatibilidad con el código PDF.
        """
        return self.name or ""

    class Config:
        from_attributes = True

class Category(BaseModel):
    """Modelo de Categoría"""
    id: Optional[int] = None
    name: str
    keywords: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
