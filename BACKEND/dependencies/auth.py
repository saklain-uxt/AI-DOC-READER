
from fastapi import Request, HTTPException, status
from bson import ObjectId
from jwt.exceptions import InvalidTokenError

from core.security import decode_access_token


async def get_current_user(request: Request):

    # 1. Get access token from cookie
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # 2. Decode JWT
    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if not user_id or not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")

    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # 3. Get MongoDB collection
    db = request.app.state.db
    users = db["users"]

    # 4. Find complete user document
    user = await users.find_one({
        "_id": ObjectId(user_id)
    })

    # 5. Check whether user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )

    # 6. Return complete user document
    return user
