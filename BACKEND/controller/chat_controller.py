
from fastapi import Request, HTTPException, status

from services.chat_service import chat_service


async def create_chat_controller(
    request: Request,
    current_user: dict,
    chat_data
):
    try:
        db = request.app.state.db

        user_id = str(current_user["_id"])

        result = await chat_service(
            db=db,
            user_id=user_id,
            query=chat_data.query,
            mode=chat_data.mode,
            document_id=chat_data.document_id,
            document_ids=chat_data.document_ids,
            conversation_id=chat_data.conversation_id
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

    except Exception as error:
        print(f"Chat controller error: {error}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process chat request"
        )
