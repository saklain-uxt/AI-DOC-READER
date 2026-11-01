from datetime import datetime, timezone


def create_document_model(
    user_id: str,
    filename: str,
    public_id: str,
    asset_id: str,
    resource_type: str,
    mime_type: str,
    file_size: int
):
    """
    Creates a document metadata dictionary.

    The actual PDF/image is stored in Cloudinary.

    MongoDB stores:
    - Document owner
    - Original filename
    - Cloudinary public ID
    - Cloudinary asset ID
    - File information
    - RAG processing status
    """

    now = datetime.now(timezone.utc)

    return {
        "user_id": user_id,

        "filename": filename,

        "public_id": public_id,

        "asset_id": asset_id,

        "resource_type": resource_type,

        "mime_type": mime_type,

        "file_size": file_size,

        # Cloudinary authenticated delivery
        "delivery_type": "authenticated",

        # Future RAG processing fields
        "status": "uploaded",

        "total_pages": None,

        "total_chunks": 0,

        "created_at": now,

        "updated_at": now
    }




