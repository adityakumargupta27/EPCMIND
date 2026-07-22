import logging
from typing import List, Dict, Any, Optional
from rag.embeddings import embed_query
from rag import vector_store

logger = logging.getLogger("epcmind.retriever")

def retrieve_context(question: str, top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Embed question, perform vector search against SQLite vector store,
    optionally filtered strictly by document_id.
    """
    try:
        q_emb = embed_query(question)
    except Exception as e:
        logger.warning(f"[RAG Retriever] Could not embed query: {e}")
        return []

    chunks = vector_store.query_similar(q_emb, top_k=top_k, document_id=document_id)

    # Safe logging (no API keys, no confidential raw text)
    print(f"\n[RAG RETRIEVER DEBUG]")
    print(f"Question: {question} (Filter doc_id: {document_id})")
    print(f"Retrieved Chunks Count: {len(chunks)}")
    for i, c in enumerate(chunks, 1):
        print(f"  Chunk {i}: Doc='{c['document_name']}', Page={c['page_number']}, Section='{c['section']}', Score={c['score']:.4f}")
    print("-" * 50 + "\n")

    return chunks
