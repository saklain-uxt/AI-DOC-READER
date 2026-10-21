from bson import ObjectId
from fastapi import Depends, HTTPException, Request, status
from jwt.exceptions import InvalidTokenError

from core.csrf import verify_csrf
from core.security import decode_access_token


async def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id or not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")

    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = await request.app.state.db["users"].find_one(
        {"_id": ObjectId(user_id)}
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    return user


async def get_current_user_with_csrf(
    request: Request,
    user: dict = Depends(get_current_user),
):
    await verify_csrf(request)
    return user


#You'll use Depends(get_current_user) on protected read-only routes. For state-changing routes that require a logged-in user, use Depends(get_current_user_with_csrf).