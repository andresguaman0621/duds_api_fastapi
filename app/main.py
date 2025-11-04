from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import products, pdf, categories

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API para catálogo de productos DUDS con generación de PDFs"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(pdf.router, prefix="/api", tags=["Health & PDF"])
app.include_router(products.router, prefix="/api", tags=["Products & Categories"])
app.include_router(categories.router, prefix="/api", tags=["Categories CRUD"])

@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "DUDS Catalog API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }
