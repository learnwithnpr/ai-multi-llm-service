"""
chroma_service.py
-----------------
Responsibility: Talk to ChromaDB — store text chunks and retrieve relevant ones.

What is ChromaDB?
  A vector database.  Instead of storing rows like a normal database, it stores
  "embeddings" — lists of numbers that represent the *meaning* of a piece of text.
  When you search, it finds chunks whose meaning is closest to your query.

What is an embedding?
  The OpenAI embedding model reads a piece of text and outputs ~1500 numbers.
  Similar texts produce similar numbers, so "dog" and "puppy" end up close
  together in that number-space.

RAG Steps this service covers:
  - After chunking  → add_documents_to_collection()  (stores chunks)
  - Before the LLM  → retrieve_relevant_chunks()      (fetches context)
"""

import uuid

import chromadb
from chromadb.utils import embedding_functions
from app.core.logger import get_logger

from app.core.config import get_settings
from app.services.openai_service import get_embeddings, get_embedding

# ── Constants ─────────────────────────────────────────────────────────────────

COLLECTION_NAME = "document_chunks"   # All uploaded docs share one collection.
                                       # Students: change this to namespace docs.
EMBEDDING_MODEL = "text-embedding-3-small"   # Cheap, fast, great for teaching.

logger = get_logger()

# ── Internal helper: build the ChromaDB client + collection ──────────────────

def _get_chroma_collection() -> chromadb.Collection:
    """Connect to ChromaDB and return (or create) our collection.

    This is a private helper — the underscore means "don't call this directly".
    Both public functions below call it so they always use the same collection.
    """
    settings = get_settings()

    # HttpClient connects to a running ChromaDB server (e.g. via Docker).
    # Students: make sure `docker run -p 8000:8000 chromadb/chroma` is running.
    chroma_client = chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )

    # get_or_create_collection: if the collection already exists, reuse it;
    # if not, create a new empty one.  Safe to call on every request.
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
    )

    return collection


# ── Public functions ──────────────────────────────────────────────────────────

def add_documents_to_collection(
    text_chunks: list[str],
    document_name: str,
) -> int:
    """Store a list of text chunks in ChromaDB.

    Each chunk gets:
      - A unique ID  (so we can store multiple documents without collisions)
      - The raw text (ChromaDB calls OpenAI to turn it into an embedding)
      - Metadata     (so we know which file the chunk came from)

    Args:
        text_chunks:   List of strings from document_service.split_text_into_chunks().
        document_name: The original filename — stored as metadata for traceability.

    Returns:
        The total number of chunks stored.
    """
    collection = _get_chroma_collection()

    # Build parallel lists that ChromaDB's .add() method expects.
    unique_ids = []
    metadata_list = []

    for chunk_text in text_chunks:
        # uuid4() generates a random 128-bit ID — virtually no collision risk.
        chunk_id = str(uuid.uuid4())
        unique_ids.append(chunk_id)
        metadata_list.append({"source_document": document_name})

    # Explicitly generate embeddings for all chunk texts
    chunk_embeddings = get_embeddings(text_chunks)
    logger.info("Embedding generation complete %s",chunk_embeddings)
    # .add() sends all chunks to ChromaDB in one network call.
    collection.add(
        ids=unique_ids,
        embeddings=chunk_embeddings, # We embed the chunks before adding them
        documents=text_chunks,       # raw text goes here
        metadatas=metadata_list,     # our custom metadata dict per chunk
    )

    total_chunks_stored = len(text_chunks)
    return total_chunks_stored


def retrieve_relevant_chunks(
    user_query: str,
    number_of_results: int = 1,
) -> list[str]:
    """Find the most relevant text chunks for a given user question.

    ChromaDB converts the query to an embedding, then finds the chunks
    whose embeddings are numerically closest (= semantically most similar).

    Args:
        user_query:       The user's raw question string.
        number_of_results: How many chunks to return.  3 is a good default;
                           raise it for longer context, lower it to reduce cost.

    Returns:
        A list of text strings, ordered from most to least relevant.
        Returns an empty list if the collection has no documents yet.
    """
    collection = _get_chroma_collection()

    # Guard: if the collection is empty, skip the query and return nothing.
    # This prevents an error when /chat is called before any document is uploaded.
    if collection.count() == 0:
        return []

    # Explicitly generate an embedding for the user's query
    query_embedding = get_embedding(user_query)

    query_results = collection.query(
        query_embeddings=[query_embedding], # Semantic search using the embedded user query
        n_results=number_of_results,
    )

    # logger.info("Query results %s",query_results)
    logger.info("Query results id %s",query_results["ids"])

    # query_results["documents"] is a list-of-lists because you can query
    # multiple texts at once.  We queried one text, so we take index [0].
    relevant_text_chunks = query_results["documents"][0]

    return relevant_text_chunks
