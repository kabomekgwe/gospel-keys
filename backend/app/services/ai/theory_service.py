
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import mlx.core as mx
from mlx_lm import load, generate

# Configure logger
logger = logging.getLogger(__name__)

class TheoryService:
    """
    Service for generating music theory explanations and analysis using local LLMs via MLX.
    Optimized for Apple Silicon.
    """
    
    # Model configuration
    MODEL_PATH = "mlx-community/Qwen2.5-14B-Instruct-4bit"
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_loaded = False

    async def load_model(self):
        """
        Loads the model into memory. This is a heavy operation.
        """
        if self.is_loaded:
            return

        try:
            logger.info(f"Loading MLX model: {self.MODEL_PATH}...")
            # load() returns (model, tokenizer)
            self.model, self.tokenizer = load(self.MODEL_PATH)
            self.is_loaded = True
            logger.info("✅ MLX Model loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load MLX model: {e}")
            raise e

    async def explain_concept(self, concept: str, context: str = "general") -> str:
        """
        Generates an explanation for a music theory concept using RAG context.
        """
        if not self.is_loaded:
            await self.load_model()
            
        # 1. Retrieve relevant context from RAG
        try:
            from app.services.ai.rag_service import rag_service
            # Retrieve potentially useful context
            retrieved_docs = rag_service.retrieve(concept, n_results=2)
            context_str = "\n".join(retrieved_docs) if retrieved_docs else "No specific external context provided."
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            context_str = "Context retrieval unavailable."

        system_prompt = (
            "You are an expert music theory professor. "
            "Explain the following concept clearly, using musical examples where appropriate.\n"
            "Use the provided context below if it helps answer the user's specific query, but relies on your general knowledge if the context is irrelevant.\n"
            f"--- CONTEXT START ---\n{context_str}\n--- CONTEXT END ---\n"
            "Keep the explanation concise but accurate."
        )
        
        user_prompt = f"Explain the concept of '{concept}' in the context of {context} music theory."
        
        # Format for chat models (Qwen Instruct)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            response = generate(
                self.model, 
                self.tokenizer, 
                prompt=prompt, 
                max_tokens=512, 
                verbose=True
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating theory explanation: {e}")
            return "I encountered an error trying to explain that concept."

    async def analyze_progression(self, chords: List[str]) -> str:
        """
        Analyzes a chord progression using the LLM.
        """
        if not self.is_loaded:
            await self.load_model()

        chord_str = " - ".join(chords)
        prompt = (
            f"Analyze the following chord progression: {chord_str}. "
            "Identify the key, functional harmony (Roman Numerals), and any interesting modulations or substitutions."
        )
        
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        return generate(
            self.model, 
            self.tokenizer, 
            prompt=formatted_prompt, 
            max_tokens=512,
            verbose=False
        )

# Singleton instance
theory_service = TheoryService()
