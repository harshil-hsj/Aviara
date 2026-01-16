from fastapi import APIRouter, HTTPException, UploadFile, File, logger
from uuid import uuid4
import shutil
from app.services.chunk_text import chunk_text
from app.services.embed_text import embed_text
from app.services.pdf_reader import extract_pages
from app.services.metadata_extractor import extract_metadata
from app.db.db import collection, chunks_collection

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
        
        all_metadata = []
        page_number = 0 
        for page in pages:
            page_text = page['text']
            page_metadata = extract_metadata(page_text,page_number)
            page_number=page_number+1

            chunks = chunk_text(page_text)

            for chunk_text_value, start, end in chunks:
                embedding = embed_text(chunk_text_value)
                try:
                    chunks_collection.insert_one({
                        "chunk_id": str(uuid4()),
                        "document_id": doc_id,
                        "page_number": page_number,
                        "text": chunk_text_value,
                        "char_start": start,
                        "char_end": end,
                        "embedding": embedding,
                        "metadata": page_metadata
                    })
                except Exception as e:
                    logger.exception(f"Failed to insert Chunk with document_id:{doc_id}")

                    raise HTTPException(
                        status_code=500,
                        detail={
                            "message": "Failed to store text document",
                            "document_id": doc_id
                        }
                    )

            all_metadata.append(page_metadata)
        try:    
            collection.insert_one({
                "document_id": doc_id,
                "filename": file.filename,
                "num_of_pages": len(pages),
                "status": "TEXT_EXTRACTED" if has_text else "NO_TEXT_LAYER",
                "metadata":all_metadata
            })
        except Exception as e:
            logger.exception(f"Failed to insert document with file Name:{file.filename}")

            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Failed to store document metadata",
                    "document_id": doc_id
                }
            )

    documents.append({
            "document_id": doc_id,
            "filename": file.filename,
            "pages": len(pages),
            "status": "TEXT_EXTRACTED" if has_text else "NO_TEXT_LAYER",
            "metadata":all_metadata
        })
    
    return documents