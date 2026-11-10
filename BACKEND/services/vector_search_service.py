from services.embedding_service import generate_embedding_async


# -----------------------------------------
# 1. Configuration
# -----------------------------------------

VECTOR_INDEX_NAME = "document_chunks_vector_index"

EMBEDDING_DIMENSION = 384

DEFAULT_LIMIT = 5

DEFAULT_NUM_CANDIDATES = 100




# -----------------------------------------
# 2. Semantic search
# -----------------------------------------

async def semantic_search_service(
    query: str,
    user_id: str,
    collection,
    document_id: str = None,
    limit: int = DEFAULT_LIMIT
):
    """
    Search relevant document chunks using
    MongoDB Atlas Vector Search.

    Supports:
    1. Search within a specific document.
    2. Search across all user documents.
    """

    # Step 1: Validate query
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty")

    # Step 2: Generate query embedding
    query_embedding = await generate_embedding_async(
        query.strip()
    )

    # Step 3: Validate embedding dimensions
    if len(query_embedding) != EMBEDDING_DIMENSION:
        raise ValueError("Invalid embedding dimensions")

    # Step 4: Build search filter
    search_filter = {
        "user_id": user_id
    }

    # Step 5: Apply document filter if provided
    if document_id:
        search_filter["document_id"] = document_id

    # Step 6: Build MongoDB aggregation pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": max(
                    DEFAULT_NUM_CANDIDATES,
                    limit * 20
                ),
                "limit": limit,
                "filter": search_filter
            }
        },
        {
            "$project": {
                "_id": 0,
                "document_id": 1,
                "user_id": 1,
                "chunk_index": 1,
                "page_number": 1,
                "text": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]

    # Step 7: Execute vector search
    cursor = await collection.aggregate(pipeline)

    # Step 8: Retrieve results
    results = await cursor.to_list(
        length=limit

    )
    


    

    # Step 8: Return results
    return {
        "query": query,
        "document_id": document_id,
        "total_results": len(results),
        "results": results
    }
