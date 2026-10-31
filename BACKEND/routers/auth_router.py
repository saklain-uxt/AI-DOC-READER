


from fastapi import APIRouter, Request, Response, status, Depends

from dependencies.auth import get_current_user

from controller.auth_controller import (
    get_csrf_token,
    register_user,
    login_user,
    get_me,
    logout_user,
)

from schema.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    MessageResponse,
    CsrfResponse
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.get("/csrf", response_model=CsrfResponse)
async def csrf_endpoint(response: Response):
    return await get_csrf_token(response)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_endpoint(
    data: RegisterRequest,
    response: Response,
    request: Request
):
    return await register_user(data, response, request)


@router.post("/login", response_model=UserResponse)
async def login_endpoint(
    data: LoginRequest,
    response: Response,
    request: Request
):
    return await login_user(data, response, request)


@router.get("/me", response_model=UserResponse)
async def me_endpoint(
    user: dict = Depends(get_current_user)
):
    return await get_me(user)


@router.post("/logout", response_model=MessageResponse)
async def logout_endpoint(
    request: Request,
    response: Response
):
    return await logout_user(request, response)
