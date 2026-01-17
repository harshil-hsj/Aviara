from fastapi import APIRouter, HTTPException
from app.db.db import chunks_collection
from app.services.llm import model
import json

router = APIRouter()

@router.post("/audit", summary="Detects and outlines risky clauses with text proofs")
def audit(document_id: str):
    chunks = chunks_collection.find({"document_id": document_id})

    findings = []
    detected_risks =[]
    
    for chunk in chunks:
        
        detected_risks = detect_risks_rule_based(chunk["text"])
        
        
        for risk in detected_risks:
            
            prompt = f"""
You are a contract risk validation assistant.

You are given:
1. A specific RISK TYPE
2. A contract text excerpt

Your task:
- Determine whether the given risk is EXPLICITLY present in the text
- Do NOT infer or assume
- Use ONLY the provided text
- If the risk is not clearly present, set confirmed=false
- If confirmed=true, explain why and assign severity

Severity definitions:
- LOW: Minor risk, standard wording
- MEDIUM: Noticeable risk but negotiable
- HIGH: Significant legal or financial exposure
- CRITICAL: Severe or unlimited exposure

Return STRICT JSON ONLY.
Do NOT include explanations, markdown, or extra text.

Output format:
{{
  "confirmed": boolean,
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "description": string
}}

RISK TYPE:
{risk}

CONTRACT TEXT:
{chunk["text"][:1500]}
"""
            try:
                result = parse_gemini_json(model.generate_content(prompt))
            except Exception as e:
                print(f"Gemini API error: {e}")
                raise HTTPException(
                            status_code=500,
                            detail={
                            "message": "Failed retrive response from LLM",
                        }
                        )
            if result and result["confirmed"]:
                findings.append({
                    "risk_type": risk,
                    "severity": result["severity"],
                    "description": result["description"],
                    "evidence": {
                        "page": chunk["page_number"],
                        "text": chunk["text"]
                    }
                })

    return {
        "document_id": document_id,
        "findings": findings
    }


import re
from typing import List

def detect_risks_rule_based(text: str) -> List[str]:
    """
    Detect potential legal risks using rule-based heuristics.
    Returns a list of risk_type strings.
    """
    risks = []
    t = text.lower()

    if "automatically renew" in t or "auto-renew" in t:
        notice_match = re.search(r"(\d+)\s+days", t)
        if notice_match:
            days = int(notice_match.group(1))
            if days < 30:
                risks.append("AUTO_RENEWAL_SHORT_NOTICE")

    if re.search(r"unlimited liability|liability shall be unlimited", t):
        risks.append("UNLIMITED_LIABILITY")

    if "liability" in t and not re.search(r"liability cap|limit liability|capped at", t):
        risks.append("NO_LIABILITY_CAP")

    if "indemnify" in t:
        if re.search(r"any and all|all claims|whatsoever", t):
            risks.append("BROAD_INDEMNITY")

    if "terminate" in t:
        if re.search(r"at any time.*without cause", t):
            if not re.search(r"both parties|either party", t):
                risks.append("ONE_SIDED_TERMINATION")

    return list(set(risks))

def parse_gemini_json(response):

    fallback = {
        "confirmed": False,
        "severity": "LOW",
        "description": ""
    }

    if not response:
        return fallback

    try:
        # Gemini SDK response → text
        text = response.text if hasattr(response, "text") else str(response)

        if not text:
            return fallback

        # Remove markdown code fences if present
        text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

        # Extract first JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return fallback

        json_str = match.group(0)
        data = json.loads(json_str)

        confirmed = bool(data.get("confirmed", False))
        severity = data.get("severity", "LOW")
        description = data.get("description", "")

        allowed_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if severity not in allowed_severities:
            severity = "LOW"

        return {
            "confirmed": confirmed,
            "severity": severity,
            "description": description
        }

    except Exception as e:
        print("Gemini JSON parse error:", e)
        return fallback