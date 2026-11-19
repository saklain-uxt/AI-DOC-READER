
from fastapi import HTTPException

from services.conversation_service import (
    get_user_conversations,
    get_conversation_messages,
    delete_conversation
)

# --------------------------------------------------
# 1. GET ALL USER CONVERSATIONS
# --------------------------------------------------

async def get_user_conversations_controller(
    request,
    current_user
):
    try:
        db = request.app.state.db

        user_id = str(current_user["_id"])

        conversations = await get_user_conversations(
            db=db,
            user_id=user_id
        )

        return {
            "total": len(conversations),
            "conversations": conversations
        }

    except Exception as error:
        print(f"Get conversations error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve conversations"
        )

# --------------------------------------------------
# 2. GET CONVERSATION MESSAGES
# --------------------------------------------------

async def get_conversation_messages_controller(
    request,
    conversation_id,
    current_user
):
    try:
        db = request.app.state.db

        user_id = str(current_user["_id"])

        result = await get_conversation_messages(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:
        print(f"Get conversation messages error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve conversation messages"
        )

# --------------------------------------------------
# 3. DELETE CONVERSATION
# --------------------------------------------------

async def delete_conversation_controller(
    request,
    conversation_id,
    current_user
):
    try:
        db = request.app.state.db

        user_id = str(current_user["_id"])

        result = await delete_conversation(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:
        print(f"Delete conversation error: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to delete conversation"
        )