import os
import sys
import json
import logging

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_compliance_test_pdfs import generate_requirement_pdf, generate_vendor_pdf
from services.document_service import ingest_pdf_bytes
from services.compliance_service import analyze_compliance
from rag import vector_store
from rag import rag_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_compliance")

def run_verification():
    print("=" * 70)
    print("         EPCMIND AI -- STAGE 3 COMPLIANCE VERIFICATION          ")
    print("=" * 70)

    # 1. Ingest controlled test PDFs
    print("\n[STEP 1] Generating and ingesting test PDFs...")
    req_pdf_path = generate_requirement_pdf()
    vendor_pdf_path = generate_vendor_pdf()

    with open(req_pdf_path, "rb") as f:
        req_meta = ingest_pdf_bytes("Requirement_Specification_Test.pdf", f.read())
    
    with open(vendor_pdf_path, "rb") as f:
        vendor_meta = ingest_pdf_bytes("Vendor_Submittal_Test.pdf", f.read())

    req_doc_id = req_meta["document_id"]
    vendor_doc_id = vendor_meta["document_id"]

    print(f"[OK] Requirement Document ID: {req_doc_id}")
    print(f"[OK] Vendor Submittal Document ID: {vendor_doc_id}")

    # 2. Run Specification Compliance Analysis
    print("\n[STEP 2] Executing compliance analysis...")
    res = analyze_compliance(
        requirement_document_id=req_doc_id,
        vendor_document_id=vendor_doc_id,
        equipment="UPS-04",
        discipline="Electrical"
    )

    checks = res["checks"]
    stats = res["stats"]

    print(f"\n[ANALYSIS STATS] Total: {stats['total']} | Compliant: {stats['compliant']} | Non-Compliant: {stats['nonCompliant']} | Not Verifiable: {stats['notVerifiable']} | High Severity: {stats['highSeverity']}")
    print("-" * 70)

    # Dictionary lookup by parameter keyword
    checks_by_param = {}
    for c in checks:
        p_lower = c["parameter"].lower()
        checks_by_param[p_lower] = c
        print(f"Parameter: {c['parameter']:<25} | Req: {c['requirement']:<10} | Vendor: {c['vendorValue']:<10} | Status: {c['status']:<15} | Severity: {c['severity']}")

    # 3. Controlled Parameter Validations
    print("\n[STEP 3] Validating 6 parameter test cases...")

    def find_check(keyword):
        for k, v in checks_by_param.items():
            if keyword in k:
                return v
        return None

    # Parameter 1: UPS Efficiency
    ups_eff = find_check("efficiency")
    assert ups_eff is not None, "UPS Efficiency check missing"
    assert ups_eff["status"] == "NON-COMPLIANT", f"Expected NON-COMPLIANT, got {ups_eff['status']}"
    assert "-1.2" in str(ups_eff.get("deviation")), f"Expected -1.2 deviation, got {ups_eff.get('deviation')}"
    assert ups_eff["requirementSource"]["page"] == 1, "Requirement page mismatch for UPS Efficiency"
    assert ups_eff["vendorSource"]["page"] == 1, "Vendor page mismatch for UPS Efficiency"
    print("[OK] Parameter 1: UPS Efficiency (>=96% vs 94.8% -> NON-COMPLIANT, -1.2%, Req Page 1, Vendor Page 1) PASSED")

    # Parameter 2: Battery Autonomy
    autonomy = find_check("autonomy")
    assert autonomy is not None, "Battery Autonomy check missing"
    assert autonomy["status"] == "NON-COMPLIANT", f"Expected NON-COMPLIANT, got {autonomy['status']}"
    assert "-3" in str(autonomy.get("deviation")), f"Expected -3 deviation, got {autonomy.get('deviation')}"
    assert autonomy["requirementSource"]["page"] == 2, "Requirement page mismatch for Battery Autonomy"
    assert autonomy["vendorSource"]["page"] == 2, "Vendor page mismatch for Battery Autonomy"
    print("[OK] Parameter 2: Battery Autonomy (>=15 min vs 12 min -> NON-COMPLIANT, -3 min, Req Page 2, Vendor Page 2) PASSED")

    # Parameter 3: UPS Redundancy
    ups_red = find_check("ups redundancy")
    assert ups_red is not None, "UPS Redundancy check missing"
    assert ups_red["status"] == "COMPLIANT", f"Expected COMPLIANT, got {ups_red['status']}"
    assert ups_red["requirementSource"]["page"] == 3, "Requirement page mismatch for UPS Redundancy"
    assert ups_red["vendorSource"]["page"] == 3, "Vendor page mismatch for UPS Redundancy"
    print("[OK] Parameter 3: UPS Redundancy (N+1 vs N+1 -> COMPLIANT, Req Page 3, Vendor Page 3) PASSED")

    # Parameter 4: Generator Runtime
    gen_run = find_check("generator")
    assert gen_run is not None, "Generator Runtime check missing"
    assert gen_run["status"] == "COMPLIANT", f"Expected COMPLIANT, got {gen_run['status']}"
    assert gen_run["requirementSource"]["page"] == 4, "Requirement page mismatch for Generator Runtime"
    assert gen_run["vendorSource"]["page"] == 4, "Vendor page mismatch for Generator Runtime"
    print("[OK] Parameter 4: Generator Runtime (>=48h vs 52h -> COMPLIANT, Req Page 4, Vendor Page 4) PASSED")

    # Parameter 5: Cooling Redundancy
    cool_red = find_check("cooling")
    assert cool_red is not None, "Cooling Redundancy check missing"
    assert cool_red["status"] == "NON-COMPLIANT", f"Expected NON-COMPLIANT, got {cool_red['status']}"
    assert cool_red["requirementSource"]["page"] == 5, "Requirement page mismatch for Cooling Redundancy"
    assert cool_red["vendorSource"]["page"] == 5, "Vendor page mismatch for Cooling Redundancy"
    print("[OK] Parameter 5: Cooling Redundancy (N+1 vs N -> NON-COMPLIANT, Req Page 5, Vendor Page 5) PASSED")

    # Parameter 6: Battery Design Life (Missing parameter test)
    life_check = find_check("design life")
    assert life_check is not None, "Battery Design Life check missing"
    assert life_check["status"] == "NOT_VERIFIABLE", f"Expected NOT_VERIFIABLE, got {life_check['status']}"
    assert life_check["requirementSource"]["page"] == 6, "Requirement page mismatch for Battery Design Life"
    assert life_check["vendorSource"] is None, "Vendor source MUST BE None for missing parameter"
    print("[OK] Parameter 6: Battery Design Life (>=10 years vs missing -> NOT_VERIFIABLE, Req Page 6, Vendor Source NONE) PASSED")

    # 4. Error Handling Validations
    print("\n[STEP 4] Testing error scenarios...")

    # Same document selected twice
    try:
        analyze_compliance(req_doc_id, req_doc_id)
        assert False, "Should have failed for identical document IDs"
    except ValueError as e:
        print(f"[OK] Error test (Same document IDs): Caught expected exception: {e}")

    # Invalid document ID
    try:
        analyze_compliance("non_existent_doc_id", vendor_doc_id)
        assert False, "Should have failed for non-existent document ID"
    except ValueError as e:
        print(f"[OK] Error test (Invalid Document ID): Caught expected exception: {e}")

    # 5. SQLite Persistence Verification
    print("\n[STEP 5] Testing SQLite persistence...")
    latest = vector_store.get_latest_compliance_analysis()
    assert latest is not None, "No compliance analysis found in DB"
    assert latest["req_doc_id"] == req_doc_id, "Persisted req_doc_id mismatch"
    assert latest["stats"]["total"] == stats["total"], "Persisted stats mismatch"
    print(f"[OK] Persistence test: Successfully fetched saved analysis '{latest['analysis_id']}' with {len(latest['checks'])} checks")

    # 6. Copilot RAG Regression Test
    print("\n[STEP 6] Testing normal Copilot RAG regression...")
    rag_res = rag_service.ask_copilot_rag("What is the required UPS efficiency?")
    assert "96" in rag_res["content"], f"RAG response missing 96%: {rag_res['content']}"
    assert len(rag_res["sources"]) > 0, "RAG response missing source citations"
    print(f"[OK] Copilot RAG regression test: Answered correctly with {len(rag_res['sources'])} citations.")

    print("\n" + "=" * 70)
    print("        ALL 10 COMPLIANCE VERIFICATION TESTS PASSED!          ")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
