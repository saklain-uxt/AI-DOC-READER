

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# -----------------------------------------
# 1. Chat Request
# -----------------------------------------

class ChatRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )

    mode: Literal["document", "global"]

    document_id: Optional[str] = None
    document_ids: Optional[List[str]] = None

    conversation_id: Optional[str] = None


# -----------------------------------------
# 2. Source Schema
# -----------------------------------------

class SourceSchema(BaseModel):

    document_id: str

    page_number: Optional[int] = None

    chunk_index: int

    score: float


# -----------------------------------------
# 3. Chat Response
# -----------------------------------------

class ChatResponse(BaseModel):

    conversation_id: str

    answer: str

    sources: List[SourceSchema] = Field(
        default_factory=list
    )
