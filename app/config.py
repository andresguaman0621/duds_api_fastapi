# import os
# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     # DUDS Cpanel BanaHosting Database
#     # IMPORTANTE: Configura estas variables en el archivo .env
#     # NO incluyas credenciales reales aquí (este archivo se sube a GitHub)
#     DB_HOST: str = "localhost"
#     DB_PORT: int = 3306
#     DB_USER: str = "user"
#     DB_PASSWORD: str = "password"
#     DB_NAME: str = "database"

#     # Database View
#     PRODUCTS_VIEW: str = "vw_products_mariadb"

#     # Directories
#     TEMP_PDF_DIR: str = "temp_pdfs"
#     TEMP_IMAGE_DIR: str = "temp_images"

#     # API
#     API_TITLE: str = "DUDS Catalog API"
#     API_VERSION: str = "1.0.0"

#     class Config:
#         env_file = ".env"

# settings = Settings()

# # Create temp directories if they don't exist
# os.makedirs(settings.TEMP_PDF_DIR, exist_ok=True)
# os.makedirs(settings.TEMP_IMAGE_DIR, exist_ok=True)


import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


# Cargar .env solo si existe (útil para desarrollo local)
if Path(".env").exists():
    load_dotenv(".env")


class Settings(BaseSettings):
    # Variables de entorno que Coolify inyecta automáticamente
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")

    PRODUCTS_VIEW: str = os.getenv("PRODUCTS_VIEW")

    TEMP_PDF_DIR: str = os.getenv("TEMP_PDF_DIR", "temp_pdfs")
    TEMP_IMAGE_DIR: str = os.getenv("TEMP_IMAGE_DIR", "temp_images")

    API_TITLE: str = os.getenv("API_TITLE", "DUDS Catalog API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

# Crear directorios si no existen
os.makedirs(settings.TEMP_PDF_DIR, exist_ok=True)
os.makedirs(settings.TEMP_IMAGE_DIR, exist_ok=True)
