

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def create_document_chunks(
    pages: list,
    document_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[Document]:

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    documents = []

    # Step 1: Convert every page into a Document
    for page in pages:

        page_text = page.get("text", "").strip()

        if not page_text:
            continue

        documents.append(
            Document(
                page_content=page_text,
                metadata={
                    "document_id": document_id,
                    "page_number": page["page_number"]
                }
            )
        )

    # Step 2: Split all documents
    chunks = text_splitter.split_documents(documents)

    # Step 3: Add chunk index
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index

    # Step 4: Return chunks
    return chunks
