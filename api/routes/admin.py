from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.schemas.admin import (
    CollectionsResponse,
    DeleteDocumentResponse,
    DocumentsResponse,
    UpdateDocumentRequest,
    UpdateDocumentResponse,
    UploadCsvResponse,
)
from config.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from db.connection import get_db
from db.repositories.admin import (
    ADMIN_COLLECTIONS,
    count_collections,
    delete_document,
    ingest_csv,
    list_documents,
    update_document,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _check_collection(collection: str) -> None:
    if collection not in ADMIN_COLLECTIONS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Colección desconocida: '{collection}'. "
                f"Válidas: {', '.join(ADMIN_COLLECTIONS)}."
            ),
        )


@router.get("/collections", response_model=CollectionsResponse)
async def collections(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Conteo de documentos por colección (events, sessions, content_stats)."""
    counts = await count_collections(db)
    return CollectionsResponse(
        collections=counts, total=sum(c["count"] for c in counts)
    )


@router.post("/upload-csv", response_model=UploadCsvResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Sube un CSV de eventos: lo inserta en `events` y re-construye las derivadas.
    El dashboard refleja los datos nuevos de inmediato.
    """
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un .csv")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    try:
        result = await ingest_csv(db, raw)
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=400, detail=f"No se pudo procesar el CSV: {e}"
        ) from e

    return UploadCsvResponse(filename=file.filename, **result)


@router.get("/documents/{collection}", response_model=DocumentsResponse)
async def documents(
    collection: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Documentos paginados de una colección, para la tabla editable del admin."""
    _check_collection(collection)
    data = await list_documents(db, collection, page, page_size)
    return DocumentsResponse(
        collection=collection,
        page=page,
        page_size=page_size,
        total=data["total"],
        documents=data["documents"],
    )


@router.put(
    "/documents/{collection}/{doc_id}", response_model=UpdateDocumentResponse
)
async def edit_document(
    collection: str,
    doc_id: str,
    body: UpdateDocumentRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Edición en vivo de un documento (aplica $set con los campos enviados)."""
    _check_collection(collection)
    try:
        modified = await update_document(db, collection, doc_id, body.fields)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return UpdateDocumentResponse(ok=True, modified=modified)


@router.delete(
    "/documents/{collection}/{doc_id}", response_model=DeleteDocumentResponse
)
async def remove_document(
    collection: str,
    doc_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    _check_collection(collection)
    try:
        deleted = await delete_document(db, collection, doc_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    return DeleteDocumentResponse(ok=True, deleted=deleted)
