def chunk_text(text: str, chunk_size=700, overlap=100):
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(
            (
                chunk.strip(),
                start,
                min(end, text_length)
            )
        )

        start += chunk_size - overlap

    return chunks
