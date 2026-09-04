"""
document_service.py
-------------------
Responsibility: Turn an uploaded file into a list of text chunks.

Why do we chunk?
  A language model has a limited "context window" (how much text it can read
  at once).  Instead of sending the ENTIRE document to the model, we break it
  into small, overlapping pieces and only send the most relevant ones.

RAG Step: This service feeds Step 1 (before we store anything in ChromaDB).

Supported file types:
  .txt, .md, .csv, .log   → Plain text (UTF-8 decode)
  .json                    → JSON (pretty-printed for readability)
  .docx                    → Word documents (python-docx)
  .pdf                     → PDF documents (PyPDF2)
  .pptx                    → PowerPoint presentations (python-pptx)
  .html, .htm              → HTML (BeautifulSoup strips tags)
"""

import io
import json
import re

from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.logger import get_logger

logger = get_logger()

# ── Constants ─────────────────────────────────────────────────────────────────
# Students: try changing these numbers and re-uploading a document to see
# how the chunk count changes.

CHUNK_SIZE = 500       # Maximum number of characters per chunk.
CHUNK_OVERLAP = 50     # How many characters are SHARED between two neighbours.
                       # Overlap helps the model understand context at boundaries.

# File extensions grouped by how we extract text from them.
PLAIN_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".log"}
DOCX_EXTENSIONS       = {".docx"}
PDF_EXTENSIONS        = {".pdf"}
PPTX_EXTENSIONS       = {".pptx"}
HTML_EXTENSIONS       = {".html", ".htm"}
JSON_EXTENSIONS       = {".json"}


# ── File-type specific readers ────────────────────────────────────────────────

def _read_plain_text(raw_bytes: bytes) -> str:
    """Decode raw bytes as UTF-8 plain text."""
    return raw_bytes.decode("utf-8", errors="replace")


def _read_docx(raw_bytes: bytes) -> str:
    """Extract text from a .docx Word document.

    A .docx file is a ZIP archive containing XML files.
    python-docx parses the XML and gives us the text paragraph by paragraph.
    """
    from docx import Document

    # python-docx needs a file-like object, so we wrap the bytes in BytesIO.
    doc = Document(io.BytesIO(raw_bytes))

    # Each paragraph is a block of text (heading, body, bullet, etc.).
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]

    return "\n\n".join(paragraphs)


def _read_pdf(raw_bytes: bytes) -> str:
    """Extract text from a .pdf document.

    PyPDF2 reads each page and extracts selectable text.
    Note: This does NOT work for scanned/image-only PDFs — those need OCR.
    """
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(raw_bytes))
    pages_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text and page_text.strip():
            pages_text.append(page_text.strip())

    return "\n\n".join(pages_text)


def _read_pptx(raw_bytes: bytes) -> str:
    """Extract text from a .pptx PowerPoint presentation.

    Each slide can have multiple text frames (title, body, text boxes).
    We extract all of them, slide by slide.
    """
    from pptx import Presentation

    prs = Presentation(io.BytesIO(raw_bytes))
    slides_text = []

    for slide_number, slide in enumerate(prs.slides, start=1):
        slide_parts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        slide_parts.append(text)

        if slide_parts:
            slides_text.append(f"[Slide {slide_number}]\n" + "\n".join(slide_parts))

    return "\n\n".join(slides_text)


def _read_html(raw_bytes: bytes) -> str:
    """Extract visible text from an HTML file by stripping all tags."""
    from bs4 import BeautifulSoup

    html_text = raw_bytes.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html_text, "html.parser")

    # Remove script and style elements — they contain code, not content.
    for element in soup(["script", "style"]):
        element.decompose()

    return soup.get_text(separator="\n", strip=True)


def _read_json(raw_bytes: bytes) -> str:
    """Convert a JSON file into a readable text representation.

    JSON files are structured data (not prose), so we pretty-print them
    to make them readable for the LLM while preserving structure.
    """
    text = raw_bytes.decode("utf-8", errors="replace")
    parsed = json.loads(text)
    return json.dumps(parsed, indent=2, ensure_ascii=False)


# ── Text cleaning ────────────────────────────────────────────────────────────

def _clean_extracted_text(text: str) -> str:
    """Clean up extracted text to remove noise before chunking.

    This catches:
      - Binary garbage that slipped through (non-printable characters)
      - Excessive whitespace / blank lines
      - Control characters (except newlines and tabs)
    """
    # Step 1: Remove non-printable / control characters (keep \n, \t, \r, and space).
    # This catches binary garbage like the garbled .docx bytes we saw earlier.
    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]', '', text)

    # Step 2: Collapse runs of 3+ blank lines into 2 (keeps paragraph spacing).
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Step 3: Strip leading/trailing whitespace from each line.
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Step 4: Strip the whole string.
    text = text.strip()

    return text


def _is_garbage_text(text: str) -> bool:
    """Check if the extracted text is mostly binary garbage.

    Heuristic: if more than 30% of the characters are replacement characters (�)
    or non-ASCII non-printable, the extraction likely failed.
    """
    if not text:
        return True

    # Count "suspicious" characters (replacement char, null, etc.)
    suspicious = sum(1 for ch in text if ch == '\ufffd' or ord(ch) < 32 and ch not in '\n\t\r')
    ratio = suspicious / len(text)

    return ratio > 0.3


# ── Main public functions ─────────────────────────────────────────────────────

def read_text_from_uploaded_file(uploaded_file: UploadFile) -> str:
    """Read the uploaded file and extract clean text based on file type.

    Detects the file extension and uses the appropriate parser to extract
    human-readable text. Falls back to plain-text decoding for unknown types.

    Args:
        uploaded_file: The file object FastAPI gives us from the request.

    Returns:
        A single cleaned string with the complete file contents.

    Raises:
        ValueError: If the file type is unsupported or the extracted text
                    appears to be binary garbage.
    """
    # .file is a file-like object (same as open() in Python).
    raw_bytes = uploaded_file.file.read()
    filename = uploaded_file.filename or "unknown"

    # Get the file extension (lowercase), e.g. ".docx", ".pdf"
    extension = ""
    if "." in filename:
        extension = "." + filename.rsplit(".", 1)[-1].lower()

    logger.info("PARSE    file=%s  extension=%s  size_bytes=%d", filename, extension, len(raw_bytes))

    # ── Route to the correct parser based on file type ────────────────────
    if extension in DOCX_EXTENSIONS:
        extracted_text = _read_docx(raw_bytes)

    elif extension in PDF_EXTENSIONS:
        extracted_text = _read_pdf(raw_bytes)

    elif extension in PPTX_EXTENSIONS:
        extracted_text = _read_pptx(raw_bytes)

    elif extension in HTML_EXTENSIONS:
        extracted_text = _read_html(raw_bytes)

    elif extension in JSON_EXTENSIONS:
        extracted_text = _read_json(raw_bytes)

    elif extension in PLAIN_TEXT_EXTENSIONS:
        extracted_text = _read_plain_text(raw_bytes)

    else:
        # Unknown extension — try plain text as a fallback.
        logger.warning(
            "PARSE    Unknown extension '%s' for file '%s'. Trying plain text.",
            extension, filename,
        )
        extracted_text = _read_plain_text(raw_bytes)

    # ── Clean the text ────────────────────────────────────────────────────
    cleaned_text = _clean_extracted_text(extracted_text)

    # ── Validate: reject if the text is mostly binary garbage ─────────────
    if _is_garbage_text(cleaned_text):
        raise ValueError(
            f"Could not extract readable text from '{filename}'. "
            f"The file may be corrupted, password-protected, or in an unsupported format."
        )

    logger.info(
        "PARSE OK file=%s  chars_extracted=%d",
        filename, len(cleaned_text),
    )

    return cleaned_text


def split_text_into_chunks(raw_text: str) -> list[str]:
    """Break a long string into smaller, overlapping chunks.

    Why RecursiveCharacterTextSplitter?
      It tries to split on natural boundaries first (paragraphs → sentences →
      words → characters), so chunks tend to end at logical break-points rather
      than in the middle of a sentence.

    Args:
        raw_text: The full document text returned by read_text_from_uploaded_file().

    Returns:
        A list of strings, each at most CHUNK_SIZE characters long.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        # separators tells the splitter which boundaries to try, in order.
        separators=["\n\n", "\n", " ", ""],
    )

    # create_documents() returns LangChain Document objects.
    # We extract only the .page_content string from each one.
    langchain_document_objects = text_splitter.create_documents([raw_text])

    # Build a plain Python list of strings — no LangChain objects downstream.
    text_chunks = [doc.page_content for doc in langchain_document_objects]

    return text_chunks
