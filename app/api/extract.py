from fastapi import APIRouter, HTTPException
from app.db.db import get_collection
from app.api.models import ExtractRequest  

router = APIRouter()
collection = get_collection("Document_Metadata")
@router.post("/extract")
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
