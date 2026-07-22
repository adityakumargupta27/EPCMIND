import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types
from models.schemas import AIMessage

load_dotenv()


SYSTEM_INSTRUCTION = """You are EPCMind AI, an engineering intelligence assistant for a hyperscale data centre EPC project.
You assist project managers and engineering teams with questions related to:
- electrical systems
- mechanical systems
- cooling
- UPS systems
- generators
- commissioning
- project schedules
- construction risks
- RFIs
- engineering specifications
- quality and compliance

Be concise, professional and engineering-focused.
If information is not available in the supplied project context, clearly state that it cannot be verified.
Never fabricate project specifications, document citations, equipment values or compliance requirements.
You MUST format your response as a valid JSON object matching the requested schema.
"""

PROJECT_CONTEXT = """
Project: Bengaluru Hyperscale Data Centre
Code: BLR-DC-01
Location: Bengaluru, Karnataka
Capacity: 48 MW
Tier: Tier III
Phase: MEP Installation & Commissioning
Progress: 72%
Health: 78/100
Status: At Risk

Known project intelligence:
UPS-04 delivery delay: 12 days
Available schedule float: 4 days
Potential schedule exposure: 8 days
Affected milestone: Integrated Systems Testing

UPS efficiency requirement: >=96%
Vendor submitted: 94.8%
Deviation: -1.2%

Battery autonomy: Required >=15 minutes
Vendor: 12 minutes

RFI-042: UPS Room Cable Routing Conflict
Similarity: 91%
Historical match: RFI-017
"""

def get_model_name() -> str:
    """Return the configured Gemini model from environment or fallback default."""
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def get_client():
    """Configure Google Generative AI and return a wrapper compatible with previous interface."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API key is not configured. Please set GEMINI_API_KEY in backend/.env.")
    genai.configure(api_key=api_key)
    class _Wrapper:
        def __init__(self, model_name: str):
            self._model = genai.GenerativeModel(model_name)
        @property
        def models(self):
            return self
        def generate_content(self, model, contents, config=None):
            # New API does not use the model argument; ignore it.
            return self._model.generate_content(contents)
    return _Wrapper(get_model_name())

def get_copilot_status() -> dict:
    """Return status information for the Copilot service without leaking API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    is_configured = bool(api_key and api_key != "your_gemini_api_key_here")
    return {
        "configured": is_configured,
        "provider": "Google Gemini",
        "model": get_model_name()
    }

def ask_gemini(question: str) -> dict:
    """
    Send question to Gemini with project context and return AIMessage dictionary.
    Handles all API, missing key, rate limit, timeout, and response parsing errors gracefully.
    """
    model_name = get_model_name()
    
    try:
        client = get_client()
    except ValueError as err:
        return {
            "role": "assistant",
            "content": str(err),
            "sources": [{"document": "Demo Project Context", "section": "System", "page": 1}],
            "meta": {"action": "Configure GEMINI_API_KEY"}
        }

    prompt = f"PROJECT CONTEXT:\n{PROJECT_CONTEXT}\n\nUSER QUESTION:\n{question}"

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=AIMessage.model_json_schema()
            ),
        )
    except Exception as e:
        return {
            "role": "assistant",
            "content": f"Gemini API request failed: {str(e)}",
            "sources": [{"document": "Demo Project Context", "section": "System", "page": 1}],
            "meta": {"action": "Retry Request"}
        }

    if not response or not response.text:
        return {
            "role": "assistant",
            "content": "Received empty response from Gemini AI service.",
            "sources": [{"document": "Demo Project Context", "section": "System", "page": 1}],
            "meta": {"action": "Retry Request"}
        }

    try:
        data = json.loads(response.text)
        data["role"] = "assistant"
        
        # Normalize sources to avoid fabricated doc names in pre-RAG mode
        if "sources" not in data or not data["sources"]:
            data["sources"] = [{"document": "Demo Project Context", "section": "Summary", "page": 1}]
        else:
            # Override document name to Demo Project Context if not specified or fabricated
            for s in data["sources"]:
                if isinstance(s, dict):
                    s["document"] = "Demo Project Context"

        return data
    except Exception as e:
        return {
            "role": "assistant",
            "content": f"Failed to parse response: {str(e)}",
            "sources": [{"document": "Demo Project Context", "section": "System", "page": 1}],
            "meta": {"action": "System Error"}
        }
