"""
RAG Module - Retrieval Augmented Generation
Combines vector search with LLM for contextual responses
"""

from typing import List, Tuple
from vector_store import search_similar_documents
from gemini_client import GeminiClient
from prompts import get_system_prompt


def get_relevant_context(query: str, top_k: int = 5) -> Tuple[str, List[dict]]:
    """
    Retrieve relevant document chunks for a query
    
    Args:
        query: User's question
        top_k: Number of chunks to retrieve
    
    Returns:
        Tuple of (formatted context string, list of source documents)
    """
    results = search_similar_documents(query, top_k)
    
    if not results:
        return "", []
    
    # Format context from retrieved chunks
    context_parts = []
    sources = []
    
    for i, doc in enumerate(results, 1):
        context_parts.append(f"[Source {i}]: {doc['content']}")
        sources.append({
            "id": doc.get('id'),
            "content": doc['content'][:100] + "...",
            "similarity": doc.get('similarity', 0)
        })
    
    context = "\n\n".join(context_parts)
    return context, sources


def generate_rag_response(
    query: str, 
    gemini_client: GeminiClient,
    language: str = "English",
    top_k: int = 5
) -> Tuple[str, List[dict]]:
    """
    Generate a response using RAG
    
    Args:
        query: User's question
        gemini_client: Configured Gemini client
        language: Response language
        top_k: Number of context chunks to retrieve
    
    Returns:
        Tuple of (response text, sources list)
    """
    # Get relevant context
    context, sources = get_relevant_context(query, top_k)
    
    # Build the prompt with context
    if context:
        augmented_prompt = f"""Based on the following context from the knowledge base, answer the user's question.

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION: {query}

Instructions:
- Use the context to provide accurate, specific information
- If the context doesn't contain relevant information, say so and provide general guidance
- Always be helpful and educational
- Respond in {language}"""
    else:
        augmented_prompt = f"""The knowledge base doesn't have specific information about this topic.

USER QUESTION: {query}

Instructions:
- Provide general guidance based on common academic practices
- Be clear that this is general information
- Suggest the user check their institution's specific policies
- Respond in {language}"""
    
    try:
        response = gemini_client.generate_response(augmented_prompt)
        return response, sources
    except Exception as e:
        return f"Error generating response: {str(e)}", []


def format_citations(sources: List[dict]) -> str:
    """Format source citations for display"""
    if not sources:
        return ""
    
    citations = "\n\n---\n📚 **Sources:**\n"
    for i, source in enumerate(sources, 1):
        similarity = source.get('similarity', 0)
        citations += f"\n{i}. {source['content']} (relevance: {similarity:.0%})"
    
    return citations
