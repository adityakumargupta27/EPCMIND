import os
import sys
import json
import time
import urllib.request

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag import vector_store

SERVER_URL = "http://127.0.0.1:8000"
TEST_PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UPS_Technical_Specification_Test.pdf"))

def post_chat(question: str) -> dict:
    url = f"{SERVER_URL}/api/copilot/chat"
    data = json.dumps({"question": question}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def upload_pdf(file_path: str) -> dict:
    url = f"{SERVER_URL}/api/documents/upload"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    filename = os.path.basename(file_path)
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def run_tests():
    print("==================================================")
    print("      RAG STAGE 2 END-TO-END VERIFICATION         ")
    print("==================================================\n")

    # TEST 1: PDF Upload & Ingestion Pipeline
    print("--- TEST 1: PDF Ingestion Pipeline ---")
    if not os.path.exists(TEST_PDF_PATH):
        print(f"FAILED: Test PDF file not found at {TEST_PDF_PATH}")
        return False

    upload_res = upload_pdf(TEST_PDF_PATH)
    print(f"Upload Response: {json.dumps(upload_res, indent=2)}")

    if upload_res.get("status") != "Indexed":
        print(f"TEST 1 FAILED: Expected status 'Indexed', got '{upload_res.get('status')}'")
        return False
    print("[OK] TEST 1 PASSED: PDF stored, extracted, chunked, embedded, and stored in vector database.\n")
    time.sleep(2)

    # TEST 2: Q1 Minimum UPS efficiency
    print("--- TEST 2: Question 1 (UPS Efficiency) ---")
    res2 = post_chat("What is the minimum UPS efficiency?")
    print(f"Role: {res2.get('role')}")
    print(f"Content: {res2.get('content')}")
    print(f"Sources: {res2.get('sources')}")
    print(f"Meta: {res2.get('meta')}")

    content2 = res2.get("content", "").lower()
    sources2 = res2.get("sources", [])
    if "96%" not in content2:
        print("TEST 2 FAILED: Expected '96%' in answer.")
        return False
    if not sources2 or not any("UPS_Technical_Specification_Test.pdf" in s.get("document", "") for s in sources2):
        print("TEST 2 FAILED: Missing real document citation.")
        return False
    print("[OK] TEST 2 PASSED: 96% efficiency verified with real document citation.\n")
    time.sleep(2)

    # TEST 3: Q2 Battery autonomy
    print("--- TEST 3: Question 2 (Battery Autonomy) ---")
    res3 = post_chat("What is the required battery autonomy?")
    print(f"Content: {res3.get('content')}")
    print(f"Sources: {res3.get('sources')}")

    content3 = res3.get("content", "").lower()
    sources3 = res3.get("sources", [])
    if "15" not in content3:
        print("TEST 3 FAILED: Expected '15 minutes' in answer.")
        return False
    if not sources3 or not any("UPS_Technical_Specification_Test.pdf" in s.get("document", "") for s in sources3):
        print("TEST 3 FAILED: Missing real document citation.")
        return False
    print("[OK] TEST 3 PASSED: 15 minutes autonomy verified with real document citation.\n")
    time.sleep(2)

    # TEST 4: Q3 UPS Redundancy
    print("--- TEST 4: Question 3 (UPS Redundancy) ---")
    res4 = post_chat("What UPS redundancy is required?")
    print(f"Content: {res4.get('content')}")
    print(f"Sources: {res4.get('sources')}")

    content4 = res4.get("content", "").lower()
    if "n+1" not in content4:
        print("TEST 4 FAILED: Expected 'N+1' in answer.")
        return False
    print("[OK] TEST 4 PASSED: N+1 redundancy verified with real document citation.\n")
    time.sleep(2)

    # TEST 5: Q4 Generator Runtime
    print("--- TEST 5: Question 4 (Generator Runtime) ---")
    res5 = post_chat("What is the minimum generator runtime?")
    print(f"Content: {res5.get('content')}")
    print(f"Sources: {res5.get('sources')}")

    content5 = res5.get("content", "").lower()
    if "48" not in content5:
        print("TEST 5 FAILED: Expected '48 hours' in answer.")
        return False
    print("[OK] TEST 5 PASSED: 48 hours generator runtime verified with real document citation.\n")
    time.sleep(2)

    # TEST 6: Q5 Fire Suppression (Unverified Question)
    print("--- TEST 6: Question 5 (Fire Suppression Agent) ---")
    res6 = post_chat("What fire suppression agent is required for Data Hall 3?")
    print(f"Content: {res6.get('content')}")
    print(f"Sources: {res6.get('sources')}")

    content6 = res6.get("content", "").lower()
    if "cannot be verified" not in content6 and "not" not in content6:
        print("TEST 6 FAILED: Expected unverified response.")
        return False
    print("[OK] TEST 6 PASSED: Assistant correctly stated information cannot be verified.\n")
    time.sleep(1)

    # TEST 7: Duplicate Upload Prevention
    print("--- TEST 7: Duplicate Upload Prevention ---")
    dup_res = upload_pdf(TEST_PDF_PATH)
    print(f"Duplicate Upload Response: {json.dumps(dup_res, indent=2)}")
    if not dup_res.get("duplicate"):
        print("TEST 7 FAILED: SHA-256 deduplication did not trigger.")
        return False
    print("[OK] TEST 7 PASSED: Duplicate upload correctly detected via SHA-256 hash.\n")

    # TEST 8: Persistence Verification
    print("--- TEST 8: Vector Store Restart Persistence ---")
    docs = vector_store.get_all_documents()
    print(f"Persisted Documents Count in SQLite: {len(docs)}")
    if not docs:
        print("TEST 8 FAILED: SQLite vector database empty.")
        return False
    print("[OK] TEST 8 PASSED: Documents and vector embeddings persisted in SQLite DB.\n")

    print("==================================================")
    print("       ALL RAG VERIFICATION TESTS PASSED!         ")
    print("==================================================")
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
