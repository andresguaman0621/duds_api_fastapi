import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DUDS Cpanel BanaHosting Database
    # IMPORTANTE: Configura estas variables en el archivo .env
    # NO incluyas credenciales reales aquí (este archivo se sube a GitHub)
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "database"

    # Database View
    PRODUCTS_VIEW: str = "vw_products_mariadb"

    # Directories
    TEMP_PDF_DIR: str = "temp_pdfs"
    TEMP_IMAGE_DIR: str = "temp_images"

    # API
    API_TITLE: str = "DUDS Catalog API"
    API_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"

settings = Settings()

# Create temp directories if they don't exist
os.makedirs(settings.TEMP_PDF_DIR, exist_ok=True)
os.makedirs(settings.TEMP_IMAGE_DIR, exist_ok=True)
