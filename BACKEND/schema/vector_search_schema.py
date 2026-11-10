
from pydantic import BaseModel, Field
from typing import Optional


class SemanticSearchRequest(BaseModel):

    query: str = Field(
        min_length=1,
        max_length=2000,
        description="User's semantic search query"
    )

    document_id: Optional[str] = Field(
        default=None,
        description="Optional document ID for document-specific search"
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of search results"
    )
