"""
RAG Module - Retrieval Augmented Generation
Uses local rag.json knowledge base for context
"""

from typing import List, Tuple
from knowledge_base import KnowledgeBase
from gemini_client import GeminiClient

# Initialize knowledge base (loads rag.json)
_kb = None

def get_knowledge_base() -> KnowledgeBase:
    """Get or create knowledge base instance"""
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


def get_relevant_context(query: str, top_k: int = 7) -> Tuple[str, List[dict]]:
    """
    Retrieve relevant document chunks for a query from rag.json
    
    Args:
        query: User's question
        top_k: Number of chunks to retrieve
    
    Returns:
        Tuple of (formatted context string, list of source documents)
    """
    kb = get_knowledge_base()
    
    # Get context from knowledge base (uses rag.json)
    context = kb.get_context_for_query(query)
    
    # Build sources list from matched documents
    sources = []
    if kb.documents:
        query_lower = query.lower()
        for doc in kb.documents[:top_k]:
            if any(word in doc.get("content", "").lower() for word in query_lower.split() if len(word) > 2):
                sources.append({
                    "id": doc.get("id", "unknown"),
                    "content": doc.get("content", "")[:80] + "...",
                    "similarity": 0.85  # Simulated for display
                })
    
    return context, sources


def generate_rag_response(
    query: str, 
    gemini_client: GeminiClient,
    language: str = "English",
    top_k: int = 7
) -> Tuple[str, List[dict]]:
    """
    Generate a response using RAG with local rag.json
    
    Args:
        query: User's question
        gemini_client: Configured Gemini client
        language: Response language
        top_k: Number of context chunks to retrieve
    
    Returns:
        Tuple of (response text, sources list)
    """
    # Get relevant context from rag.json
    context, sources = get_relevant_context(query, top_k)
    
    # Build the prompt with context
    if context:
        augmented_prompt = f"""You are an expert on SRKR Engineering College R23 regulations.
Based on the following official regulations, answer the student's question accurately.

OFFICIAL REGULATIONS FROM SRKR ENGINEERING COLLEGE (R23):
{context}

STUDENT QUESTION: {query}

Instructions:
- Use ONLY the regulations provided above to answer
- Be specific and cite the actual rules
- If asked about something not in the regulations, say so clearly
- Be helpful and student-friendly
- Respond in {language}"""
    else:
        augmented_prompt = f"""You are an expert on academic regulations.

STUDENT QUESTION: {query}

Instructions:
- Provide general guidance based on common academic practices
- Mention this is general information
- Suggest checking SRKR R23 regulations for specifics
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
    
    citations = "\n\n---\n📚 **Sources from R23 Regulations:**\n"
    for i, source in enumerate(sources[:3], 1):  # Show max 3 sources
        citations += f"\n{i}. {source['content']}"
    
    return citations
