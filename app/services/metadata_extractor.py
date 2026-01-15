import re
import json
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# client = genai.Client(api_key=GEMINI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

def extract_metadata(text: str, page_number:int) -> dict:
    """
    Extract structured metadata from a page of text.
    Step 1: Use regex/rule-based extraction for all fields.
    Step 2: Send all fields to Gemini API for normalization/completion.
    """
    # ------------------------
    # 1. Rule-based extraction
    # ------------------------
    metadata = {
        "page_number":page_number,
        "parties": [],
        "effective_date": None,
        "term": None,
        "governing_law": None,
        "payment_terms": None,
        "termination": None,
        "auto_renewal": None,
        "confidentiality": None,
        "indemnity": None,
        "liability_cap": {"amount": None, "currency": None},
        "signatories": []
    }
    try:
        parties = re.findall(r"Party\s[A-Z][\w\s]*", text)
        metadata["parties"] = list({*metadata["parties"], *parties})

        date_match = re.search(r"(?:Effective Date|Effective as of)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})", text)
        if date_match:
            metadata["effective_date"] = date_match.group(1)
            
        term_match = re.search(r"for a period of ([\w\s]+)", text, re.IGNORECASE)
        if term_match:
            metadata["term"] = term_match.group(1)

        law_match = re.search(r"governing law[:\s]*([\w\s]+)", text, re.IGNORECASE)
        if law_match:
            metadata["governing_law"] = law_match.group(1)

        payment_match = re.search(r"(payment terms[:\s]*[\w\s,]+)", text, re.IGNORECASE)
        if payment_match:
            metadata["payment_terms"] = payment_match.group(1)

        termi_match = re.search(r"(termination[:\s]*[\w\s,]+)", text, re.IGNORECASE)
        if termi_match:
            metadata["termination"] = termi_match.group(1)

        auto_match = re.search(r"auto[-\s]?renewal[:\s]*(true|false|yes|no)", text, re.IGNORECASE)
        if auto_match:
            metadata["auto_renewal"] = auto_match.group(1).lower() in ["true", "yes"]

        metadata["confidentiality"] = bool(re.search(r"confidential", text, re.IGNORECASE))

        indemnity_match = re.search(r"(indemnity[:\s]*[\w\s,]+)", text, re.IGNORECASE)
        if indemnity_match:
            metadata["indemnity"] = indemnity_match.group(1)

        cap_match = re.search(r"liability (?:cap|limit)[:\s]*([\$€£]?)([\d,]+)", text, re.IGNORECASE)
        if cap_match:
            currency = cap_match.group(1) or "USD"
            amount = int(cap_match.group(2).replace(",", ""))
            metadata["liability_cap"] = {"amount": amount, "currency": currency}

        signatory_matches = re.findall(r"([A-Z][a-z]+\s[A-Z][a-z]+),\s*(\w+)", text)
        if signatory_matches:
            metadata["signatories"] = [{"name": name, "title": title} for name, title in signatory_matches]
    except Exception as e:
        print("failed in regex validation")
        
    # ------------------------
    # 2. Gemini API fallback / normalization for all fields
    # ------------------------
    print(metadata)
    metadata = call_gemini_for_metadata(text, metadata)

    return metadata


# ------------------------
# Gemini API call
# ------------------------
def call_gemini_for_metadata(text: str, metadata: dict) -> dict:

    prompt = f"""
You are a contract metadata extraction assistant.

You will be given:
1. Contract text
2. An existing JSON object with partially extracted metadata

Your task:
- Preserve all values already present in the JSON.
- Only add or update fields if you find clear, explicit evidence in the contract text.
- Do NOT guess or infer.
- If a field is not mentioned in the text, leave it as null or an empty list.
- Normalize wording but do not change meaning.

Return STRICT JSON ONLY.
Do NOT include explanations, markdown, or extra text.

Fields to extract or normalize:
- parties: string[]
- effective_date: string | null
- term: string | null
- governing_law: string | null
- payment_terms: string | null
- termination: string | null
- auto_renewal: string | null
- confidentiality: boolean | null
- indemnity: string | null
- liability_cap: 
- signatories: 


{json.dumps(metadata, indent=2)}

Contract Text:
{text[:2000]}
"""
    try:
        response = model.generate_content(prompt)
        
        raw = parse_gemini_json(response)
        print(raw)
        normalized_metadata = raw

        return normalized_metadata
    except Exception as e:
        print(f"Gemini API error: {e}")
        return metadata

def parse_gemini_json(response) -> dict:
    try:
        text = response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError) as e:
        raise ValueError(f"Invalid Gemini response format: {e}")

    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini JSON:\n{text}") from e