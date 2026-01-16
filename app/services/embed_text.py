from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list:
    """
    Generate embedding locally using SentenceTransformers.
    Returns a list of floats (vector).
    """

    if not text.strip():
        return []

    embedding = model.encode(text, normalize_embeddings=True)

    return embedding.tolist()
