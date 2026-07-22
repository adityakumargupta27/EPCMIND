import os
import re
import hashlib
import uuid
import fitz  # PyMuPDF

from rag import chunking, embeddings, vector_store

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))

def ensure_uploads_dir():
    """Ensure the uploads directory exists."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or unsafe characters."""
    clean = re.sub(r'[^\w\.\-]', '_', filename)
    return clean or "document.pdf"

def compute_sha256(content: bytes) -> str:
    """Compute SHA-256 hash of file bytes for deduplication."""
    return hashlib.sha256(content).hexdigest()

def process_pdf_upload(filename: str, content: bytes) -> dict:
    """
    Validate, save, and extract page-by-page text from uploaded PDF content.
    Returns structured document info and extracted pages.
    """
    ensure_uploads_dir()

    if len(content) > 50 * 1024 * 1024:
        raise ValueError("File size exceeds maximum limit of 50 MB.")

    safe_filename = sanitize_filename(filename)
    file_hash = compute_sha256(content)
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    stored_filename = f"{document_id}_{safe_filename}"
    file_path = os.path.join(UPLOADS_DIR, stored_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    pages = []
    status = "Processing"
    total_text_length = 0

    try:
        doc = fitz.open(file_path)
        page_count = len(doc)

        for page_num in range(page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text") or ""
            clean_text = re.sub(r'\s+', ' ', text).strip()
            total_text_length += len(clean_text)
            pages.append({
                "page": page_num + 1,
                "text": clean_text
            })

        doc.close()

        if total_text_length < 30 and page_count > 0:
            status = "OCR Required"
        else:
            status = "Processing"

    except Exception as e:
        status = "Failed"
        page_count = 0
        pages = []

    return {
        "document_id": document_id,
        "original_filename": filename,
        "stored_filename": stored_filename,
        "file_path": file_path,
        "file_hash": file_hash,
        "file_size": len(content),
        "page_count": page_count,
        "status": status,
        "pages": pages
    }

def ingest_pdf_bytes(filename: str, content: bytes) -> dict:
    """Full pipeline: upload, extract text, chunk, generate embeddings, and persist in SQLite vector DB."""
    file_hash = compute_sha256(content)
    existing_doc = vector_store.get_document_by_hash(file_hash)
    if existing_doc:
        return existing_doc

    doc_info = process_pdf_upload(filename, content)
    if doc_info["status"] == "OCR Required":
        vector_store.upsert_document(doc_info, [], [])
        return doc_info

    chunks = chunking.chunk_pages(
        document_id=doc_info["document_id"],
        document_name=doc_info["original_filename"],
        pages=doc_info["pages"]
    )

    if not chunks:
        doc_info["status"] = "Failed"
        vector_store.upsert_document(doc_info, [], [])
        return doc_info

    chunk_texts = [c["text"] for c in chunks]
    embeddings_list = embeddings.embed_documents(chunk_texts)

    doc_info["status"] = "Indexed"
    vector_store.upsert_document(doc_info, chunks, embeddings_list)
    return doc_info
