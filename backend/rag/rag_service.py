import json
from typing import List, Dict, Any
import google.generativeai as genai
from google.generativeai import types

from services.gemini_service import get_client, get_model_name, PROJECT_CONTEXT
from rag.retriever import retrieve_context
from models.schemas import AIMessage

RAG_SYSTEM_INSTRUCTION = """You are EPCMind AI, an engineering intelligence assistant for a hyperscale data centre EPC project.
You answer user questions using the retrieved project document excerpts provided.

Strict Rules:
1. Answer using ONLY the retrieved project document context.
2. Never fabricate specifications, document citations, page numbers, or equipment values.
3. If the retrieved context does not contain enough information to answer the question, clearly state:
   "This information cannot be verified from the indexed project documents."
4. Do not invent page numbers or document names.
5. Be concise, professional, and engineering-focused.
6. You MUST format your response as a valid JSON object matching the requested schema.
"""

def deduplicate_sources(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate source citations based on (document, page)."""
    seen = set()
    sources = []
    for c in chunks:
        key = (c["document_name"], c["page_number"])
        if key not in seen:
            seen.add(key)
            sources.append({
                "document": c["document_name"],
                "section": c.get("section", "General"),
                "page": c["page_number"]
            })
    return sources

def ask_copilot_rag(question: str) -> dict:
    """
    Perform RAG pipeline:
    1. Retrieve relevant document chunks from vector store.
    2. Construct prompt with retrieved context.
    3. Query Gemini for grounded response.
    4. Attach real document citations.
    """
    # Retrieve top 5 chunks
    retrieved_chunks = retrieve_context(question, top_k=5)

    # Filter chunks with reasonable similarity (score >= 0.20)
    relevant_chunks = [c for c in retrieved_chunks if c.get("score", 0) >= 0.20]

    model_name = get_model_name()

    try:
        client = get_client()
    except ValueError as err:
        return {
            "role": "assistant",
            "content": str(err),
            "sources": [],
            "meta": {"action": "Configure GEMINI_API_KEY"}
        }

    if relevant_chunks:
        # Construct grounded context prompt
        context_blocks = []
        for i, c in enumerate(relevant_chunks, 1):
            block = (
                f"--- Document Chunk {i} ---\n"
                f"Document: {c['document_name']}\n"
                f"Page: {c['page_number']}\n"
                f"Section: {c.get('section', 'General')}\n"
                f"Text:\n{c['text']}\n"
            )
            context_blocks.append(block)

        context_str = "\n".join(context_blocks)
        prompt = f"RETRIEVED PROJECT DOCUMENTS:\n{context_str}\n\nUSER QUESTION:\n{question}"

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=RAG_SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                    response_schema=AIMessage.model_json_schema()
                ),
            )

            if response and response.text:
                data = json.loads(response.text)
                data["role"] = "assistant"
                data["sources"] = deduplicate_sources(relevant_chunks)
                if "meta" not in data or not data["meta"]:
                    data["meta"] = {"mode": "rag"}
                else:
                    data["meta"]["mode"] = "rag"
                return data

        except Exception as e:
            return {
                "role": "assistant",
                "content": f"Gemini API request failed: {str(e)}",
                "sources": deduplicate_sources(relevant_chunks),
                "meta": {"mode": "rag_error"}
            }

    # Fallback if no relevant indexed document chunks are found
    prompt = (
        f"PROJECT CONTEXT (Dashboard Summary):\n{PROJECT_CONTEXT}\n\n"
        f"USER QUESTION:\n{question}\n\n"
        f"INSTRUCTION: If this is a document specification question not present in the project summary above, "
        f"state clearly that it cannot be verified from indexed project documents."
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=RAG_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=AIMessage.model_json_schema()
            ),
        )
        if response and response.text:
            data = json.loads(response.text)
            data["role"] = "assistant"
            # Do NOT fabricate document sources when no document chunks match
            data["sources"] = []
            return data
    except Exception as e:
        pass

    return {
        "role": "assistant",
        "content": "This information cannot be verified from the indexed project documents.",
        "sources": [],
        "meta": {"mode": "unverified"}
    }
