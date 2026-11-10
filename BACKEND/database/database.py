from contextlib import asynccontextmanager
from core.cloudinary_config import configure_cloudinary

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from core.config import (
    MONGODB_URI,
    MONGODB_DATABASE,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncMongoClient(MONGODB_URI)

    try:
        await client.admin.command("ping")

        app.state.mongo_client = client
        app.state.db = client[MONGODB_DATABASE]
        configure_cloudinary()

        # Each email must be unique.
        await app.state.db["users"].create_index(
            "email",
            unique=True
        )

        # Index documents by user and creation date
        await app.state.db["documents"].create_index(
            [("user_id", 1), ("created_at", -1)]
        )
          # 3. Document chunks collection
        await app.state.db["document_chunks"].create_index(
            [
                ("user_id", 1),
                ("document_id", 1),
                ("chunk_index", 1)
            ],
            unique=True
        )

        yield

    finally:
        await client.close()