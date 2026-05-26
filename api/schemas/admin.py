from typing import Any

from pydantic import BaseModel


class CollectionCount(BaseModel):
    name: str
    count: int


class CollectionsResponse(BaseModel):
    collections: list[CollectionCount]
    total: int


class UploadCsvResponse(BaseModel):
    filename: str
    rows_total: int
    rows_skipped: int
    inserted: int
    batch_errors: int
    events_total: int
    sessions_built: int
    content_stats_built: int


class DocumentsResponse(BaseModel):
    collection: str
    total: int
    page: int
    page_size: int
    documents: list[dict[str, Any]]


class UpdateDocumentRequest(BaseModel):
    # Campos a sobreescribir vía $set. `_id` se ignora en el repositorio.
    fields: dict[str, Any]


class UpdateDocumentResponse(BaseModel):
    ok: bool
    modified: int


class DeleteDocumentResponse(BaseModel):
    ok: bool
    deleted: int
