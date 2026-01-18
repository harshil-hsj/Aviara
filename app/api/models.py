from typing import Any, Dict, List
from pydantic import BaseModel

class ExtractRequest(BaseModel):
    document_id: str

class AskRequest(BaseModel):
    question: str
    
class DocumentModel(BaseModel):
    document_id: str
    filename: str
    pages: int
    status: str
    metadata: List[Dict[str, Any]]

class ChunkModel(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    text: str
    char_start: int
    char_end: int
    embedding:List[float]
    metadata: List[Dict[str, Any]] 