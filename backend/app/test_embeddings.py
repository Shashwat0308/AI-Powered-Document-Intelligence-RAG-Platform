from backend.app.services.embedding_service import EmbeddingService


texts = [
    "Machine learning is a branch of artificial intelligence.",
    "Artificial intelligence allows computers to learn from data.",
    "The weather is very pleasant today."
]

embedding_service = EmbeddingService()

embeddings = embedding_service.generate_embeddings(texts)

print("Number of texts:", len(texts))
print("Embedding shape:", embeddings.shape)
print("First embedding:")
print(embeddings[0])