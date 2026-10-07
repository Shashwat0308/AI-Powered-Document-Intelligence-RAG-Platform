from backend.app.services.ingestion_service import IngestionService
from backend.app.services.llm_service import LLMService


class RAGService:

    def __init__(self):

        self.ingestion_service = IngestionService()
        self.llm_service = LLMService()

    def extract_document_filter(
        self,
        question: str
    ):

        question_lower = question.lower()

        if "research2" in question_lower:
            return "research2.pdf"

        if "research" in question_lower:
            return "research.pdf"

        return None

    def is_document_level_question(
        self,
        question: str
    ):

        question_lower = question.lower()

        document_patterns = [

            "what is this paper about",
            "what is the paper about",
            "what is this research paper about",
            "what is the research paper about",

            "give me an overview",
            "give an overview",
            "overview of the paper",
            "overview of this paper",

            "summarize the paper",
            "summarise the paper",
            "summarize this paper",
            "summarise this paper",

            "summary of the paper",
            "summary of this paper",

            "explain the paper",
            "explain this paper",

            "tell me about the paper",
            "tell me about this paper",

            "what does this paper discuss",
            "what is discussed in the paper",
            "what is discussed in this paper",

            "what is discussed",
            "what does",
            "what is in",

            "summary",
            "overview",
            "explain the document",
            "tell me about"
        ]

        return any(
            pattern in question_lower
            for pattern in document_patterns
        )

    def ask(
        self,
        question: str,
        top_k: int = 5,
        user_id: int | None = None
    ):

        question = question.strip()

        if not question:

            return {
                "answer": "Please provide a question.",
                "sources": []
            }

        # ---------------------------------
        # DETECT DOCUMENT
        # ---------------------------------

        document_filter = (
            self.extract_document_filter(
                question
            )
        )

        # ---------------------------------
        # DETECT QUESTION TYPE
        # ---------------------------------

        document_level = (
            self.is_document_level_question(
                question
            )
        )

        print(
            "\nQUESTION:",
            question
        )

        print(
            "USER ID:",
            user_id
        )

        print(
            "DOCUMENT FILTER:",
            document_filter
        )

        print(
            "DOCUMENT LEVEL:",
            document_level
        )

        # ---------------------------------
        # SEARCH QUERY
        # ---------------------------------

        search_query = question

        if document_level:

            if document_filter:

                search_query = (
                    f"Give a complete overview "
                    f"of {document_filter}"
                )

            else:

                search_query = (
                    "Give a complete overview "
                    "of the research paper and "
                    "its main topics, objectives, "
                    "methods, findings and conclusions."
                )

        # ---------------------------------
        # RETRIEVE DOCUMENTS
        # ---------------------------------

        results = self.ingestion_service.search(

            query=search_query,

            top_k=top_k,

            document_filter=document_filter,

            retrieve_all=document_level,

            user_id=user_id
        )

        if not results:

            print(
                "NO RELEVANT DOCUMENTS FOUND"
            )

            return {
                "answer": (
                    "I could not find this information "
                    "in the provided documents."
                ),
                "sources": []
            }

        # ---------------------------------
        # BUILD CONTEXT
        # ---------------------------------

        context_parts = []

        sources = []

        seen_sources = set()

        for result in results:

            document = result["document"]

            context_parts.append(
                f"""
Source: {document['document_name']}
Page: {document['page_number']}

Content:
{document['text']}
"""
            )

            source_key = (
                document["document_name"],
                document["page_number"]
            )

            if source_key not in seen_sources:

                sources.append({
                    "source":
                        document["document_name"],

                    "page_number":
                        document["page_number"],

                    "score":
                        round(
                            float(result["score"]),
                            4
                        )
                })

                seen_sources.add(
                    source_key
                )

        context = "\n".join(
            context_parts
        )

        # ---------------------------------
        # GENERATE ANSWER
        # ---------------------------------

        answer = (
            self.llm_service.generate_answer(

                question=question,

                context=context
            )
        )

        # ---------------------------------
        # RETURN RESPONSE
        # ---------------------------------

        return {
            "answer": answer,
            "sources": sources
        }