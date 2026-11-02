from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    Request
)

# Existing authentication dependency.
from dependencies.auth import get_current_user

# Existing CSRF protection.
from core.csrf import verify_csrf

# Document controllers.
from controller.document_controller import (
    upload_document_controller,
    get_all_documents_controller,
    get_document_by_id_controller,
    delete_document_controller,
    get_document_file_controller
)

# Response schemas.
from schema.document_schema import (
    DocumentResponse,
    DocumentListResponse,
    MessageResponse
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)



async def require_csrf(request: Request):
    """
    Reuses existing CSRF verification.

    Rejects state-changing requests if CSRF
    verification fails.
    """
    await verify_csrf(request)

     



@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
    dependencies=[Depends(require_csrf)]
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    POST /api/documents/upload

    Uploads PDF or image files.
    """

    collection = request.app.state.db["documents"]

    return await upload_document_controller(
        file=file,
        current_user=current_user,
        collection=collection
    )    


@router.get(
    "/",
    response_model=DocumentListResponse
)
async def get_all_documents(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/documents/

    Returns all documents belonging to the user.
    """

    collection = request.app.state.db["documents"]

    return await get_all_documents_controller(
        current_user=current_user,
        collection=collection
    )    



@router.get(
    "/{document_id}",
    response_model=DocumentResponse
)
async def get_document_by_id(
    document_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/documents/{document_id}

    Returns details of a specific document.
    """

    collection = request.app.state.db["documents"]

    return await get_document_by_id_controller(
        document_id=document_id,
        current_user=current_user,
        collection=collection
    )



@router.delete(
    "/{document_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_csrf)]
)
async def delete_document(
    document_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    DELETE /api/documents/{document_id}

    Deletes a document from Cloudinary
    and its metadata from MongoDB.
    """

    collection = request.app.state.db["documents"]

    return await delete_document_controller(
        document_id=document_id,
        current_user=current_user,
        collection=collection
    )

@router.get("/{document_id}/file")
async def get_document_file(
    document_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    GET /api/documents/{document_id}/file

    Retrieves the actual PDF file for preview.
    """

    collection = request.app.state.db["documents"]

    return await get_document_file_controller(
        document_id=document_id,
        current_user=current_user,
        collection=collection
    )    