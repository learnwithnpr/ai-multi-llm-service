import os
import chromadb
from app.core.config import get_settings
from app.services.chroma_service import COLLECTION_NAME

def main():
    print("Connecting to ChromaDB...")
    settings = get_settings()
    
    try:
        client = chromadb.HttpClient(
            host=settings.CHROMA_HOST, 
            port=settings.CHROMA_PORT
        )
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as error:
        print(f"\nFailed to connect to ChromaDB or collection '{COLLECTION_NAME}' does not exist.")
        print(f"Error: {error}")
        return

    # Fetch all data (IDs, text, metadata, and embeddings)
    data = collection.get(
        include=["documents", "metadatas", "embeddings"]
    )
    
    ids = data.get("ids", [])
    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])
    embeddings = data.get("embeddings", [])

    
    if not ids:
        print("\nNo documents found in the database.")
        return
        
    print(f"\nSuccessfully fetched {len(ids)} chunks from ChromaDB:\n")
    
    # Define column widths for tabular output
    ID_WIDTH = 38
    SOURCE_WIDTH = 25
    EMB_WIDTH = 18
    TEXT_WIDTH = 45
    
    # Print Table Header
    header = f"{'ID':<{ID_WIDTH}} | {'Document Source':<{SOURCE_WIDTH}} | {'Embedding':<{EMB_WIDTH}} | {'Text Preview'}"
    print(header)
    print("-" * len(header))
    
    # Print Rows
    # In case embeddings are missing for some reason, pad the list
    if embeddings is None or len(embeddings) == 0:
        embeddings = [None] * len(ids)

    for doc_id, doc_text, meta, emb in zip(ids, documents, metadatas, embeddings):
        source = meta.get("source_document", "Unknown") if meta else "Unknown"
        
        # Format embedding preview
        if emb is not None and len(emb) >= 2:
            emb_str = f"[{emb[0]:.2f}, {emb[1]:.2f} ...]"
        elif emb is not None and len(emb) == 1:
            emb_str = f"[{emb[0]:.2f}]"
        else:
            emb_str = "[No Emb]"
            
        if len(emb_str) > EMB_WIDTH:
            emb_str = emb_str[:EMB_WIDTH - 3] + "..."
            
        # Clean up text for the preview (remove newlines and truncate)
        clean_text = (doc_text or "").replace("\n", " ").strip()
        if len(clean_text) > TEXT_WIDTH:
            preview = clean_text[:TEXT_WIDTH - 3] + "..."
        else:
            preview = clean_text
            
        # Truncate source if too long
        if len(source) > SOURCE_WIDTH:
            source = source[:SOURCE_WIDTH - 3] + "..."
            
        print(f"{doc_id:<{ID_WIDTH}} | {source:<{SOURCE_WIDTH}} | {emb_str:<{EMB_WIDTH}} | {preview}")
        
    print("\n")

if __name__ == "__main__":
    main()
