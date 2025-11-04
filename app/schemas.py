from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# ===== Schemas para CRUD de Categorías =====

class CategoryCreate(BaseModel):
    """Schema para crear una categoría"""
    name: str = Field(..., min_length=1, max_length=255)
    keywords: List[str] = Field(..., min_length=1)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío")
        return v.strip()

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if not v:
            raise ValueError("Debe proporcionar al menos una palabra clave")
        cleaned_keywords = [kw.strip() for kw in v if kw and kw.strip()]
        if not cleaned_keywords:
            raise ValueError("Las palabras clave no pueden estar vacías")
        return cleaned_keywords

class CategoryUpdate(BaseModel):
    """Schema para actualizar una categoría"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    keywords: Optional[List[str]] = Field(None, min_length=1)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("El nombre de la categoría no puede estar vacío")
        return v.strip() if v else v

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if v is not None:
            if not v:
                raise ValueError("Debe proporcionar al menos una palabra clave")
            cleaned_keywords = [kw.strip() for kw in v if kw and kw.strip()]
            if not cleaned_keywords:
                raise ValueError("Las palabras clave no pueden estar vacías")
            return cleaned_keywords
        return v

class CategoryDB(BaseModel):
    """Schema de categoría desde la base de datos"""
    id: int
    name: str
    keywords: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    """Respuesta de lista de categorías CRUD"""
    categories: List[CategoryDB]
    total: int

# ===== Schemas para productos por categoría (existentes) =====

class CategoryResponse(BaseModel):
    """Respuesta de categoría con conteo de productos"""
    name: str
    count: int

class CategoriesListResponse(BaseModel):
    """Respuesta de lista de categorías"""
    categories: List[CategoryResponse]
    total_categories: int

class SizeResponse(BaseModel):
    """Respuesta de talla"""
    size: str
    count: int

class SizesListResponse(BaseModel):
    """Respuesta de lista de tallas"""
    category: str
    sizes: List[SizeResponse]
    total_sizes: int

class PDFRequest(BaseModel):
    """Request para generación de PDF"""
    category: str = Field(..., min_length=1)
    sizes: List[str] = Field(..., min_length=1)

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if not v or not v.strip():
            raise ValueError("La categoría no puede estar vacía")
        return v.strip()

    @field_validator('sizes')
    @classmethod
    def validate_sizes(cls, v):
        if not v:
            raise ValueError("Debe seleccionar al menos una talla")

        cleaned_sizes = [size.strip() for size in v if size and size.strip()]

        if not cleaned_sizes:
            raise ValueError("Las tallas no pueden estar vacías")

        return cleaned_sizes

class PDFResponse(BaseModel):
    """Respuesta de PDF generado"""
    download_url: str
    filename: str
    category: str
    size: str
    product_count: int

class MultiplePDFResponse(BaseModel):
    """Respuesta de múltiples PDFs"""
    files: List[PDFResponse]
    message: str
    total_files: int

class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: str
    message: str
    timestamp: str

class ErrorResponse(BaseModel):
    """Respuesta de error"""
    error: str
