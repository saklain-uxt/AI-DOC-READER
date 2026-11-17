
from fastapi import APIRouter, Depends, Request

from schema.chat_schema import ChatRequest, ChatResponse
from controller.chat_controller import create_chat_controller

from dependencies.auth import get_current_user


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
async def create_chat(
    request: Request,
    chat_data: ChatRequest,
    current_user: dict = Depends(get_current_user)
):

    return await create_chat_controller(
        request=request,
        current_user=current_user,
        chat_data=chat_data
    )
