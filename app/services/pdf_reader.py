import pdfplumber
from typing import List, Dict

def extract_pages(file_path: str):
    pages = []
    has_text = False

    with pdfplumber.open(file_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if text.strip():
                has_text = True

            pages.append({
                "page_number": idx + 1,
                "text": text.strip()
            })

    return pages, has_text
