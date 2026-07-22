import os
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def get_embedding_model_name() -> str:
    """Return the configured embedding model name."""
    return os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

def get_client():
    """Configure API key and return genai module for embeddings."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("Gemini API key is not configured.")
    genai.configure(api_key=api_key)
    return genai

def embed_query(text: str) -> List[float]:
    """Embed a single search query string using genai.embed_content."""
    client = get_client()
    model = get_embedding_model_name()
    res = client.embed_content(model=model, content=text)
    if hasattr(res, "embedding"):
        return list(res.embedding)
    raise ValueError("Failed to generate embedding for query.")

def embed_documents(texts: List[str]) -> List[List[float]]:
    """Embed a list of document chunk texts."""
    client = get_client()
    model = get_embedding_model_name()
    embeddings = []
    
    # Process each text to ensure reliable response handling
    for text in texts:
        res = client.embed_content(model=model, content=text)
        if hasattr(res, "embedding"):
            embeddings.append(list(res.embedding))
        else:
            raise ValueError(f"Failed to generate embedding for chunk: {text[:30]}...")

    return embeddings
