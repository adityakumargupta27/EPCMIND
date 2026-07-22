import os
import re
import json
import uuid
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from services.gemini_service import get_client, get_model_name
from rag import vector_store
from rag.retriever import retrieve_context

REQ_EXTRACTION_INSTRUCTION = """You are an engineering compliance AI. Analyze the provided technical specification text excerpt and extract technical requirements.

For each requirement found, extract:
- parameter: Parameter name (e.g., 'UPS Efficiency', 'Battery Autonomy', 'UPS Redundancy', 'Generator Runtime', 'Cooling Redundancy', 'Battery Design Life').
- operator: Comparison operator (e.g., '>=', '<=', '==', 'N+1', 'minimum').
- required_value: Complete value string (e.g., '>=96%', '>=15 min', 'N+1', '>=48 hours', '>=10 years').
- raw_numeric: Numeric value if applicable (e.g., 96.0, 15.0, 48.0, 10.0) or null if non-numeric.
- unit: Measurement unit (e.g., '%', 'minutes', 'hours', 'years', 'none').

Format output as a valid JSON object matching the requested schema.
"""

VENDOR_EXTRACTION_INSTRUCTION = """You are an engineering compliance AI. Extract the vendor's submitted value for a specific requested parameter from the provided vendor submittal text excerpt.

Parameter to find: {parameter}

Extract:
- found: True if the parameter is specified in the text excerpt, False otherwise.
- vendor_value: Complete submitted value string (e.g., '94.8%', '12 minutes', 'N+1', '52 hours', 'N') or null if not found.
- raw_numeric: Numeric value if applicable (e.g. 94.8, 12.0, 52.0) or null.
- unit: Measurement unit (e.g., '%', 'minutes', 'hours', 'none') or null.

Format output as a valid JSON object matching the requested schema.
"""

ENGINEERING_ANALYSIS_INSTRUCTION = """You are an EPC Mind AI engineering consultant.
Given a technical requirement comparison, provide:
- analysis: A concise 1-2 sentence engineering assessment explaining the compliance status or deviation.
- impact: A list of 1-3 potential technical or operational impacts.
- action: A clear 1-sentence recommended engineering action.
- severity: One of 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'.

Format output as a valid JSON object matching the requested schema.
"""

def parse_numeric(val_str: str) -> Optional[float]:
    """Extract first numeric float from a string."""
    if not val_str:
        return None
    match = re.search(r'(\d+(?:\.\d+)?)', str(val_str))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

def normalize_unit(unit_str: str) -> str:
    """Normalize common engineering units."""
    if not unit_str:
        return ""
    u = unit_str.lower().strip()
    if u in ["%", "percent", "percentage"]:
        return "%"
    if u in ["min", "mins", "minute", "minutes"]:
        return "minutes"
    if u in ["h", "hr", "hrs", "hour", "hours"]:
        return "hours"
    if u in ["yr", "yrs", "year", "years"]:
        return "years"
    return u

def evaluate_numeric_or_logical(req: dict, vendor_found: bool, vendor_val_str: Optional[str]) -> tuple:
    """
    Perform deterministic Python comparison between requirement and vendor values.
    Returns (status, deviation_str).
    """
    if not vendor_found or not vendor_val_str or vendor_val_str.lower() in ["missing", "null", "not specified"]:
        return ("NOT_VERIFIABLE", "Missing vendor evidence")

    req_val_str = str(req.get("required_value", ""))
    req_num = req.get("raw_numeric") or parse_numeric(req_val_str)
    vendor_num = parse_numeric(vendor_val_str)

    req_lower = req_val_str.lower()
    vendor_lower = vendor_val_str.lower()

    # Special handling for N+1 redundancy
    if "n+1" in req_lower:
        if "n+1" in vendor_lower:
            return ("COMPLIANT", None)
        else:
            return ("NON-COMPLIANT", "Vendor submission lacks N+1 redundancy")

    # Numeric comparison if numbers exist
    if req_num is not None and vendor_num is not None:
        unit = req.get("unit", "")
        norm_unit = normalize_unit(unit)
        unit_label = "%" if norm_unit == "%" else f" {norm_unit}" if norm_unit else ""

        # Default operator is >= for minimum specifications
        if vendor_num >= req_num:
            return ("COMPLIANT", None)
        else:
            diff = vendor_num - req_num
            diff_fmt = f"{diff:+.1f}".rstrip('0').rstrip('.')
            return ("NON-COMPLIANT", f"{diff_fmt}{unit_label}")

    # Fallback string comparison
    if req_lower in vendor_lower or vendor_lower in req_lower:
        return ("COMPLIANT", None)

    return ("WARNING", "Manual engineering review required")

def analyze_compliance(
    requirement_document_id: str,
    vendor_document_id: str,
    equipment: str = "UPS-04",
    discipline: str = "Electrical"
) -> dict:
    """
    Execute full specification compliance comparison between requirement PDF and vendor submittal PDF.
    """
    # 1. Validate inputs and document index status
    if not requirement_document_id or not vendor_document_id:
        raise ValueError("Both Requirement Document and Vendor Submission Document must be selected.")

    if requirement_document_id == vendor_document_id:
        raise ValueError("Requirement Document and Vendor Submission Document must be different documents.")

    req_doc = vector_store.get_document_by_id(requirement_document_id)
    if not req_doc or req_doc.get("status") != "Indexed":
        raise ValueError("Selected Requirement Document is unavailable or not indexed.")

    vendor_doc = vector_store.get_document_by_id(vendor_document_id)
    if not vendor_doc or vendor_doc.get("status") != "Indexed":
        raise ValueError("Selected Vendor Submission Document is unavailable or not indexed.")

    client = get_client()
    model_name = get_model_name()

    # 2. Comprehensive Requirement Extraction from requirement document chunks
    req_chunks = vector_store.get_chunks_by_document(requirement_document_id)
    if not req_chunks:
        raise ValueError("No indexed text chunks found for requirement document.")

    extracted_reqs = []
    seen_parameters = set()

    for chunk in req_chunks:
        prompt = (
            f"REQUIREMENT DOCUMENT EXCERPT (Page {chunk['page_number']}):\n"
            f"{chunk['text']}\n\n"
            f"Extract all technical parameters and requirements from this excerpt."
        )

        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=REQ_EXTRACTION_INSTRUCTION,
                    response_mime_type="application/json"
                ),
            )
            if res and res.text:
                parsed = json.loads(res.text)
                items = parsed.get("requirements", []) if isinstance(parsed, dict) else parsed if isinstance(parsed, list) else []
                for item in items:
                    param = item.get("parameter")
                    if param and param.lower() not in seen_parameters:
                        seen_parameters.add(param.lower())
                        item["page_number"] = chunk["page_number"]
                        item["section"] = chunk.get("section", "General")
                        item["document_name"] = req_doc["original_filename"]
                        extracted_reqs.append(item)
        except Exception:
            continue

    if not extracted_reqs:
        raise ValueError("Could not extract technical requirements from requirement document.")

    # 3. For each requirement, perform document-scoped semantic retrieval on VENDOR document
    checks = []
    check_counter = 1

    for req in extracted_reqs:
        param_name = req["parameter"]
        
        # Document-scoped retrieval strictly on vendor_document_id
        vendor_chunks = retrieve_context(
            question=f"What is the specified or submitted value for {param_name}?",
            top_k=3,
            document_id=vendor_document_id
        )

        relevant_vendor_chunks = [c for c in vendor_chunks if c.get("score", 0) >= 0.20]
        
        vendor_found = False
        vendor_val_str = None
        vendor_num = None
        vendor_page = None
        vendor_section = None

        if relevant_vendor_chunks:
            top_v_chunk = relevant_vendor_chunks[0]
            v_prompt = (
                f"VENDOR SUBMITTAL EXCERPT (Page {top_v_chunk['page_number']}):\n"
                f"{top_v_chunk['text']}\n\n"
                f"Extract submitted value for parameter: '{param_name}'."
            )
            try:
                v_res = client.models.generate_content(
                    model=model_name,
                    contents=v_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=VENDOR_EXTRACTION_INSTRUCTION.format(parameter=param_name),
                        response_mime_type="application/json"
                    ),
                )
                if v_res and v_res.text:
                    v_parsed = json.loads(v_res.text)
                    if v_parsed.get("found"):
                        vendor_found = True
                        vendor_val_str = v_parsed.get("vendor_value")
                        vendor_num = v_parsed.get("raw_numeric")
                        vendor_page = top_v_chunk["page_number"]
                        vendor_section = top_v_chunk.get("section", "General")
            except Exception:
                pass

        # 4. Deterministic Python Comparison
        status, deviation = evaluate_numeric_or_logical(req, vendor_found, vendor_val_str)

        # 5. Engineering Analysis & Severity via Gemini
        analysis_text = f"Evaluated parameter '{param_name}': Requirement {req['required_value']} versus Vendor submission {vendor_val_str or 'Not specified'}."
        impact_list = ["Specification compliance"]
        action_text = "Review specification."
        severity = "HIGH" if status == "NON-COMPLIANT" else "LOW" if status == "COMPLIANT" else "MEDIUM"

        eval_prompt = (
            f"Parameter: {param_name}\n"
            f"Requirement: {req['required_value']}\n"
            f"Vendor Value: {vendor_val_str or 'Not Specified'}\n"
            f"Status: {status}\n"
            f"Deviation: {deviation or 'None'}\n\n"
            f"Provide engineering analysis, potential impact list, recommended action, and severity."
        )

        try:
            a_res = client.models.generate_content(
                model=model_name,
                contents=eval_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=ENGINEERING_ANALYSIS_INSTRUCTION,
                    response_mime_type="application/json"
                ),
            )
            if a_res and a_res.text:
                a_parsed = json.loads(a_res.text)
                analysis_text = a_parsed.get("analysis", analysis_text)
                impact_list = a_parsed.get("impact", impact_list)
                action_text = a_parsed.get("action", action_text)
                severity = a_parsed.get("severity", severity)
        except Exception:
            pass

        # Build genuine sources
        req_source = {
            "document": req_doc["original_filename"],
            "page": req["page_number"],
            "section": req.get("section", "General")
        }

        # Do NOT generate fake vendor source if vendor evidence is missing
        vendor_source = None
        if vendor_found and vendor_page is not None:
            vendor_source = {
                "document": vendor_doc["original_filename"],
                "page": vendor_page,
                "section": vendor_section or "General"
            }

        sources_list = [f"Requirement: {req_source['document']} (Page {req_source['page']})"]
        if vendor_source:
            sources_list.append(f"Vendor: {vendor_source['document']} (Page {vendor_source['page']})")

        check_id = f"CC-{100 + check_counter}"
        check_counter += 1

        checks.append({
            "id": check_id,
            "equipment": equipment,
            "parameter": param_name,
            "requirement": req["required_value"],
            "vendorValue": vendor_val_str if (vendor_found and vendor_val_str) else "Not Specified",
            "status": status,
            "severity": severity,
            "deviation": deviation,
            "analysis": analysis_text,
            "impact": impact_list,
            "action": action_text,
            "sources": sources_list,
            "requirementSource": req_source,
            "vendorSource": vendor_source
        })

    # Summary Statistics
    total_checks = len(checks)
    compliant_cnt = sum(1 for c in checks if c["status"] == "COMPLIANT")
    warnings_cnt = sum(1 for c in checks if c["status"] == "WARNING")
    non_compliant_cnt = sum(1 for c in checks if c["status"] == "NON-COMPLIANT")
    not_verifiable_cnt = sum(1 for c in checks if c["status"] == "NOT_VERIFIABLE")
    high_severity_cnt = sum(1 for c in checks if c["severity"] in ["HIGH", "CRITICAL"])

    stats = {
        "total": total_checks,
        "compliant": compliant_cnt,
        "warnings": warnings_cnt,
        "nonCompliant": non_compliant_cnt,
        "notVerifiable": not_verifiable_cnt,
        "highSeverity": high_severity_cnt
    }

    analysis_id = f"anl_{uuid.uuid4().hex[:12]}"
    vector_store.save_compliance_analysis(
        analysis_id=analysis_id,
        req_doc_id=requirement_document_id,
        vendor_doc_id=vendor_document_id,
        equipment=equipment,
        discipline=discipline,
        checks=checks,
        stats=stats
    )

    return {
        "analysis_id": analysis_id,
        "checks": checks,
        "stats": stats
    }
