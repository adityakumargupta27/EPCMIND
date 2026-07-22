import re
import uuid
from typing import List, Dict, Any

DEFAULT_CHUNK_SIZE = 2400  # ~600 tokens
DEFAULT_OVERLAP = 400      # ~100 tokens

def detect_section(text: str) -> str:
    """Attempt to detect section numbers or headers in chunk text."""
    match = re.search(r'(?:Section|§|\b)(\d+\.[\d\.]+|\b[A-Z][A-Za-z0-9\s]{3,30}:)', text)
    if match:
        return match.group(0).strip()
    return "General"

def chunk_pages(
    document_id: str,
    document_name: str,
    pages: List[Dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Chunk page-by-page text while preserving page number citations.
    Returns list of chunk objects with full metadata.
    """
    chunks = []

    for page_info in pages:
        page_num = page_info["page"]
        text = page_info["text"]

        if not text or len(text.strip()) == 0:
            continue

        # If page text fits within chunk size, create single chunk
        if len(text) <= chunk_size:
            section = detect_section(text)
            chunks.append({
                "chunk_id": f"chk_{uuid.uuid4().hex[:12]}",
                "document_id": document_id,
                "document_name": document_name,
                "page_number": page_num,
                "section": section,
                "text": text
            })
            continue

        # Otherwise, slide window with overlap within the page
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Adjust end to nearest sentence or space if possible
            if end < len(text):
                last_space = text.rfind(' ', start + chunk_size - 100, end)
                if last_space != -1:
                    end = last_space

            chunk_text = text[start:end].strip()
            if len(chunk_text) > 0:
                section = detect_section(chunk_text)
                chunks.append({
                    "chunk_id": f"chk_{uuid.uuid4().hex[:12]}",
                    "document_id": document_id,
                    "document_name": document_name,
                    "page_number": page_num,
                    "section": section,
                    "text": chunk_text
                })

            if end >= len(text):
                break
            start = max(start + 1, end - overlap)

    return chunks
