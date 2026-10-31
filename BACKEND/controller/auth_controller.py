
from fastapi import HTTPException, Response, Request, status
from pymongo.errors import DuplicateKeyError

from core.config import ACCESS_TOKEN_MINUTES, COOKIE_SECURE
from core.csrf import set_csrf_cookie, verify_csrf
from core.security import verify_password, hash_password, create_access_token
from models.user import create_user_document, serialize_user


# Always use the same collection
USERS_COLLECTION = "users"


# -------------------------
# Authentication Cookies
# -------------------------

async def set_auth_cokkies(response: Response, user_id: str):
    token = create_access_token(user_id)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
        max_age=ACCESS_TOKEN_MINUTES * 60,
    )


# -------------------------
# CSRF Token
# -------------------------

async def get_csrf_token(response: Response):
    token = set_csrf_cookie(response)

    return {"csrf_token": token}


# -------------------------
# Register User
# -------------------------

async def register_user(
    data,
    response: Response,
    request: Request
):
    await verify_csrf(request)

    db = request.app.state.db
    users = db[USERS_COLLECTION]

    email = str(data.email).lower().strip()

    document = create_user_document(
        name=data.name.strip(),
        email=email,
        hashed_password=hash_password(data.password)
    )

    try:
        result = await users.insert_one(document)

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    user_id = str(result.inserted_id)

    await set_auth_cokkies(response, user_id)

    print("REGISTER DATABASE:", db.name)
    print("REGISTER COLLECTION:", users.name)
    print("REGISTERED USER ID:", user_id)

    return {
        "id": user_id,
        "name": document["name"],
        "email": document["email"],
    }


# -------------------------
# Login User
# -------------------------

async def login_user(
    data,
    response: Response,
    request: Request
):
    await verify_csrf(request)

    db = request.app.state.db
    users = db[USERS_COLLECTION]

    email = str(data.email).lower().strip()

    print("LOGIN DATABASE:", db.name)
    print("LOGIN COLLECTION:", users.name)
    print("LOGIN EMAIL:", email)

    # Find user by email
    user = await users.find_one({
        "email": email
    })

    print("USER FOUND:", user is not None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        data.password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Confirm user exists
    check_user = await users.find_one({
        "_id": user["_id"]
    })

    print("LOGIN USER ID:", user["_id"])
    print("USER EXISTS IN LOGIN:", check_user is not None)

    # Set authentication cookie
    await set_auth_cokkies(
        response,
        str(user["_id"])
    )

    return serialize_user(user)


# -------------------------
# Get Current User
# -------------------------

async def get_me(current_user: dict):
    return serialize_user(current_user)


# -------------------------
# Logout User
# -------------------------

async def logout_user(
    request: Request,
    response: Response
):
    await verify_csrf(request)

    response.delete_cookie(
        key="access_token",
        path="/",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key="csrf_token",
        path="/",
        secure=COOKIE_SECURE,
        httponly=False,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}












