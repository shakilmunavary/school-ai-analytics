import os
import chromadb

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB = os.path.join(PROJECT_ROOT, "vector_db")
SCHEMA_REF_FILE = os.path.join(PROJECT_ROOT, "db_schema_reference.txt")

def run_indexing_loop():
    print("Initializing Unified Vector Database Sync...")
    client = chromadb.PersistentClient(path=VECTOR_DB)
    
    try:
        client.delete_collection("school_context")
    except Exception:
        pass
        
    collection = client.create_collection("school_context")
    
    if os.path.exists(SCHEMA_REF_FILE):
        with open(SCHEMA_REF_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        chunks = [chunk.strip() for chunk in content.split("Table:") if chunk.strip()]
        for idx, chunk in enumerate(chunks):
            collection.add(
                documents=[f"Table Setup:\n{chunk}"],
                ids=[f"schema_table_idx_{idx}"]
            )
        print(f"Indexed {len(chunks)} structural schema tables cleanly.")
    else:
        print("Missing database schema tracking file blueprint.")

if __name__ == "__main__":
    run_indexing_loop()