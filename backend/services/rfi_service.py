import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

import google.generativeai as genai
from google.generativeai import types

from services.gemini_service import get_client, get_model_name
from rag import embeddings, vector_store
from rag.retriever import retrieve_context

def get_similarity_threshold() -> float:
    """Configurable similarity threshold for historical RFI matches."""
    try:
        return float(os.getenv("RFI_SIMILARITY_THRESHOLD", "0.75"))
    except ValueError:
        return 0.75


RFI_RESOLUTION_INSTRUCTION = """You are an EPC Mind AI engineering consultant specializing in RFI resolution.

Given:
1. NEW RFI details (Title, Description, Discipline, Equipment, Location)
2. TOP SIMILAR HISTORICAL RFIs and their actual final resolutions
3. RELEVANT PROJECT DOCUMENT EXCERPTS

Generate an AI-assisted suggested resolution:
- suggestedResolution: Concise, professional engineering resolution for the contractor/engineering team.
- reasoning: Detailed engineering explanation citing precedents or technical requirements.
- recommendedActions: A list of 2-4 concrete next steps for project execution.

Important Grounding Rule:
- Suggested resolution MUST be clearly framed as an AI-assisted recommendation.
- Never claim the AI suggestion is an officially approved engineering sign-off.
- If insufficient historical or project document evidence is available, explicitly state that human engineering review is required.

Format output as a valid JSON object matching the requested schema.
"""

# Deprecated: use vector_store.generate_rfi_embedding_text
def generate_rfi_text_for_embedding(title: str, description: str, discipline: str = "", equipment: str = "", location: str = "") -> str:
    """Legacy wrapper that forwards to vector_store.generate_rfi_embedding_text for backward compatibility."""
    rfi = {
        "title": title,
        "description": description,
        "discipline": discipline,
        "equipment": equipment,
        "location": location,
    }
    return vector_store.generate_rfi_embedding_text(rfi)

def seed_initial_rfis():
    """Seed baseline historical RFIs into SQLite database if empty."""
    existing = vector_store.get_all_rfis()
    if len(existing) > 0:
        return

    seed_data = [
        {
            "rfi_id": "RFI-017",
            "title": "Cable Tray Routing Adjustment",
            "description": "Power cable trays conflict with structural beam and chilled-water piping within the UPS room ceiling coordination zone.",
            "discipline": "Electrical",
            "equipment": "UPS",
            "location": "UPS Room",
            "status": "Closed",
            "priority": "HIGH",
            "raised_by": "Electrical Contractor",
            "created_at": "2026-06-15 10:00:00",
            "closed_at": "2026-06-18 14:30:00",
            "final_resolution": "Cable tray elevation revised following MEP coordination review while maintaining required clearance from mechanical services."
        },
        {
            "rfi_id": "RFI-021",
            "title": "Generator Fuel Line Routing Clash",
            "description": "Generator fuel supply piping conflicts with electrical containment near the generator room service corridor.",
            "discipline": "Mechanical",
            "equipment": "Generator",
            "location": "Generator Room",
            "status": "Closed",
            "priority": "HIGH",
            "raised_by": "Mechanical Contractor",
            "created_at": "2026-06-20 09:15:00",
            "closed_at": "2026-06-23 16:00:00",
            "final_resolution": "Fuel line routing revised through coordinated service corridor per mechanical detail drawing M-301."
        },
        {
            "rfi_id": "RFI-031",
            "title": "Data Hall Cable Tray Clearance Issue",
            "description": "Overhead cable containment does not maintain required clearance from adjacent mechanical ductwork in Data Hall 1.",
            "discipline": "Electrical",
            "equipment": "Cable Tray",
            "location": "Data Hall 1",
            "status": "Closed",
            "priority": "MEDIUM",
            "raised_by": "Electrical Contractor",
            "created_at": "2026-07-01 11:30:00",
            "closed_at": "2026-07-04 15:45:00",
            "final_resolution": "Containment elevation adjusted by -150mm and BIM coordination drawing revised."
        },
        {
            "rfi_id": "RFI-005",
            "title": "Chiller Water Pipe Connection Flange Size",
            "description": "Chilled water inlet flange connection diameter differs from specification drawing detail.",
            "discipline": "Mechanical",
            "equipment": "Chiller CH-02",
            "location": "Mechanical Yard",
            "status": "Closed",
            "priority": "MEDIUM",
            "raised_by": "Piping Contractor",
            "created_at": "2026-05-10 08:30:00",
            "closed_at": "2026-05-12 12:00:00",
            "final_resolution": "Flange adapter fittings specified per mechanical detail drawing M-402."
        },
        {
            "rfi_id": "RFI-012",
            "title": "Switchgear Busduct Alignment",
            "description": "Main switchgear busduct riser connection exhibits 50mm offset from transformer terminal flange.",
            "discipline": "Electrical",
            "equipment": "Switchgear SWGR-02",
            "location": "Switchgear Room",
            "status": "Closed",
            "priority": "CRITICAL",
            "raised_by": "Electrical Contractor",
            "created_at": "2026-06-02 14:00:00",
            "closed_at": "2026-06-05 17:30:00",
            "final_resolution": "Flexible expansion copper braided joints installed at switchgear connection interface."
        }
    ]

    for item in seed_data:
        text = generate_rfi_text_for_embedding(
            item["title"], item["description"], item["discipline"], item["equipment"], item["location"]
        )
        try:
            emb = embeddings.embed_query(text)
        except Exception:
            emb = None

        vector_store.upsert_rfi(item, embedding=emb)

def calculate_confidence(top_similarity: float, metadata_match_score: float, document_evidence_score: float) -> float:
    """Deterministic confidence calculation.
    - top_similarity: best semantic similarity (0-1)
    - metadata_match_score: normalized metadata match (0-1)
    - document_evidence_score: proportion of relevant documents (0-1)
    - precedent_quality_score: normalized hybrid score of top historical match (0-1)
    Formula: 0.55*semantic + 0.15*metadata + 0.20*doc_evidence + 0.10*precedent_quality
    """
    # Placeholder for precedent quality; will be passed as additional argument in call.
    # For simplicity, treat it as same as metadata_match_score here (can be refined later).
    confidence = (
        0.55 * top_similarity +
        0.15 * metadata_match_score +
        0.20 * document_evidence_score +
        0.10 * metadata_match_score  # using metadata as proxy for precedent quality
    )
    return min(1.0, max(0.0, round(confidence, 3)))

def analyze_rfi(rfi_data: dict) -> dict:
    """
    Perform full RFI Intelligence workflow:
    1. Embed RFI query
    2. Vector similarity search across historical RFIs
    3. Retrieve relevant project document RAG context
    4. Gemini AI resolution generation
    5. Deterministic confidence scoring & citation formatting
    """
    seed_initial_rfis()

    title = rfi_data.get("title") or rfi_data.get("subject", "")
    description = rfi_data.get("description") or rfi_data.get("question", "")
    discipline = rfi_data.get("discipline", "Electrical")
    equipment = rfi_data.get("equipment", "")
    location = rfi_data.get("location", "")
    rfi_id = rfi_data.get("rfi_id") or rfi_data.get("id")

    if not title or not description:
        raise ValueError("RFI title/subject and description/question are required.")

    # 1. Embed RFI text
    text_to_embed = generate_rfi_text_for_embedding(title, description, discipline, equipment, location)
    try:
        query_emb = embeddings.embed_query(text_to_embed)
    except Exception as e:
        query_emb = None

    threshold = get_similarity_threshold()
    similar_rfis = []
    top_match_similar = None
    top_similarity = 0.0

    # 2. Historical RFI similarity search if embedding succeeded
    if query_emb:
        similar_candidates = vector_store.find_similar_rfis(
            query_embedding=query_emb,
            top_k=5,
            exclude_rfi_id=rfi_id,
            discipline=discipline,
            equipment=equipment,
            location=location
        )

        for s in similar_candidates:
            if s["similarity_score"] >= threshold:
                similar_rfis.append(s)

        if similar_candidates:
            top_match_similar = similar_candidates[0]
            top_similarity = top_match_similar["similarity_score"]

    # 3. Retrieve relevant project document RAG context
    doc_chunks = retrieve_context(question=f"{title} {description}", top_k=5)
    relevant_doc_chunks = [c for c in doc_chunks if c.get("score", 0) >= 0.20]

    # 4. Gemini AI Suggested Resolution
    client = get_client()
    model_name = get_model_name()

    hist_summary_lines = []
    for s in similar_rfis[:3]:
        hist_summary_lines.append(
            f"- Match {s['rfi_id']} ({s['similarity_percentage']}%): Title='{s['title']}', Resolution='{s.get('final_resolution') or 'Under review'}'"
        )
    hist_context = "\n".join(hist_summary_lines) if hist_summary_lines else "No strong historical RFI matches found above threshold."

    doc_context_lines = []
    for c in relevant_doc_chunks:
        doc_context_lines.append(
            f"- Document '{c['document_name']}' (Page {c['page_number']}): {c['text'][:300]}"
        )
    doc_context = "\n".join(doc_context_lines) if doc_context_lines else "No specific project document excerpts retrieved."

    prompt = (
        f"NEW RFI DETAILS:\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Discipline: {discipline}\n"
        f"Equipment: {equipment}\n"
        f"Location: {location}\n\n"
        f"HISTORICAL PRECEDENTS:\n{hist_context}\n\n"
        f"PROJECT DOCUMENT EXCERPTS:\n{doc_context}\n\n"
        f"Generate AI suggested resolution, engineering reasoning, and recommended actions."
    )

    suggested_res = "Review technical query against MEP coordination drawings and verify field clearances."
    reasoning_text = "Analysis based on standard engineering practices and project constraints."
    rec_actions = ["Verify site clearance dimensions.", "Submit updated coordination drawing for engineer review."]

    try:
        res = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=RFI_RESOLUTION_INSTRUCTION,
                response_mime_type="application/json"
            )
        )
        if res and res.text:
            parsed = json.loads(res.text)
            suggested_res = parsed.get("suggestedResolution", suggested_res)
            reasoning_text = parsed.get("reasoning", reasoning_text)
            rec_actions = parsed.get("recommendedActions", rec_actions)
    except Exception:
        pass

    # 5. Deterministic Confidence Calculation
    # Compute metadata match score (same bonuses as hybrid scoring, normalized to 0-1)
    raw_metadata_score = 0.0
    if discipline and top_match_similar and top_match_similar.get('discipline', '').lower() == discipline.lower():
        raw_metadata_score += 0.07
    if equipment and top_match_similar and top_match_similar.get('equipment') and equipment.lower() in top_match_similar.get('equipment', '').lower():
        raw_metadata_score += 0.05
    if location and top_match_similar and top_match_similar.get('location') and location.lower() in top_match_similar.get('location', '').lower():
        raw_metadata_score += 0.03
    # Normalize metadata score to 0-1 (max possible 0.15)
    metadata_score = raw_metadata_score / 0.15 if raw_metadata_score > 0 else 0.0
    # Document evidence score: proportion of relevant doc chunks up to 5 docs
    doc_evidence_score = min(1.0, len(relevant_doc_chunks) / 5.0)
    # Precedent quality proxy: use hybrid similarity of top match (if any)
    precedent_quality = top_match_similar["similarity_score"] if top_match_similar else 0.0
    confidence = calculate_confidence(top_similarity, metadata_score, doc_evidence_score)
    # Store additional fields for response
    analysis_version = 1


    # 6. Format genuine citations
    sources = []
    for c in relevant_doc_chunks:
        sources.append({
            "document": c["document_name"],
            "page": c["page_number"],
            "section": c.get("section", "General")
        })

    # Top similar RFI object formatted for frontend
    similar_obj = None
    if top_match_similar and top_match_similar["similarity_score"] >= threshold:
        similar_obj = {
            "id": top_match_similar["rfi_id"],
            "subject": top_match_similar["title"],
            "match": top_match_similar["similarity_percentage"],
            "question": top_match_similar["description"],
            "resolution": top_match_similar.get("final_resolution") or "Resolved",
            "discipline": top_match_similar.get("discipline")
        }

    return {
        "query_embedding": query_emb,
        "similar": similar_obj,
        "semanticSimilarity": top_match_similar["raw_cosine_sim"] if top_match_similar else None,
        "hybridScore": top_match_similar["similarity_score"] if top_match_similar else None,
        "similarRFIs": [
            {
                "rfiId": s["rfi_id"],
                "title": s["title"],
                "semanticSimilarity": s["raw_cosine_sim"],
                "hybridScore": s["similarity_score"],
                "similarityPercentage": s["similarity_percentage"],
                "finalResolution": s.get("final_resolution"),
                "discipline": s.get("discipline")
            } for s in similar_rfis
        ],
        "suggestedResolution": suggested_res,
        "reasoning": reasoning_text,
        "recommendedActions": rec_actions,
        "confidence": confidence,
        "analysis_version": 1,
        "sources": sources
    }

def create_and_embed_rfi(
    title: str,
    description: str,
    discipline: str = "Electrical",
    priority: str = "HIGH",
    equipment: str = "",
    location: str = "",
    raised_by: str = "Contractor"
) -> dict:
    """Create, analyze, and persist a new RFI record."""
    if not title or not description:
        raise ValueError("RFI title and description are required.")

    # Generate sequential or unique RFI ID
    all_rfis = vector_store.get_all_rfis()
    existing_ids = [r["rfi_id"] for r in all_rfis if r["rfi_id"].startswith("RFI-")]
    
    max_num = 0
    for r_id in existing_ids:
        try:
            num = int(r_id.split("-")[1])
            if num > max_num:
                max_num = num
        except Exception:
            pass

    next_num = max_num + 1
    rfi_id = f"RFI-{next_num:03d}"

    now_str = datetime.utcnow().strftime("%d %b %Y")

    rfi_data = {
        "rfi_id": rfi_id,
        "title": title,
        "description": description,
        "discipline": discipline,
        "equipment": equipment,
        "location": location,
        "status": "Open",
        "priority": priority,
        "raised_by": raised_by,
        "created_at": now_str
    }

    # Execute RFI Intelligence Analysis
    analysis_res = analyze_rfi(rfi_data)

    query_emb = analysis_res.pop("query_embedding", None)

    # Persist RFI record and embedding in SQLite
    vector_store.upsert_rfi(rfi_data, embedding=query_emb, analysis=analysis_res)

    top_match_pct = analysis_res["similar"]["match"] if analysis_res.get("similar") else 0

    return {
        "id": rfi_id,
        "subject": title,
        "discipline": discipline,
        "priority": priority,
        "status": "Open",
        "aiMatch": top_match_pct,
        "created": now_str,
        "question": description,
        "equipment": equipment,
        "location": location,
        "raisedBy": raised_by,
        "similar": analysis_res.get("similar"),
        "suggested": analysis_res.get("suggestedResolution"),
        "reasoning": analysis_res.get("reasoning"),
        "recommendedActions": analysis_res.get("recommendedActions"),
        "confidence": analysis_res.get("confidence"),
        "sources": analysis_res.get("sources")
    }

def get_rfi_detail(rfi_id: str) -> Optional[dict]:
    """Retrieve full RFI detail by ID."""
    rfi = vector_store.get_rfi_by_id(rfi_id)
    if not rfi:
        return None

    analysis = rfi.get("analysis") or {}

    return {
        "id": rfi["rfi_id"],
        "subject": rfi["title"],
        "discipline": rfi["discipline"],
        "priority": rfi["priority"],
        "status": rfi["status"],
        "aiMatch": analysis.get("similar", {}).get("match", 0) if analysis.get("similar") else 0,
        "created": rfi["created_at"][:11] if rfi.get("created_at") else "Today",
        "question": rfi["description"],
        "equipment": rfi.get("equipment"),
        "location": rfi.get("location"),
        "raisedBy": rfi.get("raised_by"),
        "similar": analysis.get("similar"),
        "suggested": analysis.get("suggestedResolution"),
        "reasoning": analysis.get("reasoning"),
        "recommendedActions": analysis.get("recommendedActions"),
        "confidence": analysis.get("confidence"),
        "sources": analysis.get("sources"),
        "finalResolution": rfi.get("final_resolution")
    }
