from datetime import datetime
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """
    Defines the response returned after uploading
    or retrieving one document.
    """

    id: str

    filename: str

    delivery_url: str

    resource_type: str

    mime_type: str

    file_size: int

    status: str

    total_pages: int | None = None

    total_chunks: int = 0

    created_at: datetime


class DocumentListResponse(BaseModel):
    """
    Defines the response for listing documents.
    """

    documents: list[DocumentResponse] = Field(
        default_factory=list
    )

    total: int


class MessageResponse(BaseModel):
    """
    Standard API success message.
    """

    message: str