from backend.app.services.rag_service import RAGService


pdf_path = "data/documents/research.pdf"

rag = RAGService()

stats = rag.ingestion_service.process_pdf(pdf_path)

print("\nDocument indexed successfully!")
print("Pages:", stats["pages"])
print("Chunks:", stats["chunks"])


question = input("\nAsk a question about the document: ")

result = rag.ask(question)

print("\n================ ANSWER ================\n")
print(result["answer"])

print("\n================ SOURCES ================\n")

for source in result["sources"]:
    print(
        f"Page: {source['page_number']} | "
        f"Score: {source['score']:.4f} | "
        f"Source: {source['source']}"
    )