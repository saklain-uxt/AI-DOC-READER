
from fastapi import HTTPException

from controller.document_controller import extract_user_id
import logging

logger = logging.getLogger(__name__)

from services.vector_search_service import (
    semantic_search_service
)


# --------------------------------------------------
# 1. Semantic search controller
# --------------------------------------------------
async def semantic_search_controller(
    search_request,
    current_user: dict,
    collection
):
    user_id = extract_user_id(current_user)

    try:

        result = await semantic_search_service(
            query=search_request.query,
            user_id=user_id,
            document_id=search_request.document_id,
            limit=search_request.limit,
            collection=collection
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception:

        logger.exception(
            "Semantic search failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to perform semantic search"
        )