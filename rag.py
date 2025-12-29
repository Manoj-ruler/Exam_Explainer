"""
RAG Module - Retrieval Augmented Generation
Uses local rag.json knowledge base for context
"""

from typing import List, Tuple
from knowledge_base import KnowledgeBase
from gemini_client import GeminiClient

# Initialize knowledge base (loads rag.json)
_kb = None

# Keywords that indicate OFF-TOPIC queries (things we should NOT answer)
OFF_TOPIC_KEYWORDS = [
    "r24", "r22", "r21", "r20", "r19",  # Other regulations
    "solve", "calculate my", "predict my", "give me answer",  # Cheating requests
    "weather", "movie", "song", "game", "joke", "recipe",  # Unrelated topics
    "write code", "programming", "python code", "java code",  # Programming
    "travel", "news", "sports", "politics"  # Random topics
]


def get_knowledge_base() -> KnowledgeBase:
    """Get or create knowledge base instance"""
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


def is_off_topic(query: str) -> bool:
    """Check if query is completely off-topic (should be declined)"""
    query_lower = query.lower()
    
    # Check for off-topic keywords
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in query_lower:
            return True
    
    return False


def get_relevant_context(query: str, top_k: int = 7) -> Tuple[str, List[dict]]:
    """
    Retrieve relevant document chunks for a query from rag.json
    """
    kb = get_knowledge_base()
    
    # Get context from knowledge base (uses rag.json)
    context = kb.get_context_for_query(query)
    
    # Build sources list from matched documents
    sources = []
    if kb.documents:
        query_lower = query.lower()
        for doc in kb.documents:
            doc_content = doc.get("content", "").lower()
            # Check if any query word (3+ chars) appears in document
            if any(word in doc_content for word in query_lower.split() if len(word) > 2):
                sources.append({
                    "id": doc.get("id", "unknown"),
                    "content": doc.get("content", "")[:80] + "...",
                    "similarity": 0.85
                })
                if len(sources) >= top_k:
                    break
    
    return context, sources


def generate_rag_response(
    query: str, 
    gemini_client: GeminiClient,
    language: str = "English",
    top_k: int = 7
) -> Tuple[str, List[dict]]:
    """
    Generate a response using RAG with local rag.json
    """
    # Check if query is completely off-topic
    if is_off_topic(query):
        decline_message = """I'm sorry, but I cannot help with that.

As an **SRKR Engineering College R23 Regulations** explainer, I'm designed to answer questions about:

• **Grading System** (CGPA, grade points, 10-point scale)
• **Attendance Rules** (75% minimum, condonation)
• **Internal & External Evaluation** (30-70 split)
• **Revaluation Process**
• **Credit System** (160 credits for B.Tech)
• **Internship Requirements**
• **MOOC Policies**
• **Malpractice Regulations**
• **Promotion Rules**

Is there anything about **R23 exam procedures or regulations** I can explain for you?"""
        return decline_message, []
    
    # Get relevant context from rag.json
    context, sources = get_relevant_context(query, top_k)
    
    # Build the prompt - be helpful with R23 content
    augmented_prompt = f"""You are a helpful expert on SRKR Engineering College R23 regulations.

Your job is to answer student questions based on the following official R23 regulations:

{context}

STUDENT QUESTION: {query}

INSTRUCTIONS:
1. Answer the question using the regulations provided above
2. Be helpful, friendly, and informative
3. If the question is general (like "tell me about R23"), give an overview of the key points
4. Format your response nicely with bullet points where appropriate
5. Respond in {language}

Remember: You are helping students understand SRKR R23 regulations. Be thorough and helpful!"""
    
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
    for i, source in enumerate(sources[:3], 1):
        citations += f"\n{i}. {source['content']}"
    
    return citations
