from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from pymongo.errors import DuplicateKeyError

from core.config import (
    ACCESS_TOKEN_MINUTES,
    COOKIE_SECURE,
)
from core.csrf import set_csrf_cookie, verify_csrf
from core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from dependencies.auth import get_current_user
from models.user import (
    create_user_document,
    serialize_user,
)
from schema.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    MessageResponse,
    CsrfResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
#APIRouter lets you organize related API endpoints in a separate file instead of putting every endpoint inside main.py.


def set_auth_cookie(response: Response, user_id: str):
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


@router.get("/csrf", response_model=CsrfResponse)
async def get_csrf_token(response: Response):
    token = set_csrf_cookie(response)
    return {"csrf_token": token}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    #response_model=UserResponse
    #This tells FastAPI what the response should look like.

    #FastAPI validates the returned data against this schema and uses it to generate API documentation. Response models also filter output to the declared fields, helping prevent accidental exposure of sensitive data.

    #status_code=status.HTTP_201_CREATED
    #When registration succeeds, FastAPI returns HTTP status 201 Created.
    #This tells the frontend that a new resource—the user account—was #successfully created.
)
async def register(
    data: RegisterRequest,
    request: Request,
    #This represents the incoming HTTP request. You use it to access the database handle stored in your FastAPI application's state and to verify the CSRF token.

    #This represents the outgoing HTTP response. You pass it to set_auth_cookie() so the browser receives the authentication cookie.
    response: Response,
    #Notice that data is the actual registration data, while request and response are FastAPI objects.
):
    await verify_csrf(request)

    db = request.app.state.db
    """
    request — the incoming HTTP request.


request.app — the FastAPI application handling the request.

request.app.state — the application's state storage.

request.app.state.db — the database handle your application saved there during startup.
    """
    email = str(data.email).lower()

    document = create_user_document(
        name=data.name.strip(),
        email=email,
        hashed_password=hash_password(data.password),
    )

    try:
        result = await db["users"].insert_one(document)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user_id = str(result.inserted_id)
    set_auth_cookie(response, user_id)

    return {
        "id": user_id,
        "name": document["name"],
        "email": document["email"],
    }


@router.post("/login", response_model=UserResponse)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
):
    await verify_csrf(request)

    db = request.app.state.db
    email = str(data.email).lower()

    user = await db["users"].find_one({"email": email})

    # Same message for an unknown email and wrong password.
    if not user or not verify_password(
        data.password,
        user["hashed_password"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    set_auth_cookie(response, str(user["_id"]))
    return serialize_user(user)


@router.get("/me", response_model=UserResponse)
async def me(user: dict = Depends(get_current_user)):
    return serialize_user(user)


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(
    request: Request,
    response: Response,
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


"""
Why send the same token twice?
A browser may automatically send cookies with certain cross-site requests. However, another website generally cannot read your application's CSRF cookie and reproduce its value in the custom header because of browser security restrictions.
Requiring both values helps the backend detect requests that lack the expected token.
Important: matching tokens alone is not a complete security guarantee. The CSRF token must be generated securely, and your application should configure CORS, cookie attributes and origin protections correctly.
Remember this flow
React sends the CSRF token in a header → browser sends the CSRF cookie → FastAPI compares both values → matching tokens pass this check.
And remember: CSRF verification is separate from JWT authentication. Your verify_csrf(request) checks the request's CSRF protection; get_current_user validates the user's authentication.
"""