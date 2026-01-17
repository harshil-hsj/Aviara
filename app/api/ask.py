from fastapi import APIRouter, HTTPException
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

@router.post("/ask")
async def ask(req: AskRequest):

    query_embedding = embed_text(req.question)

    if not query_embedding:
        raise HTTPException(status_code=500, detail="Failed to embed question")

    #Score chunks (STREAMING, memory safe)
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

    #Top 3 chunks
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_chunks = scored_chunks[:3]
    
    print(top_chunks)

    context = ""
    citations = []

    for score, chunk in top_chunks:
        context += f"\n---\n{chunk['text']}\n"
        citations.append({
            "document_id": chunk["document_id"],
            "page_number": chunk["page_number"],
            "char_start": chunk["char_start"],
            "char_end": chunk["char_end"]
        })

    prompt = f"""
You are a question answering assistant.

Answer the question STRICTLY using the context below.
If the answer is not present, say: "Answer not found in documents."

Context:
{context}

Question:
{req.question}
"""
    try:
        response = model.generate_content(prompt)
    except Exception as e:
        
        raise HTTPException(
                    status_code=500,
                    detail={
                    "message": "Failed retrive response from LLM",
                }
                )
    answer = parse_gemini_json(response)

    return {
        "answer": answer,
        "citations": citations
    }

def parse_gemini_json(response) -> str:
    try:
        text = response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError) as e:
        raise ValueError(f"Invalid Gemini response format: {e}")

    text = text.strip()
    print("text "+text)

    return text