from fastapi import APIRouter, UploadFile, File
from uuid import uuid4
import shutil
from app.services.pdf_reader import extract_pages

router = APIRouter()

PDF_DIR = "data/pdfs"

@router.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    documents = []

    for file in files:
        doc_id = str(uuid4())
        file_path = f"{PDF_DIR}/{doc_id}.pdf"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages, has_text = extract_pages(file_path)

        documents.append({
            "document_id": doc_id,
            "filename": file.filename,
            "pages": len(pages),
            "status": "TEXT_EXTRACTED" if has_text else "NO_TEXT_LAYER",
            "content":pages
        })

    return {"documents": documents}