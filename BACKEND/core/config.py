import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.environ["MONGODB_URI"]
MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "ai_knowledge_hub"
)

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_MINUTES = int(
    os.getenv("ACCESS_TOKEN_MINUTES", "30")
)

COOKIE_SECURE = (
    os.getenv("COOKIE_SECURE", "false").lower() == "true"
)

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173"
)



# ==============================
# Cloudinary Configuration
# ==============================

CLOUDINARY_CLOUD_NAME = os.environ["CLOUDINARY_CLOUD_NAME"]

CLOUDINARY_API_KEY = os.environ["CLOUDINARY_API_KEY"]

CLOUDINARY_API_SECRET = os.environ["CLOUDINARY_API_SECRET"]


# ==============================
# Document Upload Configuration
# ==============================

MAX_FILE_SIZE_MB = int(
    os.getenv("MAX_FILE_SIZE_MB", "10")
)

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# Allowed document types
# Supported document types
ALLOWED_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp"
}