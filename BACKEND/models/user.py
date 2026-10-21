from datetime import datetime, timezone
from bson import ObjectId


def create_user_document(
    name: str,
    email: str,
    hashed_password: str
) -> dict:
    return {
        "name": name,
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc),
    }


def serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }