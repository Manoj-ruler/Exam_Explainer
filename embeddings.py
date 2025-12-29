"""
Embeddings Module - Generate text embeddings using Gemini
Used for semantic search in the vector database
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()


def configure_genai():
    """Configure Google AI with API key"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")
    genai.configure(api_key=api_key)


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding vector for text using Gemini
    
    Args:
        text: Input text to embed
    
    Returns:
        List of floats (768 dimensions) or None on error
    """
    try:
        configure_genai()
        
        # Use text-embedding model
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def generate_query_embedding(query: str) -> Optional[List[float]]:
    """
    Generate embedding for a search query
    Uses different task_type for better retrieval
    
    Args:
        query: Search query text
    
    Returns:
        List of floats (768 dimensions) or None
    """
    try:
        configure_genai()
        
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        
        return result['embedding']
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return None


def generate_batch_embeddings(texts: List[str]) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts
    
    Args:
        texts: List of texts to embed
    
    Returns:
        List of embedding vectors
    """
    embeddings = []
    for text in texts:
        embedding = generate_embedding(text)
        embeddings.append(embedding)
    return embeddings
