import os
import json
import sqlite3
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional

VECTOR_STORE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vector_store"))
DB_PATH = os.path.join(VECTOR_STORE_DIR, "vectors.db")

# Export similarity threshold (default 0.75) for use across the codebase
RFI_SIMILARITY_THRESHOLD = float(os.getenv("RFI_SIMILARITY_THRESHOLD", "0.82"))

def generate_rfi_embedding_text(rfi: dict) -> str:
    """Construct the embedding text for an RFI.
    Uses only Title, Description, Discipline, Equipment, and Location.
    """
    parts = [
        f"Title: {rfi.get('title') or rfi.get('subject', '')}",
        f"Description: {rfi.get('description') or rfi.get('question', '')}"
    ]
    if rfi.get('discipline'):
        parts.append(f"Discipline: {rfi['discipline']}")
    if rfi.get('equipment'):
        parts.append(f"Equipment: {rfi['equipment']}")
    if rfi.get('location'):
        parts.append(f"Location: {rfi['location']}")
    return "\n".join(parts)


def get_connection():
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database tables for documents, vector chunks, compliance analyses, and RFIs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                upload_time TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                document_name TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                section TEXT,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_analyses (
                analysis_id TEXT PRIMARY KEY,
                req_doc_id TEXT NOT NULL,
                vendor_doc_id TEXT NOT NULL,
                equipment TEXT NOT NULL,
                discipline TEXT NOT NULL,
                created_at TEXT NOT NULL,
                checks_json TEXT NOT NULL,
                stats_json TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rfis (
                rfi_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                discipline TEXT NOT NULL,
                equipment TEXT,
                location TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                raised_by TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                final_resolution TEXT,
                closed_at TEXT,
                embedding_blob BLOB,
                analysis_json TEXT
            )
        """)
        conn.commit()

def get_document_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    """Check if document with exact file hash is already indexed."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None

def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """Get document metadata by ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None

def get_chunks_by_document(document_id: str) -> List[Dict[str, Any]]:
    """Retrieve all chunks belonging to a specific document for comprehensive analysis."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT chunk_id, document_id, document_name, page_number, section, text FROM chunks WHERE document_id = ? ORDER BY page_number ASC",
            (document_id,)
        )
        return [dict(r) for r in cursor.fetchall()]

def upsert_document(document_meta: dict, chunks: List[dict], embeddings: List[List[float]]):
    """
    Persist document metadata and chunk embeddings in SQLite.
    Replaces existing document chunks if document_id already exists.
    """
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_meta["document_id"],))
        cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_meta["document_id"],))

        upload_time = document_meta.get("upload_time") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO documents (
                document_id, original_filename, stored_filename, file_hash,
                file_size, upload_time, page_count, chunk_count, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document_meta["document_id"],
            document_meta["original_filename"],
            document_meta["stored_filename"],
            document_meta["file_hash"],
            document_meta["file_size"],
            upload_time,
            document_meta["page_count"],
            len(chunks),
            document_meta["status"]
        ))

        chunk_rows = []
        for chunk, emb in zip(chunks, embeddings):
            emb_bytes = np.array(emb, dtype=np.float32).tobytes()
            chunk_rows.append((
                chunk["chunk_id"],
                chunk["document_id"],
                chunk["document_name"],
                chunk["page_number"],
                chunk.get("section", "General"),
                chunk["text"],
                emb_bytes
            ))

        cursor.executemany("""
            INSERT INTO chunks (
                chunk_id, document_id, document_name, page_number, section, text, embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, chunk_rows)

        conn.commit()

def query_similar(query_embedding: List[float], top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Perform cosine similarity search using NumPy across stored chunk embeddings.
    Optionally filters chunks strictly by document_id.
    """
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        if document_id:
            cursor.execute(
                "SELECT chunk_id, document_id, document_name, page_number, section, text, embedding FROM chunks WHERE document_id = ?",
                (document_id,)
            )
        else:
            cursor.execute("SELECT chunk_id, document_id, document_name, page_number, section, text, embedding FROM chunks")
        
        rows = cursor.fetchall()

    if not rows:
        return []

    q_vec = np.array(query_embedding, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []
    q_unit = q_vec / q_norm

    chunk_metas = []
    matrix_list = []

    for r in rows:
        emb_arr = np.frombuffer(r["embedding"], dtype=np.float32)
        matrix_list.append(emb_arr)
        chunk_metas.append({
            "chunk_id": r["chunk_id"],
            "document_id": r["document_id"],
            "document_name": r["document_name"],
            "page_number": r["page_number"],
            "section": r["section"],
            "text": r["text"]
        })

    matrix = np.vstack(matrix_list) # shape (N, dim)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    matrix_unit = matrix / norms

    scores = (matrix_unit @ q_unit).tolist()

    for meta, score in zip(chunk_metas, scores):
        meta["score"] = float(score)

    chunk_metas.sort(key=lambda x: x["score"], reverse=True)
    return chunk_metas[:top_k]

def get_all_documents() -> List[Dict[str, Any]]:
    """Return all stored document metadata records."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY upload_time DESC")
        return [dict(r) for r in cursor.fetchall()]

def delete_document(document_id: str):
    """Delete document metadata and all associated chunks."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
        conn.commit()

def save_compliance_analysis(analysis_id: str, req_doc_id: str, vendor_doc_id: str, equipment: str, discipline: str, checks: list, stats: dict):
    """Persist compliance analysis run in SQLite database."""
    init_db()
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO compliance_analyses (
                analysis_id, req_doc_id, vendor_doc_id, equipment, discipline, created_at, checks_json, stats_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            req_doc_id,
            vendor_doc_id,
            equipment,
            discipline,
            created_at,
            json.dumps(checks),
            json.dumps(stats)
        ))
        conn.commit()

def get_latest_compliance_analysis() -> Optional[Dict[str, Any]]:
    """Retrieve the most recent compliance analysis from SQLite database."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM compliance_analyses ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["checks"] = json.loads(d["checks_json"])
            d["stats"] = json.loads(d["stats_json"])
            return d
    return None

# --- RFI Persistence & Vector Search ---

def upsert_rfi(rfi_data: dict, embedding: Optional[List[float]] = None, analysis: Optional[dict] = None):
    """Persist or update RFI record and embedding in SQLite database."""
    init_db()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    rfi_id = rfi_data["rfi_id"]
    created_at = rfi_data.get("created_at") or now
    updated_at = now

    emb_bytes = np.array(embedding, dtype=np.float32).tobytes() if embedding else None
    analysis_json = json.dumps(analysis) if analysis else None

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rfis (
                rfi_id, title, description, discipline, equipment, location,
                status, priority, raised_by, created_at, updated_at,
                final_resolution, closed_at, embedding_blob, analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(rfi_id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                discipline = excluded.discipline,
                equipment = excluded.equipment,
                location = excluded.location,
                status = excluded.status,
                priority = excluded.priority,
                raised_by = excluded.raised_by,
                updated_at = excluded.updated_at,
                final_resolution = excluded.final_resolution,
                closed_at = excluded.closed_at,
                embedding_blob = COALESCE(excluded.embedding_blob, rfis.embedding_blob),
                analysis_json = COALESCE(excluded.analysis_json, rfis.analysis_json)
        """, (
            rfi_id,
            rfi_data["title"],
            rfi_data["description"],
            rfi_data.get("discipline", "General"),
            rfi_data.get("equipment", ""),
            rfi_data.get("location", ""),
            rfi_data.get("status", "Open"),
            rfi_data.get("priority", "HIGH"),
            rfi_data.get("raised_by", "Contractor"),
            created_at,
            updated_at,
            rfi_data.get("final_resolution"),
            rfi_data.get("closed_at"),
            emb_bytes,
            analysis_json
        ))
        conn.commit()

def get_rfi_by_id(rfi_id: str) -> Optional[Dict[str, Any]]:
    """Fetch RFI record by ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rfis WHERE rfi_id = ?", (rfi_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            if d.get("analysis_json"):
                d["analysis"] = json.loads(d["analysis_json"])
            return d
    return None

def get_all_rfis() -> List[Dict[str, Any]]:
    """Return all stored RFI records."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rfis ORDER BY created_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if d.get("analysis_json"):
                d["analysis"] = json.loads(d["analysis_json"])
            result.append(d)
        return result

def find_similar_rfis(
    query_embedding: List[float],
    top_k: int = 5,
    exclude_rfi_id: Optional[str] = None,
    discipline: Optional[str] = None,
    equipment: Optional[str] = None,
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Perform hybrid vector similarity search across historical RFIs in SQLite.
    Combines cosine similarity with weighted metadata bonuses.
    """
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM rfis WHERE embedding_blob IS NOT NULL AND status IN ('Closed', 'Resolved')"
        )
        rows = cursor.fetchall()

    if not rows:
        return []

    q_vec = np.array(query_embedding, dtype=np.float32)
    q_norm = np.linalg.norm(q_vec)
    if q_norm == 0:
        return []
    q_unit = q_vec / q_norm

    candidates = []
    matrix_list = []

    for r in rows:
        if exclude_rfi_id and r["rfi_id"] == exclude_rfi_id:
            continue
        emb_arr = np.frombuffer(r["embedding_blob"], dtype=np.float32)
        matrix_list.append(emb_arr)
        candidates.append(dict(r))

    if not candidates:
        return []

    matrix = np.vstack(matrix_list)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    matrix_unit = matrix / norms

    raw_scores = (matrix_unit @ q_unit).tolist()

    ranked = []
    for cand, raw_sim in zip(candidates, raw_scores):
        # Weighted hybrid scoring
        semantic_part = raw_sim * 0.85
        metadata_score = 0.0
        if discipline and cand.get("discipline", "").lower() == discipline.lower():
            metadata_score += 0.07
        if equipment and cand.get("equipment") and equipment.lower() in cand.get("equipment", "").lower():
            metadata_score += 0.05
        if location and cand.get("location") and location.lower() in cand.get("location", "").lower():
            metadata_score += 0.03
        hybrid_score = semantic_part + metadata_score
        # Clamp to [0,1]
        hybrid_score = min(1.0, max(0.0, hybrid_score))
        percentage = int(round(hybrid_score * 100))

        cand["raw_cosine_sim"] = float(raw_sim)
        cand["similarity_score"] = hybrid_score
        cand["similarity_percentage"] = percentage
        ranked.append(cand)

    ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
    return ranked[:top_k]
