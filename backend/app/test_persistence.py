from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore


documents = [
    {
        "text": "Machine learning is a branch of artificial intelligence.",
        "page_number": 1,
        "source": "test.pdf"
    },
    {
        "text": "Deep learning uses neural networks with multiple layers.",
        "page_number": 2,
        "source": "test.pdf"
    },
    {
        "text": "Natural language processing allows computers to understand human language.",
        "page_number": 3,
        "source": "test.pdf"
    }
]


embedding_service = EmbeddingService()

texts = [
    document["text"]
    for document in documents
]

embeddings = embedding_service.generate_embeddings(
    texts
)


store = VectorStore()

store.add_embeddings(
    embeddings,
    documents
)


store.save(
    "data/vector_store"
)

print("Vector store saved successfully.")


new_store = VectorStore()

loaded = new_store.load(
    "data/vector_store"
)

print("Vector store loaded:", loaded)

print("Number of vectors:", new_store.index.ntotal)


query = "What is machine learning?"

query_embedding = embedding_service.generate_embeddings(
    [query]
)

results = new_store.search(
    query_embedding[0],
    top_k=2
)


print("\nSearch results:")

for result in results:

    print("\nScore:", round(result["score"], 4))
    print("Page:", result["document"]["page_number"])
    print("Text:", result["document"]["text"])