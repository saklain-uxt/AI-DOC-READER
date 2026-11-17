from services.embedding_service import generate_embedding_async
from typing import Any


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
    document_id: str | None=None,
    document_ids: list[str] | None= None,
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
    #isinstance() is a built-in Python function used to check the data type of a variable.
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
    search_filter:dict[str,Any]={
        "user_id":user_id
    }

    if document_id:
         search_filter["document_id"] = document_id

    elif document_ids:
        search_filter["document_id"] ={
             "$in": document_ids
        }
   

        
    


    # Step 6: Build MongoDB aggregation pipeline
    #In MongoDB, an aggregation pipeline is a sequence of stages. Each stage performs an operation on the data and passes its output to the next stage.
    #-----------------------------------------
    #$vectorSearch → Finds relevant chunks.
    #$project → Selects the required fields.
    #---------------------------------------
    
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
    #aggregate() executes your aggregation pipeline against the collection.
    #A cursor is an object that lets you retrieve query results.
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
