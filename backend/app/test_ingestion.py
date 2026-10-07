from backend.app.services.ingestion_service import IngestionService


pdf_path = "data/documents/research.pdf"

ingestion_service = IngestionService()

stats = ingestion_service.process_pdf(pdf_path)

print("\nDocument processed successfully!")
print("Pages:", stats["pages"])
print("Chunks:", stats["chunks"])


query = "What are the main findings of this document?"

results = ingestion_service.search(
    query,
    top_k=3
)

print("\nQuery:")
print(query)

print("\nRetrieved information:")

for result in results:
    print("\n-------------------------")
    print("Score:", round(result["score"], 4))
    print("Page:", result["document"]["page_number"])
    print("Source:", result["document"]["source"])
    print("Text:", result["document"]["text"])