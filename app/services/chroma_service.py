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

from app.core.config import get_settings

# ── Constants ─────────────────────────────────────────────────────────────────

COLLECTION_NAME = "document_chunks"   # All uploaded docs share one collection.
                                       # Students: change this to namespace docs.
EMBEDDING_MODEL = "text-embedding-3-small"   # Cheap, fast, great for teaching.


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

    # OpenAIEmbeddingFunction converts text → numbers automatically.
    # ChromaDB calls it for us every time we add or query documents.
    openai_embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=settings.OPENAI_API_KEY,
        model_name=EMBEDDING_MODEL,
    )

    # get_or_create_collection: if the collection already exists, reuse it;
    # if not, create a new empty one.  Safe to call on every request.
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=openai_embedding_function,
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

    # .add() sends all chunks to ChromaDB in one network call.
    # ChromaDB calls the embedding function on each chunk automatically.
    collection.add(
        ids=unique_ids,
        documents=text_chunks,       # raw text goes here
        metadatas=metadata_list,     # our custom metadata dict per chunk
    )

    total_chunks_stored = len(text_chunks)
    return total_chunks_stored


def retrieve_relevant_chunks(
    user_query: str,
    number_of_results: int = 3,
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

    query_results = collection.query(
        query_texts=[user_query],         # ChromaDB embeds this for us
        n_results=number_of_results,
    )

    # query_results["documents"] is a list-of-lists because you can query
    # multiple texts at once.  We queried one text, so we take index [0].
    relevant_text_chunks = query_results["documents"][0]

    return relevant_text_chunks
