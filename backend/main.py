import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api import project, documents, compliance, rfis, risks, schedule, dashboard, copilot

load_dotenv()

app = FastAPI(title="EPCMind AI Backend")

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "EPCMind AI Backend"
    }

app.include_router(project.router)
app.include_router(documents.router)
app.include_router(compliance.router)
app.include_router(rfis.router)
app.include_router(risks.router)
app.include_router(schedule.router)
app.include_router(dashboard.router)
app.include_router(copilot.router)
