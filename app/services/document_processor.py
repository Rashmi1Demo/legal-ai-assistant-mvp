from io import BytesIO
from pathlib import Path
from typing import Iterable

from docx import Document
from pypdf import PdfReader

import os
import pytesseract
from pdf2image import convert_from_bytes
from dotenv import load_dotenv


load_dotenv()

TESSERACT_CMD = os.getenv("TESSERACT_CMD")
POPPLER_PATH = os.getenv("POPPLER_PATH")

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


class DocumentProcessingError(ValueError):
    pass


def _normalize_text(text: str) -> str:
    lines = [
        line.strip()
        for line in text.replace("\r", "\n").split("\n")
    ]

    cleaned = "\n".join(
        line for line in lines if line
    )

    return cleaned.strip()


# --------------------------------------------------
# OCR FALLBACK FOR SCANNED PDFs
# --------------------------------------------------
def extract_text_with_ocr(pdf_bytes: bytes) -> str:

    images = convert_from_bytes(
        pdf_bytes,
        dpi=300,
        poppler_path=POPPLER_PATH
    )

    ocr_text = []

    for image in images:

        text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

        if text.strip():
            ocr_text.append(text.strip())

    return "\n\n".join(ocr_text)


# --------------------------------------------------
# DOCUMENT TEXT EXTRACTION
# --------------------------------------------------
def extract_text_from_bytes(
    filename: str,
    content: bytes
) -> str:

    suffix = Path(filename).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise DocumentProcessingError(
            f"Unsupported file type "
            f"'{suffix or 'unknown'}'. "
            f"Use PDF, DOCX, or TXT."
        )

    if not content:
        raise DocumentProcessingError(
            f"'{filename}' is empty."
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise DocumentProcessingError(
            f"'{filename}' exceeds the 10 MB demo limit."
        )

    try:

        # -------------------------------
        # TXT
        # -------------------------------
        if suffix == ".txt":

            text = content.decode(
                "utf-8-sig",
                errors="replace"
            )

        # -------------------------------
        # DOCX
        # -------------------------------
        elif suffix == ".docx":

            document = Document(BytesIO(content))

            parts = [
                p.text
                for p in document.paragraphs
            ]

            for table in document.tables:
                for row in table.rows:

                    parts.append(
                        " | ".join(
                            cell.text
                            for cell in row.cells
                        )
                    )

            text = "\n".join(parts)

        # -------------------------------
        # PDF
        # -------------------------------
        else:

            reader = PdfReader(BytesIO(content))

            text = "\n".join(
                (page.extract_text() or "")
                for page in reader.pages
            )

            normalized_preview = _normalize_text(text)

            # If normal PDF extraction finds
            # almost no text, try OCR.
            if len(normalized_preview) < 50:

                text = extract_text_with_ocr(
                    content
                )

    except Exception as exc:

        raise DocumentProcessingError(
            f"Could not extract text from "
            f"'{filename}': {exc}"
        ) from exc

    text = _normalize_text(text)

    if not text:

        raise DocumentProcessingError(
            f"No readable text could be extracted "
            f"from '{filename}', including OCR processing."
        )

    return text


# --------------------------------------------------
# COMBINE MULTIPLE DOCUMENTS
# --------------------------------------------------
def combine_documents(
    documents: Iterable[tuple[str, str]]
) -> str:

    sections = []

    for filename, text in documents:

        sections.append(
            f"===== DOCUMENT: {filename} =====\n{text}"
        )

    return "\n\n".join(sections).strip()