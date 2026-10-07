import faiss
import numpy as np
import os
import pickle


class VectorStore:

    def __init__(self, dimension: int = 384):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.documents = []

    def add_embeddings(
        self,
        embeddings,
        documents
    ):

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        faiss.normalize_L2(
            embeddings
        )

        self.index.add(
            embeddings
        )

        self.documents.extend(
            documents
        )

    def search(
        self,
        query_embedding,
        top_k: int = 5,
        score_threshold: float = 0.30,
        document_filter: str | None = None,
        retrieve_all: bool = False,
        user_id: int | None = None
    ):

        print("### VECTOR STORE SEARCH ###")
        print("Document filter:", document_filter)
        print("User ID:", user_id)
        print("Retrieve all:", retrieve_all)
        print("Score threshold:", score_threshold)
        print("Total vectors:", self.index.ntotal)

        if self.index.ntotal == 0:

            print("VECTOR STORE IS EMPTY")

            return []

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        ).reshape(1, -1)

        faiss.normalize_L2(
            query_embedding
        )

        scores, indices = self.index.search(
            query_embedding,
            self.index.ntotal
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:
                continue

            score = float(score)

            document = self.documents[index]

            document_name = document.get(
                "document_name",
                ""
            )

            source = document.get(
                "source",
                ""
            )

            print(
                "Checking:",
                document_name,
                "| Score:",
                score,
                "| User ID:",
                document.get("user_id")
            )

            # ---------------------------------
            # USER FILTER
            # ---------------------------------

            if user_id is not None:

                document_user_id = document.get(
                    "user_id"
                )

                if document_user_id != user_id:

                    print(
                        "Rejected because document belongs to another user"
                    )

                    continue

            # ---------------------------------
            # DOCUMENT FILTER
            # ---------------------------------

            if document_filter:

                if (
                    document_filter.lower()
                    not in document_name.lower()
                    and
                    document_filter.lower()
                    not in source.lower()
                ):
                    continue

            # ---------------------------------
            # DOCUMENT LEVEL RETRIEVAL
            # ---------------------------------

            if retrieve_all:

                results.append({
                    "score": score,
                    "document": document
                })

                continue

            # ---------------------------------
            # NORMAL QUESTION RETRIEVAL
            # ---------------------------------

            if score < score_threshold:

                print(
                    "Rejected because score is below threshold:",
                    score
                )

                continue

            results.append({
                "score": score,
                "document": document
            })

            if len(results) >= top_k:
                break

        # ---------------------------------
        # DOCUMENT LEVEL SORTING
        # ---------------------------------

        if retrieve_all:

            results.sort(
                key=lambda x: x["score"],
                reverse=True
            )

        print(
            "RESULTS FOUND:",
            len(results)
        )

        return results

    def save(
        self,
        directory: str
    ):

        os.makedirs(
            directory,
            exist_ok=True
        )

        index_path = os.path.join(
            directory,
            "faiss.index"
        )

        metadata_path = os.path.join(
            directory,
            "metadata.pkl"
        )

        faiss.write_index(
            self.index,
            index_path
        )

        with open(
            metadata_path,
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file
            )

    def load(
        self,
        directory: str
    ):

        index_path = os.path.join(
            directory,
            "faiss.index"
        )

        metadata_path = os.path.join(
            directory,
            "metadata.pkl"
        )

        if not os.path.exists(
            index_path
        ):
            return False

        if not os.path.exists(
            metadata_path
        ):
            return False

        self.index = faiss.read_index(
            index_path
        )

        with open(
            metadata_path,
            "rb"
        ) as file:

            self.documents = pickle.load(
                file
            )

        return True