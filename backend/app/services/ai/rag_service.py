import logging
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

class RagService:
    """
    RAG Service for Music Theory Context.
    Uses ChromaDB to store and retrieve music theory documents.
    """
    
    def __init__(self, persistence_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        # Use default lightweight embedding model (all-MiniLM-L6-v2)
        # This will be downloaded automatically by chromadb/sentence-transformers
        self.embedding_ctx = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name="music_theory",
            embedding_function=self.embedding_ctx
        )
        
    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        """Add a document to the knowledge base."""
        try:
            self.collection.upsert(
                documents=[text],
                ids=[doc_id],
                metadatas=[metadata or {}]
            )
            logger.info(f"Added document {doc_id} to RAG.")
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            
    def retrieve(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieve relevant context for a query."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Flatten results (list of lists)
            if results["documents"]:
                return results["documents"][0]
            return []
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

# Singleton instance
rag_service = RagService()
