from pydantic import BaseModel

class ExtractRequest(BaseModel):
    document_id: str

class AskRequest(BaseModel):
    question: str