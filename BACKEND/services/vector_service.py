from datetime import datetime, timezone
from pymongo import ReplaceOne


EMBEDDING_DIMENSION = 384


async def store_document_chunks(
    chunks: list,
    document_id: str,
    user_id: str,
    collection
):
    """
    Store embedded document chunks in MongoDB.
    Existing chunks are updated when the document is reindexed.
    """

    if not chunks:
        raise ValueError("No chunks provided")

    documents = []
    chunk_indices = set()

    # 1. Prepare and validate documents
    for chunk in chunks:

        embedding = chunk.get("embedding")
        chunk_index = chunk.get("chunk_index")

        if not isinstance(embedding, list):
            raise ValueError("Invalid embedding format")

        if len(embedding) != EMBEDDING_DIMENSION:
            raise ValueError("Invalid embedding dimensions")

        if not isinstance(chunk_index, int) or chunk_index < 0:
            raise ValueError("Invalid chunk index")

        if chunk_index in chunk_indices:
            raise ValueError("Duplicate chunk index")

        if not isinstance(chunk.get("text"), str) or not chunk["text"].strip():
            raise ValueError("Invalid chunk text")

        if not all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            for value in embedding
        ):
            raise ValueError("Invalid embedding values")

        chunk_indices.add(chunk_index)

        documents.append({
            "document_id": document_id,
            "user_id": user_id,
            "chunk_index": chunk_index,
            "page_number": chunk.get("page_number"),
            "text": chunk["text"],
            "embedding": embedding,
            "metadata": chunk.get("metadata", {}),
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "created_at": datetime.now(timezone.utc)
        })

    # 2. Upsert chunks
    #this is list comprehension
    operations = [
        ReplaceOne(
            {
                "document_id": document_id,
                "user_id": user_id,
                "chunk_index": doc["chunk_index"]
            },
            doc,
            upsert=True
            #Without upsert=True, MongoDB would simply do nothing if no matching document existed.
        )
        for doc in documents
    ]

    result = await collection.bulk_write(
        operations,
        ordered=False
    )

    # 3. Remove outdated chunks
    await collection.delete_many({
        "document_id": document_id,
        "user_id": user_id,
        "chunk_index": {"$nin": list(chunk_indices)}#$nin means NOT IN.
    })

    return {
        "total_chunks_stored": len(documents),
        "inserted": result.upserted_count,
        "updated": result.modified_count
    }