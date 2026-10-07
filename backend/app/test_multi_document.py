from backend.app.services.ingestion_service import IngestionService
from backend.app.services.rag_service import RAGService


DOCUMENTS_DIR = "data/documents"


ingestion = IngestionService()


for filename in ["research.pdf", "research2.pdf"]:

    file_path = f"{DOCUMENTS_DIR}/{filename}"

    print()
    print(f"Processing: {filename}")

    result = ingestion.process_pdf(file_path)

    print(
        f"Pages: {result['pages']} | "
        f"Chunks: {result['chunks']}"
    )


print()
print("All documents indexed successfully.")

print()
print(
    "Vectors in ingestion store:",
    ingestion.vector_store.index.ntotal
)


rag = RAGService()

# IMPORTANT:
# Use the already indexed ingestion service
rag.ingestion_service = ingestion


while True:

    question = input(
        "\nAsk a question across your documents: "
    )

    if question.lower() in ["exit", "quit"]:

        break

    document_filter = (
        rag.extract_document_filter(question)
    )

    print(
        "QUESTION:",
        question
    )

    print(
        "DOCUMENT FILTER:",
        document_filter
    )

    response = rag.ask(question)

    print()
    print("================ RESULTS ================")
    print()

    print("ANSWER:")
    print(response["answer"])

    print()
    print("SOURCES:")

    for source in response["sources"]:

        print(
            f"- {source['source']} "
            f"(Page {source['page_number']}, "
            f"Score: {source['score']:.4f})"
        )