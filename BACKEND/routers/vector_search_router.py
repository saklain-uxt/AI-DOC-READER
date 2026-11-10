
from fastapi import APIRouter, Request, Depends

from dependencies.auth import get_current_user

from schema.vector_search_schema import (
    SemanticSearchRequest
)

from controller.vector_search_controller import (
    semantic_search_controller
)


router = APIRouter(prefix="/api/vector-search",
    tags=["Vector Search"])


# --------------------------------------------------
# POST: Semantic Search
# --------------------------------------------------

@router.post("/search")
async def semantic_search(
    search_request: SemanticSearchRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):

    vector_collection = request.app.state.db[
        "document_chunks"
    ]

    return await semantic_search_controller(
        search_request=search_request,
        current_user=current_user,
        collection=vector_collection
    )
