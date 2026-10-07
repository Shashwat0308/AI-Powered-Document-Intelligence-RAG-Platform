from backend.app.services.pdf_processor import extract_text_from_pdf


pdf_path = "data/documents/research.pdf"

pages = extract_text_from_pdf(pdf_path)

for page in pages:
    print(f"\n--- Page {page['page_number']} ---")
    print(page["text"][:500])