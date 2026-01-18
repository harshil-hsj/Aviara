import json
from pathlib import Path as FilePath
import requests

BASE_DIR = FilePath(__file__).resolve().parent.parent.parent
PDF_PATH = BASE_DIR / "test_pdf" / "oneNDA-example.pdf"

url = "http://localhost:8000/ingest"

files = [
    ("files", open(PDF_PATH, "rb"))
]

response = requests.post(url, files=files)

if response.status_code == 200:
    res = json.loads(response.content)
    print(f"Successfully ingested the pdf from script. Saved with doc_id:{res["document_id"]}")
else:
    print("Failed to ingest the pdf ")
    

