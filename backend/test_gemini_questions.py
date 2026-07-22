import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env')

from services.gemini_service import ask_gemini, get_copilot_status

questions = [
    ("A. Required UPS Efficiency", "What is the required UPS efficiency?"),
    ("B. Commissioning Schedule Risk", "Which equipment currently threatens the commissioning schedule?"),
    ("C. Battery Autonomy Requirement", "What is the required battery autonomy?"),
    ("D. RFI-042 Information", "Tell me about RFI-042."),
    ("E. Data Hall 3 Fire Suppression", "What fire suppression system is specified for Data Hall 3?")
]

def main():
    print("=== GEMINI COPILOT STATUS ===")
    status = get_copilot_status()
    print(f"Configured: {status['configured']}")
    print(f"Provider:   {status['provider']}")
    print(f"Model:      {status['model']}")
    print("==============================\n")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("[NOTICE] GEMINI_API_KEY is not configured or using default template value.")
        print("[NOTICE] Testing unconfigured state handling (server must not crash):\n")
        res = ask_gemini(questions[0][1])
        print(f"Response role: {res.get('role')}")
        print(f"Response content: {res.get('content')}")
        print(f"Response sources: {res.get('sources')}")
        print(f"Response meta: {res.get('meta')}\n")
        return

    print("Executing 5 Test Questions against Gemini API...\n")
    for title, q in questions:
        print(f"--- Question {title} ---")
        print(f"Q: {q}")
        res = ask_gemini(q)
        print(f"Role: {res.get('role')}")
        print(f"Content: {res.get('content')}")
        print(f"Sources: {res.get('sources')}")
        print(f"Meta: {res.get('meta')}")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    main()
