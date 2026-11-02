from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import FRONTEND_ORIGIN
from database.database import lifespan
from routers.auth_router import router as auth_router
from routers.document_router import router as document_router


app = FastAPI(
    title="AI Knowledge Hub API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

app.include_router(auth_router)
app.include_router(document_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}