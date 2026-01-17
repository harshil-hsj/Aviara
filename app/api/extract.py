from fastapi import APIRouter, HTTPException
from app.db.db import collection
from app.api.models import ExtractRequest  

router = APIRouter()

@router.post("/extract", summary = "Fetches metadata for a document")
async def extract_metadata(req: ExtractRequest):

    doc = collection.find_one(
        {"document_id": req.document_id},
        {"_id": 0, "metadata": 1}
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "metadata": doc["metadata"]
    }
