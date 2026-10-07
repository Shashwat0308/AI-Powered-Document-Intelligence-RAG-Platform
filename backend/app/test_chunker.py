from backend.app.services.pdf_processor import extract_text_from_pdf
from backend.app.services.text_chunker import clean_text, create_chunks


pdf_path = "data/documents/research.pdf"

pages = extract_text_from_pdf(pdf_path)

full_text = ""

for page in pages:
    full_text += page["text"] + "\n"

cleaned_text = clean_text(full_text)

chunks = create_chunks(cleaned_text)

print(f"Total pages: {len(pages)}")
print(f"Total chunks: {len(chunks)}")
for i, chunk in enumerate(chunks[:3], start=1):
    print(f"\n--- Chunk {i} ---")
    print(chunk)