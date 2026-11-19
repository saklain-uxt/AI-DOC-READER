
from fastapi import APIRouter, Depends, Request

from schema.chat_schema import ChatRequest, ChatResponse
from controller.chat_controller import create_chat_controller

from controller.conversation_controller import (
    get_user_conversations_controller,
    get_conversation_messages_controller,
    delete_conversation_controller
)

from dependencies.auth import get_current_user


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


# --------------------------------------------------
# 1. CREATE CHAT / SEND MESSAGE
# --------------------------------------------------

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


# --------------------------------------------------
# 2. GET ALL USER CONVERSATIONS
# --------------------------------------------------

@router.get("/conversations")
async def get_user_conversations(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    return await get_user_conversations_controller(
        request=request,
        current_user=current_user
    )


# --------------------------------------------------
# 3. GET CONVERSATION MESSAGES
# --------------------------------------------------

@router.get("/conversations/{conversation_id}")
async def get_conversation_messages(
    request: Request,
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await get_conversation_messages_controller(
        request=request,
        conversation_id=conversation_id,
        current_user=current_user
    )


# --------------------------------------------------
# 4. DELETE CONVERSATION
# --------------------------------------------------

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    request: Request,
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await delete_conversation_controller(
        request=request,
        conversation_id=conversation_id,
        current_user=current_user
    )
