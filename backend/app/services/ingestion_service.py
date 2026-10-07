import os
import uuid

from backend.app.services.pdf_processor import extract_text_from_pdf
from backend.app.services.text_chunker import clean_text, create_chunks
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.vector_store import VectorStore


class IngestionService:

    def __init__(self):

        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def get_document_names(self):

        documents = set()

        for document in self.vector_store.documents:

            document_name = document.get(
                "document_name"
            )

            if document_name:
                documents.add(document_name)

        return list(documents)

    def process_pdf(
        self,
        file_path: str,
        user_id: int | None = None
    ):

        pages = extract_text_from_pdf(
            file_path
        )

        all_chunks = []

        for page in pages:

            cleaned_text = clean_text(
                page["text"]
            )

            chunks = create_chunks(
                cleaned_text
            )

            for chunk in chunks:

                all_chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "text": chunk,
                    "page_number": page["page_number"],
                    "document_name": os.path.basename(
                        file_path
                    ),
                    "source": file_path,

                    # ---------------------------------
                    # USER OWNERSHIP
                    # ---------------------------------

                    "user_id": user_id
                })

        if not all_chunks:

            return {
                "pages": len(pages),
                "chunks": 0
            }

        texts = [
            chunk["text"]
            for chunk in all_chunks
        ]

        embeddings = (
            self.embedding_service.generate_embeddings(
                texts
            )
        )

        self.vector_store.add_embeddings(
            embeddings,
            all_chunks
        )

        return {
            "pages": len(pages),
            "chunks": len(all_chunks)
        }

    def save(self, directory: str):

        self.vector_store.save(
            directory
        )

    def load(self, directory: str):

        return self.vector_store.load(
            directory
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_filter: str | None = None,
        retrieve_all: bool = False,
        user_id: int | None = None
    ):

        query_embedding = (
            self.embedding_service.generate_embeddings(
                [query]
            )
        )

        return self.vector_store.search(
            query_embedding[0],
            top_k,
            document_filter=document_filter,
            retrieve_all=retrieve_all,
            user_id=user_id
        )