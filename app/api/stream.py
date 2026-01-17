from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.cosine_similarity import cosine_similarity
from app.services.embed_text import embed_text
from app.db.db import chunks_collection
from app.api.models import AskRequest
from app.services.llm import model
import os
from dotenv import load_dotenv
load_dotenv()


SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD"))
router = APIRouter()

@router.post("/ask/stream", summary="Returns streamed response for Asked question")
async def ask(req: AskRequest):

    query_embedding = embed_text(req.question)

    if not query_embedding:
        raise HTTPException(status_code=500, detail="Failed to embed question")

    scored_chunks = []

    for chunk in chunks_collection.find({}, {
        "embedding": 1,
        "text": 1,
        "document_id": 1,
        "page_number": 1,
        "char_start": 1,
        "char_end": 1
    }):
        score = cosine_similarity(query_embedding, chunk["embedding"])

        if score >= SIMILARITY_THRESHOLD:
            scored_chunks.append((score, chunk))

    if not scored_chunks:
        raise HTTPException(status_code=404, detail="No chunks found")

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = scored_chunks[:3]

    
    def event_generator():
        context = ""
        for _, chunk in top_chunks:
            context += f"\n---\n{chunk['text']}\n"

        prompt = f"""
You are a question answering assistant.

Answer the question STRICTLY using the context below.
If the answer is not present, say: "Answer not found in documents."
{context}

Question:
{req.question}
"""
        response = model.generate_content(prompt, stream=True)
        for part in response:
            if part.text:
                yield f"data: {part.text}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
