from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore


documents = [
    "Machine learning is a branch of artificial intelligence.",
    "Deep learning uses neural networks with multiple layers.",
    "Python is widely used for machine learning and data science.",
    "The weather forecast predicts heavy rainfall tomorrow.",
    "Natural language processing allows computers to understand human language."
]


embedding_service = EmbeddingService()

embeddings = embedding_service.generate_embeddings(documents)

vector_store = VectorStore()

vector_store.add_embeddings(
    embeddings,
    documents
)


query = "What is artificial intelligence and machine learning?"

query_embedding = embedding_service.generate_embeddings([query])

results = vector_store.search(
    query_embedding[0],
    top_k=3
)


print("\nQuery:")
print(query)

print("\nMost relevant results:")

for result in results:
    print(f"\nScore: {result['score']:.4f}")
    print(result["document"])