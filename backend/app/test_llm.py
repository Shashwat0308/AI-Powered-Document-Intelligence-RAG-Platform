from backend.app.services.llm_service import LLMService


llm = LLMService()

context = """
Machine learning is a branch of artificial intelligence.
It allows computers to learn patterns from data and make predictions
without being explicitly programmed for every task.
"""

question = "What is machine learning?"

answer = llm.generate_answer(
    question,
    context
)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(answer)