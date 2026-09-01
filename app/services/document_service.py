"""
document_service.py
-------------------
Responsibility: Turn an uploaded file into a list of text chunks.

Why do we chunk?
  A language model has a limited "context window" (how much text it can read
  at once).  Instead of sending the ENTIRE document to the model, we break it
  into small, overlapping pieces and only send the most relevant ones.

RAG Step: This service feeds Step 1 (before we store anything in ChromaDB).
"""

from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ── Constants ─────────────────────────────────────────────────────────────────
# Students: try changing these numbers and re-uploading a document to see
# how the chunk count changes.

CHUNK_SIZE = 500       # Maximum number of characters per chunk.
CHUNK_OVERLAP = 50     # How many characters are SHARED between two neighbours.
                       # Overlap helps the model understand context at boundaries.


# ── Functions ─────────────────────────────────────────────────────────────────

def read_text_from_uploaded_file(uploaded_file: UploadFile) -> str:
    """Read the raw bytes from the uploaded file and decode them as plain text.

    Args:
        uploaded_file: The file object FastAPI gives us from the request.

    Returns:
        A single string with the complete file contents.
    """
    # .file is a file-like object (same as open() in Python).
    raw_bytes = uploaded_file.file.read()

    # Decode bytes → string.  Most plain-text files use UTF-8.
    # 'errors="replace"' swaps any unreadable byte for a "?" instead of crashing.
    plain_text = raw_bytes.decode("utf-8", errors="replace")

    return plain_text


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
