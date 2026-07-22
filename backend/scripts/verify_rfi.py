import os
import sys
import json
import logging

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.rfi_service import seed_initial_rfis, create_and_embed_rfi, get_rfi_detail, analyze_rfi
from rag import vector_store, rag_service
from services import compliance_service, document_service
from scripts.generate_compliance_test_pdfs import generate_requirement_pdf, generate_vendor_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_rfi")

def run_verification():
    print("=" * 70)
    print("           EPCMIND AI -- STAGE 4 RFI VERIFICATION             ")
    print("=" * 70)

    # 1. Seed historical RFI dataset
    print("\n[STEP 1] Seeding baseline historical RFI dataset...")
    seed_initial_rfis()
    all_rfis = vector_store.get_all_rfis()
    print(f"[OK] Total RFIs in database: {len(all_rfis)}")
    rfi_ids = [r["rfi_id"] for r in all_rfis]
    assert "RFI-017" in rfi_ids, "RFI-017 missing from database"
    assert "RFI-021" in rfi_ids, "RFI-021 missing from database"
    assert "RFI-031" in rfi_ids, "RFI-031 missing from database"
    print("[OK] Baseline RFIs (RFI-017, RFI-021, RFI-031, etc.) seeded successfully.")

    # 2. Primary Test RFI Creation & Historical Similarity Search (RFI-042)
    print("\n[STEP 2] Creating RFI-042 (UPS Room Cable Routing Conflict)...")
    rfi_042 = create_and_embed_rfi(
        title="UPS Room Cable Routing Conflict",
        description="Electrical cable tray routing conflicts with chilled water pipework above UPS equipment, preventing required service clearance.",
        discipline="Electrical",
        priority="HIGH",
        equipment="UPS-04",
        location="UPS Room",
        raised_by="Electrical Contractor"
    )

    print(f"[OK] Created RFI ID: {rfi_042['id']}")
    print(f"[OK] Subject: {rfi_042['subject']}")
    print(f"[OK] AI Match Percentage: {rfi_042['aiMatch']}%")

    # Verify RFI-017 is the top match
    assert rfi_042["similar"] is not None, "Expected similar RFI match for RFI-042"
    top_match = rfi_042["similar"]
    print(f"[OK] Strongest Match ID: {top_match['id']} ({top_match['match']}%) -- {top_match['subject']}")
    assert top_match["id"] == "RFI-017", f"Expected RFI-017 as top match, got {top_match['id']}"
    assert top_match["match"] >= 70, f"Expected strong match score >= 70%, got {top_match['match']}%"

    # 3. Negative Similarity Test (RFI-099)
    print("\n[STEP 3] Testing negative similarity case (RFI-099 Landscape Irrigation)...")
    rfi_099 = create_and_embed_rfi(
        title="Landscape Irrigation Drainage Issue",
        description="External irrigation drainage does not discharge correctly near landscape boundary.",
        discipline="Civil",
        priority="LOW",
        equipment="Drainage",
        location="External Works",
        raised_by="Civil Contractor"
    )

    print(f"[OK] Created RFI ID: {rfi_099['id']}")
    print(f"[OK] Subject: {rfi_099['subject']}")
    assert rfi_099["similar"] is None, f"Landscape RFI should not have a strong match above threshold 0.75, got {rfi_099.get('similar')}"
    print("[OK] Negative similarity test passed -- weak match correctly filtered out.")


    # 4. Gemini Suggested Resolution & Reasoning
    print("\n[STEP 4] Validating Gemini suggested resolution & engineering reasoning...")
    suggested = rfi_042.get("suggested")
    reasoning = rfi_042.get("reasoning")
    actions = rfi_042.get("recommendedActions")

    assert suggested is not None and len(suggested) > 20, "Suggested resolution missing or too short"
    assert reasoning is not None, "Engineering reasoning missing"
    assert actions is not None and len(actions) > 0, "Recommended actions missing"
    print(f"[OK] AI Suggested Resolution: {suggested[:100]}...")
    print(f"[OK] Recommended Actions Count: {len(actions)}")

    # 5. Deterministic Confidence Score
    print("\n[STEP 5] Validating deterministic confidence score calculation...")
    confidence = rfi_042.get("confidence")
    assert confidence is not None, "Confidence score missing"
    assert 0.35 <= confidence <= 0.95, f"Confidence out of expected range [0.35, 0.95]: {confidence}"
    print(f"[OK] Deterministic Confidence Score: {confidence} ({int(confidence * 100)}%)")

    # 6. Genuine Project Document Sources
    print("\n[STEP 6] Validating genuine project document citations...")
    sources = rfi_042.get("sources")
    print(f"[OK] Retrieved RAG Sources Count: {len(sources) if sources else 0}")
    if sources:
        for s in sources:
            assert "document" in s and "page" in s, "Source object missing document/page keys"
            print(f"  - Document: {s['document']} (Page {s['page']})")

    # 7. SQLite Persistence Verification
    print("\n[STEP 7] Testing SQLite persistence across reload...")
    fetched_detail = get_rfi_detail(rfi_042["id"])
    assert fetched_detail is not None, f"Could not fetch {rfi_042['id']} from SQLite DB"
    assert fetched_detail["subject"] == rfi_042["subject"], "Persisted subject mismatch"
    assert fetched_detail["similar"]["id"] == "RFI-017", "Persisted similar RFI mismatch"
    print(f"[OK] Persistence test: Successfully reloaded {fetched_detail['id']} from SQLite DB.")

    # 8. Error Handling Tests
    print("\n[STEP 8] Testing error handling scenarios...")

    # Missing title/description
    try:
        create_and_embed_rfi("", "")
        assert False, "Should have failed for empty title/description"
    except ValueError as e:
        print(f"[OK] Missing fields test: Caught expected exception: {e}")

    # Non-existent RFI ID lookup
    missing_detail = get_rfi_detail("RFI-NON-EXISTENT")
    assert missing_detail is None, "Expected None for non-existent RFI ID"
    print("[OK] Non-existent RFI ID lookup test passed.")

    # 9. Copilot RAG Regression Test
    print("\n[STEP 9] Testing Copilot RAG regression...")
    rag_res = rag_service.ask_copilot_rag("What is the required UPS efficiency?")
    assert "96" in rag_res["content"], f"RAG response missing 96%: {rag_res['content']}"
    print(f"[OK] Copilot RAG regression test passed.")

    # 10. Specification Compliance API Regression Test
    print("\n[STEP 10] Testing Specification Compliance API regression...")
    req_pdf_path = generate_requirement_pdf()
    vendor_pdf_path = generate_vendor_pdf()

    with open(req_pdf_path, "rb") as f:
        req_meta = document_service.ingest_pdf_bytes("Requirement_Specification_Test.pdf", f.read())
    with open(vendor_pdf_path, "rb") as f:
        vendor_meta = document_service.ingest_pdf_bytes("Vendor_Submittal_Test.pdf", f.read())

    comp_res = compliance_service.analyze_compliance(
        requirement_document_id=req_meta["document_id"],
        vendor_document_id=vendor_meta["document_id"]
    )
    assert len(comp_res["checks"]) >= 5, "Compliance analysis regression check failed"
    print(f"[OK] Specification Compliance regression test passed ({len(comp_res['checks'])} checks evaluated).")

    print("\n" + "=" * 70)
    print("          ALL 10 RFI VERIFICATION TESTS PASSED!               ")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
