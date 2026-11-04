
import fitz


def extract_pdf_text(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF, page by page.

    Args:
        pdf_bytes: PDF binary data.

    Returns:
        List containing page numbers and extracted text.
    """

    if not pdf_bytes:
        raise ValueError("PDF file is empty.")

    pages = []

    try:
        with fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as pdf:

            if pdf.is_encrypted:
                raise ValueError("Password-protected PDFs are not supported.")

            for page_index, page in enumerate(pdf):

                # Extract text from current page
                text = page.get_text("text").strip()

                # Store only pages containing text
                if text:
                    pages.append({
                        "page_number": page_index + 1,
                        "text": text
                    })

    except fitz.FileDataError as exc:
        raise ValueError("Invalid or corrupted PDF file.") from exc

    return pages




