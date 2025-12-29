"""
Document Processor Module - Handle document ingestion
Processes PDFs and text files, chunks them, and stores in vector DB
"""

import os
from typing import List, Optional
from PyPDF2 import PdfReader
from vector_store import store_document


def read_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Extracted text content
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def read_pdf_bytes(file_bytes, filename: str = "uploaded.pdf") -> str:
    """
    Extract text from PDF bytes (for Streamlit uploads)
    
    Args:
        file_bytes: PDF file bytes
        filename: Original filename
    
    Returns:
        Extracted text content
    """
    try:
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF bytes: {e}")
        return ""


def read_text_file(file_path: str) -> str:
    """Read text from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text
        chunk_size: Target size of each chunk (in characters)
        overlap: Number of overlapping characters between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at sentence or paragraph boundary
        if end < text_length:
            # Look for paragraph break
            para_break = text.rfind('\n\n', start, end)
            if para_break > start + chunk_size // 2:
                end = para_break + 2
            else:
                # Look for sentence break
                for punct in ['. ', '? ', '! ']:
                    sent_break = text.rfind(punct, start, end)
                    if sent_break > start + chunk_size // 2:
                        end = sent_break + len(punct)
                        break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < text_length else text_length
    
    return chunks


def ingest_document(content: str, source: str = "unknown", 
                    chunk_size: int = 500) -> dict:
    """
    Process and store a document in the vector database
    
    Args:
        content: Text content of the document
        source: Source filename
        chunk_size: Size of each chunk
    
    Returns:
        dict with ingestion stats
    """
    chunks = chunk_text(content, chunk_size)
    
    stored = 0
    failed = 0
    
    for i, chunk in enumerate(chunks):
        result = store_document(
            content=chunk,
            source=source,
            metadata={"chunk_index": i, "total_chunks": len(chunks)}
        )
        
        if result:
            stored += 1
        else:
            failed += 1
    
    return {
        "total_chunks": len(chunks),
        "stored": stored,
        "failed": failed,
        "source": source
    }


def ingest_pdf(file_path: str) -> dict:
    """Ingest a PDF file into the vector database"""
    text = read_pdf(file_path)
    if not text:
        return {"error": "Failed to read PDF"}
    
    filename = os.path.basename(file_path)
    return ingest_document(text, source=filename)


def ingest_pdf_upload(file_bytes, filename: str) -> dict:
    """Ingest an uploaded PDF file (Streamlit)"""
    text = read_pdf_bytes(file_bytes, filename)
    if not text:
        return {"error": "Failed to read PDF"}
    
    return ingest_document(text, source=filename)


def ingest_text(text: str, source: str = "pasted_text") -> dict:
    """Ingest raw text into the vector database"""
    if not text.strip():
        return {"error": "Empty text"}
    
    return ingest_document(text, source=source)
