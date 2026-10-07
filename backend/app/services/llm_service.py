
import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.8-flash"

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        if not context.strip():

            return (
                "I could not find this information "
                "in the provided documents."
            )

        prompt = f"""
You are a strict document question-answering assistant.

Your job is to answer the user's question using ONLY
the information contained in DOCUMENT CONTEXT.

IMPORTANT RULES:

1. Use only information explicitly present in the
   provided document context.

2. Do not use your own general knowledge.

3. Do not invent, assume, or infer facts that are not
   supported by the document context.

4. If the answer is not present in the context, respond
   exactly with:

"I could not find this information in the provided documents."

5. If the question asks for a summary or overview,
   summarize only the information present in the
   provided document context.

6. If multiple document pages are provided, combine
   relevant information from those pages.

7. Keep the answer clear and directly related to the
   user's question.

DOCUMENT CONTEXT:
----------------
{context}
----------------

USER QUESTION:
{question}

ANSWER:
"""

        max_retries = 3

        for attempt in range(max_retries):

            try:

                response = self.client.interactions.create(
                    model=self.model,
                    input=prompt
                )

                answer = response.output_text

                if not answer or not answer.strip():

                    return (
                        "I could not find this information "
                        "in the provided documents."
                    )

                return answer.strip()

            except Exception as error:

                error_message = str(error).lower()

                print(
                    f"Gemini request failed "
                    f"(attempt {attempt + 1}/{max_retries}):"
                )

                print(error)

                is_temporary_error = (
                    "503" in error_message
                    or
                    "high demand" in error_message
                    or
                    "service_unavailable" in error_message
                    or
                    "temporarily unavailable" in error_message
                )

                if not is_temporary_error:

                    return (
                        "The AI answer service encountered "
                        "an error. Please try again."
                    )

                if attempt < max_retries - 1:

                    wait_time = 2 ** attempt

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

        return (
            "The AI answer service is temporarily busy. "
            "Please try your question again in a moment."
        )

