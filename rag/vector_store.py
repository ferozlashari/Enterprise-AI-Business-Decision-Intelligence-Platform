
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Persistent FAISS Vector Store

Responsibilities:
- Store enterprise document embeddings
- Persist FAISS index
- Persist documents
- Perform cosine-similarity search
- Validate FAISS/document consistency
- Prevent duplicate documents
- Support safe database rebuilding

Author : Feroz Ali
=========================================================
"""

from pathlib import Path
import logging
import pickle

import faiss
import numpy as np


logger = logging.getLogger("VectorStore")


class VectorStore:

    # =====================================================
    # DEFAULT CONFIGURATION
    # =====================================================

    DEFAULT_DIMENSION = 384

    INDEX_FILENAME = "enterprise.index"

    DOCUMENTS_FILENAME = "documents.pkl"

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        dimension=DEFAULT_DIMENSION,
        folder=None
    ):

        self.dimension = int(dimension)

        # -------------------------------------------------
        # IMPORTANT:
        # Always resolve vector database relative to the
        # project root instead of the current terminal
        # working directory.
        # -------------------------------------------------

        if folder is None:

            project_root = (
                Path(__file__)
                .resolve()
                .parent
                .parent
            )

            self.folder = (
                project_root /
                "vector_db"
            )

        else:

            self.folder = Path(
                folder
            ).resolve()

        self.index = None

        self.documents = []

        self.initialize()

    # =====================================================
    # PATHS
    # =====================================================

    @property
    def index_path(self):

        return (
            self.folder /
            self.INDEX_FILENAME
        )

    @property
    def documents_path(self):

        return (
            self.folder /
            self.DOCUMENTS_FILENAME
        )

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(self):

        self.folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # Existing vector database
        # -------------------------------------------------

        if (
            self.index_path.exists()
            and
            self.documents_path.exists()
        ):

            try:

                self.load()

                self.validate()

                logger.info(
                    "FAISS Store Loaded Successfully"
                )

                logger.info(
                    "Documents: %s",
                    len(self.documents)
                )

                logger.info(
                    "Vectors: %s",
                    self.index.ntotal
                )

                logger.info(
                    "Dimension: %s",
                    self.index.d
                )

                return

            except Exception as error:

                logger.exception(
                    "Existing FAISS store is invalid: %s",
                    error
                )

                logger.warning(
                    "Creating a new FAISS database."
                )

        # -------------------------------------------------
        # Create new index
        # -------------------------------------------------

        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        self.documents = []

        logger.info(
            "New FAISS Store Created"
        )

        logger.info(
            "Dimension: %s",
            self.dimension
        )

    # =====================================================
    # VALIDATE DATABASE
    # =====================================================

    def validate(self):

        if self.index is None:

            raise RuntimeError(
                "FAISS index is not initialized."
            )

        # -------------------------------------------------
        # Validate dimension
        # -------------------------------------------------

        if self.index.d != self.dimension:

            raise RuntimeError(
                "FAISS dimension mismatch. "
                f"Expected {self.dimension}, "
                f"got {self.index.d}."
            )

        # -------------------------------------------------
        # Validate document count
        # -------------------------------------------------

        if self.index.ntotal != len(
            self.documents
        ):

            raise RuntimeError(
                "FAISS/document count mismatch. "
                f"FAISS vectors: {self.index.ntotal}, "
                f"documents: {len(self.documents)}."
            )

        return True

    # =====================================================
    # NORMALIZE EMBEDDINGS
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
        # Empty embeddings
        # -------------------------------------------------

        if vectors.size == 0:

            return vectors

        # -------------------------------------------------
        # Ensure 2D
        # -------------------------------------------------

        if vectors.ndim == 1:

            vectors = vectors.reshape(
                1,
                -1
            )

        # -------------------------------------------------
        # Validate dimensions
        # -------------------------------------------------

        if vectors.ndim != 2:

            raise ValueError(
                "Embeddings must be a 1D or 2D array."
            )

        if vectors.shape[1] != self.dimension:

            raise ValueError(
                "Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"got {vectors.shape[1]}."
            )

        # -------------------------------------------------
        # Normalize for cosine similarity
        #
        # IndexFlatIP + normalized vectors =
        # cosine similarity
        # -------------------------------------------------

        faiss.normalize_L2(
            vectors
        )

        return vectors

    # =====================================================
    # DOCUMENT KEY
    # =====================================================

    @staticmethod
    def document_key(
        document
    ):

        """
        Creates a stable key for duplicate detection.

        Supports:
        - strings
        - dictionaries
        - arbitrary objects
        """

        if isinstance(
            document,
            str
        ):

            return document.strip()

        if isinstance(
            document,
            dict
        ):

            # Prefer common document text fields
            for key in (
                "text",
                "content",
                "page_content",
                "document"
            ):

                if key in document:

                    return str(
                        document[key]
                    ).strip()

        return str(
            document
        ).strip()

    # =====================================================
    # ADD DOCUMENTS
    # =====================================================

    def add_documents(
        self,
        embeddings,
        documents
    ):

        if embeddings is None:

            raise ValueError(
                "Embeddings cannot be None."
            )

        if documents is None:

            raise ValueError(
                "Documents cannot be None."
            )

        documents = list(
            documents
        )

        if len(documents) == 0:

            logger.info(
                "No documents supplied."
            )

            return 0

        embeddings = self.normalize(
            embeddings
        )

        # -------------------------------------------------
        # Validate count
        # -------------------------------------------------

        if len(embeddings) != len(
            documents
        ):

            raise ValueError(
                "Embedding/document count mismatch. "
                f"Embeddings: {len(embeddings)}, "
                f"Documents: {len(documents)}."
            )

        # -------------------------------------------------
        # Existing document keys
        # -------------------------------------------------

        existing_keys = {

            self.document_key(
                document
            )

            for document in self.documents

        }

        new_embeddings = []

        new_documents = []

        skipped = 0

        # -------------------------------------------------
        # Prevent duplicates
        # -------------------------------------------------

        for embedding, document in zip(
            embeddings,
            documents
        ):

            key = self.document_key(
                document
            )

            if not key:

                skipped += 1

                continue

            if key in existing_keys:

                skipped += 1

                continue

            existing_keys.add(
                key
            )

            new_embeddings.append(
                embedding
            )

            new_documents.append(
                document
            )

        # -------------------------------------------------
        # Nothing new
        # -------------------------------------------------

        if not new_documents:

            logger.info(
                "No new documents added. "
                "Skipped: %s",
                skipped
            )

            return 0

        # -------------------------------------------------
        # Add to FAISS
        # -------------------------------------------------

        vectors = np.asarray(
            new_embeddings,
            dtype=np.float32
        )

        self.index.add(
            vectors
        )

        # -------------------------------------------------
        # Add documents
        # -------------------------------------------------

        self.documents.extend(
            new_documents
        )

        logger.info(
            "Added %s new documents. "
            "Skipped duplicates/empty: %s",
            len(new_documents),
            skipped
        )

        return len(
            new_documents
        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query_embedding,
        top_k=5,
        min_score=None
    ):

        # -------------------------------------------------
        # Empty database
        # -------------------------------------------------

        if (
            self.index is None
            or
            self.index.ntotal == 0
        ):

            logger.warning(
                "FAISS database is empty."
            )

            return []

        # -------------------------------------------------
        # Validate top_k
        # -------------------------------------------------

        try:

            top_k = int(
                top_k
            )

        except (
            TypeError,
            ValueError
        ):

            top_k = 5

        top_k = max(
            1,
            top_k
        )

        k = min(
            top_k,
            self.index.ntotal
        )

        # -------------------------------------------------
        # Prepare query
        # -------------------------------------------------

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32
        )

        if query_embedding.ndim == 1:

            query_embedding = (
                query_embedding.reshape(
                    1,
                    -1
                )
            )

        # -------------------------------------------------
        # Validate query
        # -------------------------------------------------

        if query_embedding.ndim != 2:

            raise ValueError(
                "Query embedding must be 1D or 2D."
            )

        if (
            query_embedding.shape[1]
            != self.dimension
        ):

            raise ValueError(
                "Query embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"got {query_embedding.shape[1]}."
            )

        # -------------------------------------------------
        # Normalize query
        # -------------------------------------------------

        query_embedding = self.normalize(
            query_embedding
        )

        # -------------------------------------------------
        # FAISS search
        # -------------------------------------------------

        scores, indexes = (
            self.index.search(
                query_embedding,
                k
            )
        )

        results = []

        # -------------------------------------------------
        # Build results
        # -------------------------------------------------

        for score, idx in zip(
            scores[0],
            indexes[0]
        ):

            if idx < 0:

                continue

            if idx >= len(
                self.documents
            ):

                continue

            score = float(
                score
            )

            # -------------------------------------------------
            # Optional relevance threshold
            # -------------------------------------------------

            if (
                min_score is not None
                and
                score < float(
                    min_score
                )
            ):

                continue

            results.append({

                "document":
                    self.documents[idx],

                "score":
                    score,

                "index":
                    int(idx)

            })

        return results

    # =====================================================
    # SEARCH MANY
    # =====================================================

    def search_many(
        self,
        query_embeddings,
        top_k=5,
        min_score=None
    ):

        query_embeddings = np.asarray(
            query_embeddings,
            dtype=np.float32
        )

        if query_embeddings.ndim == 1:

            query_embeddings = (
                query_embeddings.reshape(
                    1,
                    -1
                )
            )

        query_embeddings = self.normalize(
            query_embeddings
        )

        if (
            self.index is None
            or
            self.index.ntotal == 0
        ):

            return []

        k = min(
            int(top_k),
            self.index.ntotal
        )

        scores, indexes = (
            self.index.search(
                query_embeddings,
                k
            )
        )

        all_results = []

        for row_scores, row_indexes in zip(
            scores,
            indexes
        ):

            row_results = []

            for score, idx in zip(
                row_scores,
                row_indexes
            ):

                if idx < 0:

                    continue

                if idx >= len(
                    self.documents
                ):

                    continue

                score = float(
                    score
                )

                if (
                    min_score is not None
                    and
                    score < float(
                        min_score
                    )
                ):

                    continue

                row_results.append({

                    "document":
                        self.documents[idx],

                    "score":
                        score,

                    "index":
                        int(idx)

                })

            all_results.append(
                row_results
            )

        return all_results

    # =====================================================
    # DATABASE STATISTICS
    # =====================================================

    def stats(self):

        return {

            "folder":
                str(self.folder),

            "index_file":
                str(self.index_path),

            "documents_file":
                str(self.documents_path),

            "documents":
                len(self.documents),

            "vectors":
                (
                    int(self.index.ntotal)
                    if self.index is not None
                    else 0
                ),

            "dimension":
                (
                    int(self.index.d)
                    if self.index is not None
                    else self.dimension
                ),

            "is_trained":
                (
                    bool(self.index.is_trained)
                    if self.index is not None
                    else False
                )

        }

    # =====================================================
    # CLEAR DATABASE
    # =====================================================

    def clear(
        self,
        confirm=False
    ):

        if not confirm:

            raise RuntimeError(
                "Database clear operation blocked. "
                "Call clear(confirm=True) "
                "to rebuild the database."
            )

        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        self.documents = []

        self.save()

        logger.warning(
            "FAISS database cleared."
        )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        if self.index is None:

            raise RuntimeError(
                "Cannot save an uninitialized FAISS index."
            )

        self.folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # Validate before saving
        # -------------------------------------------------

        self.validate()

        # -------------------------------------------------
        # Save FAISS index
        # -------------------------------------------------

        faiss.write_index(
            self.index,
            str(
                self.index_path
            )
        )

        # -------------------------------------------------
        # Save documents
        # -------------------------------------------------

        with open(
            self.documents_path,
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        logger.info(
            "FAISS Saved Successfully"
        )

        logger.info(
            "Documents: %s",
            len(self.documents)
        )

        logger.info(
            "Vectors: %s",
            self.index.ntotal
        )

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        if not self.index_path.exists():

            raise FileNotFoundError(
                f"FAISS index not found: "
                f"{self.index_path}"
            )

        if not self.documents_path.exists():

            raise FileNotFoundError(
                f"Documents file not found: "
                f"{self.documents_path}"
            )

        # -------------------------------------------------
        # Load FAISS index
        # -------------------------------------------------

        self.index = faiss.read_index(
            str(
                self.index_path
            )
        )

        # -------------------------------------------------
        # Load documents
        # -------------------------------------------------

        with open(
            self.documents_path,
            "rb"
        ) as file:

            self.documents = pickle.load(
                file
            )

        if not isinstance(
            self.documents,
            list
        ):

            raise RuntimeError(
                "documents.pkl does not contain a list."
            )

        logger.info(
            "Loaded %s documents",
            len(self.documents)
        )

        logger.info(
            "Loaded %s FAISS vectors",
            self.index.ntotal
        )

        return self

    # =====================================================
    # REBUILD DATABASE
    # =====================================================

    def rebuild(
        self,
        embeddings,
        documents
    ):

        """
        Completely rebuild the FAISS database.

        Use this when:
        - source dataset changed
        - old vector database is incomplete
        - embeddings model changed
        - documents.pkl contains stale data
        """

        logger.warning(
            "Rebuilding FAISS database..."
        )

        self.index = faiss.IndexFlatIP(
            self.dimension
        )

        self.documents = []

        added = self.add_documents(
            embeddings,
            documents
        )

        self.save()

        logger.info(
            "FAISS rebuild completed. "
            "Documents: %s",
            added
        )

        return added


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    from rag.embeddings import (
        EmbeddingManager
    )

    print(
        "\n=========================================="
    )

    print(
        "VECTOR STORE TEST"
    )

    print(
        "=========================================="
    )

    # -----------------------------------------------------
    # Embedding manager
    # -----------------------------------------------------

    embedding_manager = (
        EmbeddingManager()
    )

    # -----------------------------------------------------
    # Vector store
    # -----------------------------------------------------

    store = VectorStore(
        dimension=(
            embedding_manager.EMBEDDING_DIMENSION
        )
    )

    # -----------------------------------------------------
    # Health
    # -----------------------------------------------------

    print(
        "\nVector Store Health:"
    )

    print(
        store.stats()
    )

    # -----------------------------------------------------
    # Query
    # -----------------------------------------------------

    query = (
        embedding_manager.embed_text(
            "Which product categories have "
            "the highest sales?"
        )
    )

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    results = store.search(
        query,
        top_k=10
    )

    print(
        "\nSearch Results:"
    )

    if not results:

        print(
            "No documents found."
        )

    for result in results:

        print(
            "\nScore:",
            result["score"]
        )

        print(
            "Index:",
            result["index"]
        )

        print(
            "Document:",
            result["document"]
        )

