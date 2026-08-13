
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Enterprise Document Retriever

Author : Feroz Ali
=========================================================
"""

import logging

from rag.embeddings import EmbeddingManager
from rag.vector_store import VectorStore


logger = logging.getLogger("EnterpriseRetriever")


class EnterpriseRetriever:

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(
        self,
        embedding_manager=None,
        vector_store=None
    ):

        # -------------------------------------------------
        # Reuse existing embedding manager when supplied
        # -------------------------------------------------

        if embedding_manager is not None:

            self.embedding_manager = embedding_manager

        else:

            self.embedding_manager = EmbeddingManager()

        # -------------------------------------------------
        # Reuse existing vector store when supplied
        # -------------------------------------------------

        if vector_store is not None:

            self.vector_store = vector_store

        else:

            self.vector_store = VectorStore(
                dimension=self.embedding_manager.EMBEDDING_DIMENSION
            )

        logger.info(
            "Enterprise Retriever Initialized"
        )

        logger.info(
            "Embedding Dimension: %s",
            self.embedding_manager.EMBEDDING_DIMENSION
        )

        logger.info(
            "Vector Documents: %s",
            self.vector_store.index.ntotal
        )

    # =====================================================
    # Retrieve Similar Documents
    # =====================================================

    def retrieve(
        self,
        question: str,
        top_k: int = 5
    ):

        try:

            if question is None:

                return []

            question = str(
                question
            ).strip()

            if not question:

                return []

            # -------------------------------------------------
            # Generate query embedding
            # -------------------------------------------------

            query_embedding = (
                self.embedding_manager.embed_text(
                    question
                )
            )

            # -------------------------------------------------
            # Search FAISS
            # -------------------------------------------------

            results = self.vector_store.search(
                query_embedding,
                top_k=top_k
            )

            logger.info(
                "Retrieved %s documents for query.",
                len(results)
            )

            return results

        except Exception as e:

            logger.exception(
                "Retrieval Error: %s",
                e
            )

            return []

    # =====================================================
    # Retrieve Context For LLM
    # =====================================================

    def retrieve_context(
        self,
        question: str,
        top_k: int = 5
    ):

        documents = self.retrieve(
            question,
            top_k
        )

        if not documents:

            return (
                "No relevant enterprise knowledge "
                "was found in the available knowledge base."
            )

        context = []

        for index, item in enumerate(
            documents,
            start=1
        ):

            document = item.get(
                "document"
            )

            score = item.get(
                "score",
                0.0
            )

            # -------------------------------------------------
            # Extract document text
            # -------------------------------------------------

            if hasattr(
                document,
                "page_content"
            ):

                text = document.page_content

            elif hasattr(
                document,
                "text"
            ):

                text = document.text

            elif isinstance(
                document,
                dict
            ):

                text = document.get(
                    "text",
                    document.get(
                        "page_content",
                        str(document)
                    )
                )

            else:

                text = str(
                    document
                )

            text = str(
                text
            ).strip()

            if not text:

                continue

            context.append(
                f"""
Document {index}
Relevance Score: {float(score):.4f}

{text}
"""
            )

        if not context:

            return (
                "No usable enterprise knowledge "
                "was found in the retrieved documents."
            )

        return "\n\n".join(
            context
        )

    # =====================================================
    # Health Check
    # =====================================================

    def health(
        self
    ):

        try:

            count = (
                self.vector_store
                .index
                .ntotal
            )

            return {
                "status": "healthy",
                "documents": count,
                "embedding_model": (
                    "sentence-transformers/"
                    "all-MiniLM-L6-v2"
                ),
                "embedding_dimension": (
                    self.embedding_manager
                    .EMBEDDING_DIMENSION
                ),
                "vector_store": "FAISS"
            }

        except Exception as e:

            logger.exception(
                "Retriever health check failed."
            )

            return {
                "status": "error",
                "message": str(e)
            }


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    retriever = EnterpriseRetriever()

    print(
        "\n=========================================="
    )

    print(
        "RETRIEVER HEALTH"
    )

    print(
        "=========================================="
    )

    print(
        retriever.health()
    )

    question = (
        "Why did sales decrease?"
    )

    print(
        "\n=========================================="
    )

    print(
        "RETRIEVAL TEST"
    )

    print(
        "=========================================="
    )

    results = retriever.retrieve(
        question,
        top_k=5
    )

    for result in results:

        print(
            result
        )

    print(
        "\n=========================================="
    )

    print(
        "CONTEXT"
    )

    print(
        "=========================================="
    )

    print(
        retriever.retrieve_context(
            question,
            top_k=5
        )
    )

