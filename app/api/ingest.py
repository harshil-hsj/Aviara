from fastapi import APIRouter, UploadFile, File
from uuid import uuid4
import shutil
from app.db.db import get_collection
from app.services.pdf_reader import extract_pages
from app.services.metadata_extractor import extract_metadata

router = APIRouter()

PDF_DIR = "data/pdfs"

collection = get_collection("Document_Metadata")

@router.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    documents = []

    for file in files:
        doc_id = str(uuid4())
        file_path = f"{PDF_DIR}/{doc_id}.pdf"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages, has_text = extract_pages(file_path)
        
        all_metadata = []
        page_number = 0 
        for page in pages:
            page_text = page['text']
            page_metadata = extract_metadata(page_text,page_number)
            page_number=page_number+1

            all_metadata.append(page_metadata)
        collection.insert_one({
            "document_id": doc_id,
            "filename": file.filename,
            "pages": len(pages),
            "status": "TEXT_EXTRACTED" if has_text else "NO_TEXT_LAYER",
            "content":pages,
            "metadata":all_metadata
        })

    documents.append({
            "document_id": doc_id,
            "filename": file.filename,
            "pages": len(pages),
            "status": "TEXT_EXTRACTED" if has_text else "NO_TEXT_LAYER",
            "content":pages,
            "metadata":all_metadata
        })
        

    return documents