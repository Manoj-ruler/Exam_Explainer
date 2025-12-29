"""
Vector Store Module - Supabase pgvector Integration
Handles document storage and semantic search
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict
from embeddings import generate_embedding, generate_query_embedding

load_dotenv()


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Supabase credentials not found")
    
    return create_client(url, key)


def store_document(content: str, source: str = None, metadata: dict = None) -> Optional[dict]:
    """
    Store a document chunk with its embedding
    
    Args:
        content: Text content of the chunk
        source: Source filename
        metadata: Additional metadata dict
    
    Returns:
        Stored document dict or None
    """
    try:
        # Generate embedding
        embedding = generate_embedding(content)
        if not embedding:
            print("Failed to generate embedding")
            return None
        
        supabase = get_supabase_client()
        response = supabase.table("documents").insert({
            "content": content,
            "embedding": embedding,
            "source": source,
            "metadata": metadata or {}
        }).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error storing document: {e}")
        return None


def search_similar_documents(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search for documents similar to the query
    
    Args:
        query: Search query text
        top_k: Number of results to return
    
    Returns:
        List of matching documents with similarity scores
    """
    try:
        # Generate query embedding
        query_embedding = generate_query_embedding(query)
        if not query_embedding:
            print("Failed to generate query embedding")
            return []
        
        supabase = get_supabase_client()
        
        # Call the match_documents function
        response = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_count': top_k
            }
        ).execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error searching documents: {e}")
        return []


def get_all_documents() -> List[Dict]:
    """Get all stored documents (without embeddings for performance)"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("documents")\
            .select("id, content, source, metadata, created_at")\
            .order("created_at", desc=True)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"Error getting documents: {e}")
        return []


def delete_document(doc_id: str) -> bool:
    """Delete a document by ID"""
    try:
        supabase = get_supabase_client()
        supabase.table("documents")\
            .delete()\
            .eq("id", doc_id)\
            .execute()
        return True
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False


def delete_all_documents() -> bool:
    """Delete all documents (use with caution!)"""
    try:
        supabase = get_supabase_client()
        supabase.table("documents")\
            .delete()\
            .neq("id", "00000000-0000-0000-0000-000000000000")\
            .execute()
        return True
    except Exception as e:
        print(f"Error deleting all documents: {e}")
        return False


def get_document_count() -> int:
    """Get total number of stored documents"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("documents")\
            .select("id", count="exact")\
            .execute()
        return response.count or 0
    except Exception as e:
        print(f"Error counting documents: {e}")
        return 0
