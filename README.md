# EPCMind

Engineering, Procurement, and Construction (EPC) Compliance & Document Intelligence Platform

---

## Overview

EPCMind is an enterprise-grade document intelligence and compliance verification system designed for the Engineering, Procurement, and Construction (EPC) sector. Large-scale capital projects generate tens of thousands of pages across technical specifications, contract clauses, vendor submittals, and industry standard codes (ISO, IEEE, ASME, OSHA). 

EPCMind integrates a high-performance FastAPI backend with vector search and large language models (Google Gemini API) to ingest complex industrial technical specifications, verify multi-tier compliance, calculate forensic risk matrices, and automatically generate formal Requests for Information (RFIs).

---

## Key Capabilities

### Technical Specification Parsing & Vector Ingestion
- Document Ingestion Pipeline: Ingests unstructured industrial engineering documentation (e.g., electrical distribution systems, UPS technical specifications, mechanical piping P&IDs).
- Chunking & Semantic Vectorization: Splits dense technical documents by engineering section, numbering schema, and cross-referenced standards for sub-second retrieval.

### Multi-Dimensional Compliance Verification
- Automated Clause Verification: Cross-references contractor submittals against contractual specifications to flag compliance gaps, ambiguities, and scope deviations.
- Code Standards Cross-Referencing: Checks submissions against cited international engineering benchmarks (IEEE, ASME, IEC, NEC).

### Risk Matrix & Forensic Dashboards
- Project Risk Quantification: Computes compound project risk indicators across schedule impact, financial exposure, regulatory liability, and safety compliance.
- Interactive Analytical Dashboards: Real-time visibility into open non-conformance reports (NCRs), pending submittals, and engineering milestones.

### Automated RFI (Request for Information) Synthesis
- Discrepancy Detection: Flags engineering inconsistencies between design drawings and technical specifications.
- Formal RFI Generation: Generates standardized, audit-ready engineering RFIs complete with document citations, section clauses, and proposed resolutions.

### Engineering Copilot
- Context-Aware Technical Assistant: An integrated conversational copilot enabling project managers and lead engineers to perform complex queries against the entire project document archive.

---

## System Architecture

```
                       [ Web Dashboard ]
                 React + TypeScript + Vite
                 Tailwind CSS + Radix UI
                             |
                       REST API (JSON)
                             |
                   [ FastAPI Backend Core ]
                     Python 3.13 Async API
                             |
        +--------------------+--------------------+
        |                    |                    |
 [ API Modules ]      [ Document RAG ]     [ Risk & Audit ]
 - /api/project       - /api/documents     - /api/compliance
 - /api/rfis          - Vector Extraction  - /api/risks
 - /api/schedule      - Semantic Search    - /api/dashboard
 - /api/copilot       - Clause Matching    - Risk Matrix
        |                    |                    |
        +--------------------+--------------------+
                             |
                     [ AI Inference ]
                    Google Gemini API
                   LangChain / Vector Store
```

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Backend Framework | Python 3.13, FastAPI, Uvicorn (ASGI) |
| AI & Extraction | Google Gemini API, PyPDF, Vector Embeddings, LangChain |
| Frontend Framework | React 18, TypeScript, Vite |
| UI & Design System | Tailwind CSS, Radix UI Primitives, Lucide Icons |
| State & Networking | Axios, React Query, React Hook Form, Zod |
| Analytics & Visualization | Recharts, Custom Risk Heatmaps |

---

## API Architecture

The FastAPI backend exposes dedicated modular routers:

| Endpoint Router | Path | Responsibilities |
|---|---|---|
| Projects | `/api/project` | Project scope, metadata, and contractual parameters |
| Documents | `/api/documents` | File upload, OCR, chunking, and vector indexing |
| Compliance | `/api/compliance` | Clause-by-clause verification and deviation scoring |
| RFIs | `/api/rfis` | Automated RFI drafting, approval cycles, and tracking |
| Risks | `/api/risks` | Quantitative project risk matrix evaluation |
| Schedule | `/api/schedule` | Critical path timeline tracking and delay projection |
| Dashboard | `/api/dashboard` | Aggregated executive KPIs and operational summaries |
| Copilot | `/api/copilot` | Natural-language document question-answering |

---

## Getting Started

### Prerequisites
- Python (v3.11 or higher)
- Node.js (v20.0.0 or higher)
- Google Gemini API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Add your `GEMINI_API_KEY` and host configurations.

5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   API interactive documentation will be accessible at `http://localhost:8000/docs`.

### Frontend Setup
1. Navigate to the project root:
   ```bash
   cd ..
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Set `VITE_API_URL=http://localhost:8000`.

4. Start frontend development server:
   ```bash
   npm run dev
   ```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
