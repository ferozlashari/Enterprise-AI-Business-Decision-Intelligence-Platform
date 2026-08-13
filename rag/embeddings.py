
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

RAG Embeddings Manager

Author : Feroz Ali
=========================================================
"""

from typing import List

import numpy as np

from sentence_transformers import SentenceTransformer


class EmbeddingManager:

    # =====================================================
    # Shared Model
    # =====================================================

    _model = None

    # =====================================================
    # Configuration
    # =====================================================

    DEFAULT_MODEL = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    EMBEDDING_DIMENSION = 384

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        local_files_only: bool = True
    ):

        # -------------------------------------------------
        # Reuse already loaded model
        # -------------------------------------------------

        if EmbeddingManager._model is not None:

            self.model = EmbeddingManager._model

            return

        print(
            "Loading Embedding Model..."
        )

        # -------------------------------------------------
        # Local-only mode
        # -------------------------------------------------

        if local_files_only:

            try:

                EmbeddingManager._model = (
                    SentenceTransformer(
                        model_name,
                        local_files_only=True
                    )
                )

                print(
                    "Embedding Model Loaded "
                    "From Local Cache"
                )

            except Exception as error:

                print(
                    "ERROR: Local embedding model "
                    "could not be loaded."
                )

                print(
                    f"Model: {model_name}"
                )

                print(
                    f"Error: {error}"
                )

                raise RuntimeError(
                    "Local embedding model is unavailable. "
                    "The application is configured for "
                    "offline embedding loading. "
                    "Download/cache the model first."
                ) from error

        # -------------------------------------------------
        # Optional online mode
        # -------------------------------------------------

        else:

            EmbeddingManager._model = (
                SentenceTransformer(
                    model_name
                )
            )

            print(
                "Embedding Model Loaded"
            )

        # -------------------------------------------------
        # Store shared model
        # -------------------------------------------------

        self.model = EmbeddingManager._model

        # -------------------------------------------------
        # Verify embedding dimension
        # -------------------------------------------------

        actual_dimension = (
            self.model.get_embedding_dimension()
        )

        if actual_dimension != self.EMBEDDING_DIMENSION:

            raise RuntimeError(
                "Embedding dimension mismatch. "
                f"Expected {self.EMBEDDING_DIMENSION}, "
                f"got {actual_dimension}."
            )

    # =====================================================
    # Normalize Vector
    # =====================================================

    def normalize(
        self,
        vectors
    ):

        vectors = np.asarray(
            vectors,
            dtype=np.float32
        )

        # -------------------------------------------------
        # Empty vector protection
        # -------------------------------------------------

        if vectors.size == 0:

            return vectors

        # -------------------------------------------------
        # Ensure 2D shape
        # -------------------------------------------------

        if vectors.ndim == 1:

            vectors = vectors.reshape(
                1,
                -1
            )

        # -------------------------------------------------
        # Calculate vector norms
        # -------------------------------------------------

        norms = np.linalg.norm(
            vectors,
            axis=1,
            keepdims=True
        )

        # -------------------------------------------------
        # Prevent division by zero
        # -------------------------------------------------

        norms = np.maximum(
            norms,
            1e-12
        )

        return (
            vectors / norms
        ).astype(
            np.float32
        )

    # =====================================================
    # Single Text Embedding
    # =====================================================

    def embed_text(
        self,
        text: str
    ):

        # -------------------------------------------------
        # Safe text handling
        # -------------------------------------------------

        if text is None:

            text = ""

        text = str(text)

        # -------------------------------------------------
        # Generate normalized embedding
        # -------------------------------------------------

        vector = self.model.encode(

            text,

            convert_to_numpy=True,

            normalize_embeddings=True

        )

        vector = np.asarray(
            vector,
            dtype=np.float32
        )

        # -------------------------------------------------
        # Validate dimension
        # -------------------------------------------------

        if vector.shape[-1] != self.EMBEDDING_DIMENSION:

            raise RuntimeError(
                "Generated embedding dimension mismatch. "
                f"Expected {self.EMBEDDING_DIMENSION}, "
                f"got {vector.shape[-1]}."
            )

        return vector

    # =====================================================
    # Multiple Documents Embedding
    # =====================================================

    def embed_documents(
        self,
        documents: List[str]
    ):

        # -------------------------------------------------
        # Empty input
        # -------------------------------------------------

        if not documents:

            return np.empty(

                (
                    0,
                    self.EMBEDDING_DIMENSION
                ),

                dtype=np.float32

            )

        # -------------------------------------------------
        # Convert documents to strings
        # -------------------------------------------------

        texts = []

        for document in documents:

            if document is None:

                texts.append("")

            else:

                texts.append(
                    str(document)
                )

        # -------------------------------------------------
        # Generate normalized embeddings
        # -------------------------------------------------

        vectors = self.model.encode(

            texts,

            batch_size=32,

            show_progress_bar=True,

            convert_to_numpy=True,

            normalize_embeddings=True

        )

        vectors = np.asarray(
            vectors,
            dtype=np.float32
        )

        # -------------------------------------------------
        # Validate embedding dimensions
        # -------------------------------------------------

        if vectors.ndim != 2:

            raise RuntimeError(
                "Unexpected embedding output shape: "
                f"{vectors.shape}"
            )

        if vectors.shape[1] != self.EMBEDDING_DIMENSION:

            raise RuntimeError(
                "Generated embedding dimension mismatch. "
                f"Expected {self.EMBEDDING_DIMENSION}, "
                f"got {vectors.shape[1]}."
            )

        return vectors

    # =====================================================
    # Document Object Support
    # =====================================================

    def embed_llama_documents(
        self,
        documents
    ):

        texts = []

        for doc in documents:

            # -------------------------------------------------
            # LangChain Document
            # -------------------------------------------------

            if hasattr(
                doc,
                "page_content"
            ):

                texts.append(
                    doc.page_content
                )

            # -------------------------------------------------
            # Generic text object
            # -------------------------------------------------

            elif hasattr(
                doc,
                "text"
            ):

                texts.append(
                    doc.text
                )

            # -------------------------------------------------
            # Fallback
            # -------------------------------------------------

            else:

                texts.append(
                    str(doc)
                )

        return self.embed_documents(
            texts
        )


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    embedding = EmbeddingManager()

    documents = [

        "Sales increased by 12 percent.",

        "Inventory shortage detected.",

        "Customer satisfaction improved."

    ]

    vectors = embedding.embed_documents(
        documents
    )

    print(
        "Documents:",
        len(documents)
    )

    print(
        "Embedding Shape:",
        vectors.shape
    )

    print(
        "Embedding Dimension:",
        vectors.shape[1]
    )

