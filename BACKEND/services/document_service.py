import asyncio
import logging
import uuid

import urllib.request
import urllib.error

from urllib.parse import quote


from fastapi.responses import Response

from pathlib import Path

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from bson import ObjectId
from bson.errors import InvalidId

from fastapi import UploadFile, HTTPException

from core.config import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    ALLOWED_FILE_TYPES
)

from models.document_model import create_document_model
from services.pdf_extraction_service import extract_pdf_text
from services.chunking_service import create_document_chunks
from services.embedding_service import generate_embeddings_async

logger=logging.getLogger(__name__)

## validate uplode file

def validate_file(file:UploadFile):

        """
    Validates the filename, extension and MIME type.

    Supported:
    PDF, JPG, JPEG, PNG and WEBP.
    """

        if not file.filename:
                raise HTTPException(status_code=400,detail="Filename is required")
        
        extension = Path(file.filename).suffix.lower()

        expected_mime = ALLOWED_FILE_TYPES.get(extension)

        if expected_mime is None:
                raise HTTPException(status_code=400,detail="Unsupported file extension")

        if file.content_type != expected_mime:
                raise HTTPException(
                   status_code=400,
                   detail="Invalid file MIME type")
        
        return extension

        

# --------------------------------------------------
# 2. Validate actual file signature
# --------------------------------------------------
def validate_file_signature(content: bytes, extension: str) -> bool:
    """
    Checks the actual file signature (magic bytes)
    to verify that the file matches its extension.
    """

    signatures = {
        ".pdf": [b"%PDF"],
        ".jpg": [b"\xff\xd8\xff"],
        ".jpeg": [b"\xff\xd8\xff"],
        ".png": [b"\x89PNG\r\n\x1a\n"],
        ".webp": [b"RIFF"],
    }

    allowed_signatures = signatures.get(extension.lower())

    if not allowed_signatures:
        return False

    # Check whether the file starts with an expected signature
    return any(
        content.startswith(signature)
        for signature in allowed_signatures
    )



# --------------------------------------------------
# 3. Generate Cloudinary delivery URL
# --------------------------------------------------

def generate_delivery_url(
    public_id: str,
    resource_type: str
):
    """
    Generates a signed Cloudinary delivery URL.

    Uses authenticated delivery so the uploaded
    files are not ordinary public assets.
    """

    url, options = cloudinary.utils.cloudinary_url(
        public_id,
        resource_type=resource_type,
        type="authenticated",
        secure=True,
        sign_url=True
    )

    return url
# --------------------------------------------------
# 4. Serialize MongoDB document
# --------------------------------------------------

def serialize_document(document: dict):
    """
    Converts MongoDB ObjectId into a string.

    Generates a delivery URL and excludes internal
    fields such as user_id and public_id.
    """

    return {
        "id": str(document["_id"]),

        "filename": document["filename"],

        "delivery_url": generate_delivery_url(
            document["public_id"],
            document["resource_type"]
        ),

        "resource_type": document["resource_type"],

        "mime_type": document["mime_type"],

        "file_size": document["file_size"],

        "status": document["status"],

        "total_pages": document.get("total_pages"),

        "total_chunks": document.get("total_chunks", 0),

        "created_at": document["created_at"]
    }


# --------------------------------------------------
# 5. Validate MongoDB document ID
# --------------------------------------------------

def validate_document_id(document_id: str):
    """
    Converts the document ID into MongoDB ObjectId.

    Returns HTTP 400 if the ID is invalid.
    """

    try:
        return ObjectId(document_id)

    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID"
        )


# --------------------------------------------------
# 6. Upload document
# --------------------------------------------------
async def upload_document_service(
    file: UploadFile,
    user_id: str,
    collection
):
    """
    Uploads PDF/image to Cloudinary and stores
    its metadata in MongoDB.

    Workflow:

    1. Validate file.
    2. Read file with size limit.
    3. Validate file signature.
    4. Select Cloudinary resource type.
    5. Generate unique public ID.
    6. Upload to Cloudinary.
    7. Save metadata in MongoDB.
    8. Return document response.

    If MongoDB insertion fails, the Cloudinary
    asset is deleted as a cleanup operation.
    """

    try:
        # Validate file extension and MIME type.
        extension = validate_file(file)

        # Read at most maximum allowed size + 1 byte.
        content = await file.read(
            MAX_FILE_SIZE_BYTES + 1
        )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        # Check maximum file size.
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"Maximum allowed file size is "
                    f"{MAX_FILE_SIZE_MB} MB"
                )
            )

        # Verify actual binary signature.
        validate_file_signature(
            content,
            extension
        )

        # Images use image resource type.
        # PDFs use raw resource type.
        resource_type = (
            "raw" if extension == ".pdf"
            else "image"
        )

        # Generate unique Cloudinary public ID.
        unique_id = str(uuid.uuid4())

        public_id = (
            f"ai_knowledge_hub/{user_id}/{unique_id}"
        )

        # Raw PDF public IDs include their extension.
        if resource_type == "raw":
            public_id += ".pdf"

        upload_result = None

        try:
            # Upload the file to Cloudinary.
            upload_result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                content,
                public_id=public_id,
                resource_type=resource_type,
                type="authenticated",
                overwrite=False,
                unique_filename=False
            )

            # Create MongoDB metadata.
            document_data = create_document_model(
                user_id=user_id,

                filename=Path(file.filename).name,

                public_id=upload_result["public_id"],

                asset_id=upload_result["asset_id"],

                resource_type=resource_type,

                mime_type=file.content_type,

                file_size=len(content)
            )

            # Save metadata in MongoDB.
            result = await collection.insert_one(
                document_data
            )

            document_data["_id"] = result.inserted_id

            return serialize_document(document_data)

        except Exception:
            # If Cloudinary succeeded but MongoDB failed,
            # remove the uploaded Cloudinary asset.
            if upload_result:
                try:
                    await asyncio.to_thread(
                        cloudinary.uploader.destroy,
                        upload_result["public_id"],
                        resource_type=resource_type,
                        type="authenticated"
                    )

                except Exception:
                    logger.exception(
                        "Cloudinary cleanup failed"
                    )

            raise

    finally:
        # Always close the uploaded file.
        await file.close()




# --------------------------------------------------
# 7. Get all user documents
# --------------------------------------------------
async def get_all_documents_service(
    user_id: str,
    collection
):
    """
    Returns all documents owned by the authenticated user.

    Sorts documents by newest first.
    """

    cursor = collection.find(
        {"user_id": user_id}
    ).sort(
        "created_at", -1
    )

    documents = []

    async for document in cursor:
        documents.append(
            serialize_document(document)
        )

    return {
        "documents": documents,
        "total": len(documents)
    }                
         

      
# --------------------------------------------------
# 8. Get document by ID
# --------------------------------------------------

async def get_document_by_id_service(
    document_id: str,
    user_id: str,
    collection
):
    """
    Retrieves one document using its MongoDB ID.

    Checks both document ID and authenticated user ID.
    """

    object_id = validate_document_id(document_id)

    document = await collection.find_one({
        "_id": object_id,
        "user_id": user_id
    })

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return serialize_document(document)


# --------------------------------------------------
# 9. Delete document
# --------------------------------------------------

async def delete_document_service(
    document_id: str,
    user_id: str,
    collection
):
    """
    Deletes a document from Cloudinary and MongoDB.

    First checks document ownership.

    Then deletes the Cloudinary file.
    Finally removes MongoDB metadata.

    If Cloudinary deletion fails, metadata remains
    so that the deletion can be retried.
    """

    object_id = validate_document_id(document_id)

    # Find only the current user's document.
    document = await collection.find_one({
        "_id": object_id,
        "user_id": user_id
    })

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    try:
        # Delete original file from Cloudinary.
        result = await asyncio.to_thread(
            cloudinary.uploader.destroy,
            document["public_id"],
            resource_type=document["resource_type"],
            type="authenticated"
        )

        if result.get("result") not in {
            "ok",
            "not found"
        }:
            raise HTTPException(
                status_code=502,
                detail="Cloudinary deletion failed"
            )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Cloudinary deletion failed"
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to delete cloud file"
        )

    # Delete MongoDB metadata.
    delete_result = await collection.delete_one({
        "_id": object_id,
        "user_id": user_id
    })

    if delete_result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Document metadata not found"
        )

    return {
        "message": "Document deleted successfully"
    }  



# --------------------------------------------------
# 10. Retrieve PDF file for preview
# --------------------------------------------------

async def get_document_file_service(
    document_id: str,
    user_id: str,
    collection
):
    """
    Retrieves an authenticated user's PDF from Cloudinary.

    Workflow:
    1. Validate MongoDB document ID.
    2. Verify document ownership.
    3. Verify PDF file type.
    4. Generate temporary signed download URL.
    5. Download PDF from Cloudinary.
    6. Return PDF binary response to frontend.
    """

    # 1. Validate MongoDB document ID
    object_id = validate_document_id(document_id)

    # 2. Find document belonging to authenticated user
    document = await collection.find_one({
        "_id": object_id,
        "user_id": user_id
    })

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # 3. Verify PDF file
    if document.get("mime_type") != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be previewed"
        )

    if document.get("resource_type") != "raw":
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF resource type"
        )

    # 4. Generate temporary authenticated download URL
    try:
        download_url = await asyncio.to_thread(
            cloudinary.utils.private_download_url,
            document["public_id"],
            "pdf",
            resource_type="raw",
            type="authenticated",
            attachment=False
        )

    except Exception:
        logger.exception(
            "Cloudinary download URL generation failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate PDF download URL"
        )

    # 5. Download PDF bytes from Cloudinary
    def download_pdf():

        with urllib.request.urlopen(
            download_url,
            timeout=60
        ) as response:

            content = response.read(
                MAX_FILE_SIZE_BYTES + 1
            )

            return content

    try:
        content = await asyncio.to_thread(download_pdf)

    except urllib.error.HTTPError as exc:

        cloudinary_error = exc.headers.get(
            "x-cld-error",
            "No additional error information"
        )

        logger.error(
            "Cloudinary download failed: HTTP %s - %s",
            exc.code,
            cloudinary_error
        )

        raise HTTPException(
            status_code=502,
            detail="Cloudinary rejected the PDF download"
        )

    except Exception:

        logger.exception(
            "Cloudinary PDF download failed"
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve PDF from Cloudinary"
        )

    # 6. Validate downloaded content
    if not content:
        raise HTTPException(
            status_code=502,
            detail="Retrieved PDF is empty"
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=502,
            detail="PDF exceeds the maximum allowed size"
        )

    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=502,
            detail="Cloudinary returned an invalid PDF"
        )

    # 7. Return PDF binary response
    filename = document["filename"]

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"inline; filename*=UTF-8''{quote(filename)}"
            ),
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "private, no-store"
        }
    )



# --------------------------------------------------
# 11. Extract PDF text, generate chunks and embeddings
# --------------------------------------------------

async def extract_document_text_service(
    document_id: str,
    user_id: str,
    collection
):
    """
    Downloads PDF from Cloudinary, extracts text,
    generates LangChain chunks and creates embeddings.

    Workflow:
    1. Validate document ID.
    2. Verify document ownership.
    3. Verify PDF file.
    4. Generate Cloudinary download URL.
    5. Download PDF bytes.
    6. Validate PDF.
    7. Extract PDF text.
    8. Generate LangChain chunks.
    9. Generate embeddings for every chunk.
    10. Attach embeddings to chunks.
    11. Return chunks with embeddings and metadata.
    """

    # 1. Validate document ID
    object_id = validate_document_id(document_id)

    # 2. Verify document ownership
    document = await collection.find_one({
        "_id": object_id,
        "user_id": user_id
    })

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # 3. Verify PDF
    if document.get("mime_type") != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    if document.get("resource_type") != "raw":
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF resource type"
        )

    # 4. Generate Cloudinary download URL
    try:
        download_url = await asyncio.to_thread(
            cloudinary.utils.private_download_url,
            document["public_id"],
            "pdf",
            resource_type="raw",
            type="authenticated",
            attachment=False
        )

    except Exception:
        logger.exception(
            "Cloudinary URL generation failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate PDF download URL"
        )

    # 5. Download PDF bytes
    def download_pdf():

        with urllib.request.urlopen(
            download_url,
            timeout=60
        ) as response:

            content = response.read(
                MAX_FILE_SIZE_BYTES + 1
            )

            return content

    try:
        pdf_bytes = await asyncio.to_thread(
            download_pdf
        )

    except Exception:
        logger.exception("PDF download failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to download PDF"
        )

    # 6. Validate PDF
    if not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(
            status_code=502,
            detail="Invalid PDF file"
        )

    if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds maximum allowed size"
        )

    # 7. Extract PDF text using PyMuPDF
    try:
        pages = await asyncio.to_thread(
            extract_pdf_text,
            pdf_bytes
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except Exception:
        logger.exception("PDF text extraction failed")

        raise HTTPException(
            status_code=422,
            detail="Unable to extract PDF text"
        )

    if not pages:
        raise HTTPException(
            status_code=422,
            detail=(
                "No extractable text found in PDF. "
                "It may be scanned."
            )
        )

    # 8. Generate LangChain chunks
    try:
        chunks = await asyncio.to_thread(
            create_document_chunks,
            pages=pages,
            document_id=document_id,
            chunk_size=1000,
            chunk_overlap=200
        )

    except Exception:
        logger.exception("Document chunking failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate document chunks"
        )

    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="No chunks generated from PDF"
        )

    # 9. Generate embeddings for all chunks
    try:

        # Extract text from LangChain Document objects
        chunk_texts = [
            chunk.page_content
            for chunk in chunks
        ]

        # Call embedding_service.py
        embeddings = await generate_embeddings_async(
            chunk_texts
        )

        # Validate embedding count
        if len(embeddings) != len(chunks):
            raise ValueError(
                "Number of embeddings does not match number of chunks"
            )

        # Validate embedding dimensions
        if any(len(embedding) != 384 for embedding in embeddings):
            raise ValueError(
                "Invalid embedding dimensions"
            )

    except Exception:
        logger.exception("Embedding generation failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate document embeddings"
        )

    # 10. Attach embeddings to corresponding chunks
    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings):

        embedded_chunks.append({
            "chunk_index": chunk.metadata["chunk_index"],

            "page_number": chunk.metadata["page_number"],

            "text": chunk.page_content,

            "embedding": embedding,

            "metadata": chunk.metadata
        })

    # 11. Return chunks with embeddings
    return {
        "document_id": document_id,

        "total_pages_extracted": len(pages),

        "total_chunks": len(chunks),

        "embedding_dimension": 384,

        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",

        "chunks": embedded_chunks
    }
