from fastapi import HTTPException

from services.document_service import (
    upload_document_service,
    get_all_documents_service,
    get_document_by_id_service,
    delete_document_service

      
)

def extract_user_id(current_user: dict) -> str:
    """
    Extracts the authenticated user's ID.

    Supports both MongoDB _id and id fields.
    """

    user_id = (
        current_user.get("_id")
        or current_user.get("id")
    )

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID not found"
        )

    return str(user_id)



async def upload_document_controller(
    file,
    current_user,
    collection
):
    """
    Handles document upload requests.

    Extracts the user ID and forwards the
    file to the document service.
    """

    user_id = extract_user_id(current_user)

    return await upload_document_service(
        file=file,
        user_id=user_id,
        collection=collection
    )


async def get_all_documents_controller(
    current_user,
    collection
):
    """
    Handles requests to retrieve all user documents.
    """

    user_id = extract_user_id(current_user)

    return await get_all_documents_service(
        user_id=user_id,
        collection=collection
    )



async def get_document_by_id_controller(
    document_id,
    current_user,
    collection
):
    """
    Handles requests to retrieve one document.
    """

    user_id = extract_user_id(current_user)

    return await get_document_by_id_service(
        document_id=document_id,
        user_id=user_id,
        collection=collection
    )


async def delete_document_controller(
    document_id,
    current_user,
    collection
):
    """
    Handles document deletion requests.

    Ensures the operation uses the authenticated
    user's identity.
    """

    user_id = extract_user_id(current_user)

    return await delete_document_service(
        document_id=document_id,
        user_id=user_id,
        collection=collection
    )
