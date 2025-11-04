import os
import uuid
from datetime import datetime
from io import BytesIO
import textwrap

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black

from app.database import execute_query
from app.schemas import PDFRequest, PDFResponse, MultiplePDFResponse, HealthResponse
from app.utils import categorize_product, download_image, save_temp_image, cleanup_temp_file
from app.config import settings
from app.models import Product

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Verificar el estado de la API"""
    return HealthResponse(
        status="ok",
        message="API funcionando correctamente",
        timestamp=datetime.now().isoformat()
    )

@router.post("/generate-pdf")
def generate_pdf(request: Request, pdf_request: PDFRequest):
    """Generar PDFs de catálogo"""
    category = pdf_request.category
    sizes = pdf_request.sizes

    # Obtener productos filtrados desde la vista con JOIN para thumbnail
    query = f"""
        SELECT
            v.ID as id,
            v.clean_name AS name,
            CASE
                WHEN v.color_raw IS NOT NULL AND TRIM(v.color_raw) != '' THEN
                    CONCAT(
                        UPPER(LEFT(REPLACE(v.color_raw, '-', ' '), 1)),
                        LOWER(SUBSTRING(REPLACE(v.color_raw, '-', ' '), 2))
                    )
                ELSE 'Sin color'
            END AS color,
            CASE
                WHEN v.talla_raw IS NOT NULL AND TRIM(v.talla_raw) != '' THEN
                    UPPER(SUBSTRING_INDEX(v.talla_raw, '-', -1))
                ELSE 'Única'
            END AS size,
            v.stock_int AS stock,
            COALESCE(att.guid, '') AS thumbnail_url
        FROM {settings.PRODUCTS_VIEW} v
        LEFT JOIN wpdt_posts att ON v.thumbnail_id = att.ID
            AND att.post_type = 'attachment'
        WHERE v.stock_int >= 1
        ORDER BY v.ID ASC
    """

    products = execute_query(query)

    # Convertir a objetos Product y filtrar
    filtered_products = []
    for p in products:
        product = Product(**p)
        if categorize_product(product.name) == category and product.size in sizes:
            filtered_products.append(product)

    if not filtered_products:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron productos para los criterios seleccionados"
        )

    try:
        if len(sizes) == 1:
            # Un solo PDF
            size = sizes[0]
            size_products = [p for p in filtered_products if p.size == size]

            if not size_products:
                raise HTTPException(
                    status_code=404,
                    detail=f"No se encontraron productos para la talla {size}"
                )

            pdf_file_path = _generate_single_pdf(category, size, size_products)
            download_url = str(request.url_for('download_pdf', filename=os.path.basename(pdf_file_path)))

            return PDFResponse(
                download_url=download_url,
                filename=f"{category}_{size}.pdf".replace(" ", "_"),
                category=category,
                size=size,
                product_count=len(size_products)
            )

        else:
            # Múltiples PDFs
            pdf_files = []
            for size in sizes:
                size_products = [p for p in filtered_products if p.size == size]
                if size_products:
                    pdf_file_path = _generate_single_pdf(category, size, size_products)
                    download_url = str(request.url_for('download_pdf', filename=os.path.basename(pdf_file_path)))

                    pdf_files.append(PDFResponse(
                        download_url=download_url,
                        filename=f"{category}_{size}.pdf".replace(" ", "_"),
                        category=category,
                        size=size,
                        product_count=len(size_products)
                    ))

            if not pdf_files:
                raise HTTPException(
                    status_code=500,
                    detail="No se pudieron generar PDFs para ninguna talla"
                )

            return MultiplePDFResponse(
                files=pdf_files,
                message=f"Se generaron {len(pdf_files)} PDFs exitosamente",
                total_files=len(pdf_files)
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando PDFs: {str(e)}"
        )

@router.get("/download-pdf/{filename}")
def download_pdf(filename: str):
    """Descargar archivos PDF"""
    file_path = os.path.join(settings.TEMP_PDF_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(
        path=file_path,
        media_type='application/pdf',
        filename=filename
    )

def _generate_single_pdf(category: str, size: str, products: list) -> str:
    """Genera un PDF individual para una categoría y talla específica"""

    # Crear nombre único para el archivo
    filename = f"{category}_{size}_{uuid.uuid4().hex[:8]}.pdf".replace(" ", "_")
    file_path = os.path.join(settings.TEMP_PDF_DIR, filename)

    # Generar PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Configuración de diseño
    space_between_rows = 3.5 * inch
    space_between_columns = 4 * inch
    image_display_width = 2.0 * inch

    # Agregar fecha y hora
    current_datetime = datetime.now().strftime("%d/%m/%Y (%H:%M)")
    c.setFont("Helvetica", 10)
    c.drawString(width - 130, height - 20, current_datetime)

    def add_product_to_page(product, x, y):
        try:
            # Descargar y procesar imagen
            img = download_image(product.thumbnail_url)
            img_width, img_height = img.size
            aspect = img_height / float(img_width)
            display_height = image_display_width * aspect

            # Guardar imagen temporalmente
            temp_path = save_temp_image(img, f"product_{product.id}")

            # Dibujar imagen y marco
            c.setFillColor(black)
            c.rect(x - 3, y - display_height - 5, image_display_width, display_height, fill=1)
            c.drawImage(temp_path, x + 2, y - display_height,
                       width=image_display_width, height=display_height)
            c.rect(x + 2, y - display_height, image_display_width, display_height, fill=0)

            # Texto del producto
            product_name = product.clean_name
            wrapped_lines = textwrap.wrap(product_name, width=15)

            text_y = y - 50
            c.setFont("Helvetica", 12)
            for line in wrapped_lines:
                c.drawString(x + 2.35 * inch, text_y, line)
                text_y -= 14

            # Color y talla
            c.drawString(x + 2.35 * inch, y - 99, f"Color: {product.color or 'N/A'}")
            c.setFont("Helvetica-Bold", 15)
            c.drawString(x + 2.35 * inch, y - 120, f"{size}")

            # Stock
            c.setFont("Helvetica", 12)
            c.drawString(x + 2.35 * inch, y - 168, f"Disponible: {product.stock}")

            # Limpiar archivo temporal
            cleanup_temp_file(temp_path)

        except Exception as e:
            # Error al procesar imagen del producto
            c.setFont("Helvetica", 10)
            c.drawString(x + 10, y - 30, "Error al cargar imagen")

    # Procesar productos
    for i, product in enumerate(products):
        page_position = i % 6  # 6 productos por página
        if page_position == 0 and i != 0:
            c.showPage()
            c.drawString(width - 130, height - 20, current_datetime)

        row = page_position // 2
        col = page_position % 2

        x = 0.5 * inch + col * space_between_columns
        y = height - (0.5 * inch + row * space_between_rows)

        add_product_to_page(product, x, y)

    c.save()

    # Guardar archivo PDF
    pdf_content = buffer.getvalue()
    buffer.close()

    with open(file_path, 'wb') as f:
        f.write(pdf_content)

    return file_path
