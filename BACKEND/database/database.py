from contextlib import asynccontextmanager

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

        # Each email must be unique.
        await app.state.db["users"].create_index(
            "email",
            unique=True
        )

        yield

    finally:
        await client.close()