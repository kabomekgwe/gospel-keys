
import sys
import os
import argparse

# Add backend to path
sys.path.append(os.getcwd())

from app.services.ai.rag_service import rag_service

def ingest_file(file_path: str, category: str = "general"):
    """Ingest a text file into the RAG system."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        doc_id = os.path.basename(file_path)
        rag_service.add_document(
            doc_id=doc_id,
            text=content,
            metadata={"source": file_path, "category": category}
        )
        print(f"✅ Successfully ingested {file_path}")
    except Exception as e:
        print(f"❌ Failed to ingest {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into RAG")
    parser.add_argument("file", help="Path to text file to ingest")
    parser.add_argument("--category", default="theory", help="Category metadata")
    
    args = parser.parse_args()
    ingest_file(args.file, args.category)
