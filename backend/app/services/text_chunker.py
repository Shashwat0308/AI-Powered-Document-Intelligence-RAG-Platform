import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def create_chunks(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    words = text.split()

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

