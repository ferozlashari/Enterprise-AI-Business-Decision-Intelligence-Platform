
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Enterprise RAG Pipeline

Author : Feroz Ali
=========================================================
"""

import logging
import threading

from groq import Groq

from config.settings import settings

from rag.document_loader import (
    EnterpriseDocumentLoader
)

from rag.embeddings import (
    EmbeddingManager
)

from rag.vector_store import (
    VectorStore
)

from rag.retriever import (
    EnterpriseRetriever
)

from rag.prompt_templates import (
    BUSINESS_PROMPT
)

from backend.cache.decorators import (
    redis_cache
)


logger = logging.getLogger(
    "EnterpriseRAG"
)


class EnterpriseRAG:

    # =====================================================
    # Shared Groq Client
    # =====================================================

    _llm = None

    _llm_lock = threading.Lock()

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(self):

        logger.info(
            "Initializing Enterprise RAG..."
        )

        # -------------------------------------------------
        # Document Loader
        # -------------------------------------------------

        self.loader = EnterpriseDocumentLoader()

        # -------------------------------------------------
        # Embedding Manager
        # -------------------------------------------------

        self.embedding = EmbeddingManager()

        # -------------------------------------------------
        # Vector Store
        # -------------------------------------------------

        self.vector_store = VectorStore(
            dimension=(
                self.embedding.EMBEDDING_DIMENSION
            )
        )

        # -------------------------------------------------
        # Retriever
        # -------------------------------------------------

        self.retriever = EnterpriseRetriever(

            embedding_manager=self.embedding,

            vector_store=self.vector_store

        )

        # -------------------------------------------------
        # Groq
        # -------------------------------------------------

        self.load_llm()

        logger.info(
            "Enterprise RAG initialized successfully"
        )

    # =====================================================
    # Load Groq Client
    # =====================================================

    def load_llm(self):

        if EnterpriseRAG._llm is None:

            with EnterpriseRAG._llm_lock:

                if EnterpriseRAG._llm is None:

                    api_key = getattr(
                        settings,
                        "GROQ_API_KEY",
                        None
                    )

                    if not api_key:

                        raise ValueError(
                            "GROQ_API_KEY is missing "
                            "in the .env file."
                        )

                    logger.info(
                        "Connecting to Groq..."
                    )

                    EnterpriseRAG._llm = Groq(
                        api_key=api_key
                    )

                    logger.info(
                        "Groq Connected Successfully"
                    )

        self.llm = EnterpriseRAG._llm

    # =====================================================
    # Get Model Name
    # =====================================================

    @staticmethod
    def get_embedding_model_name():

        return (
            "sentence-transformers/"
            "all-MiniLM-L6-v2"
        )

    # =====================================================
    # Build Vector Database
    # =====================================================

    def build_vector_database(
        self,
        rebuild=False
    ):
        """
        Build the enterprise FAISS knowledge database.

        Parameters
        ----------
        rebuild : bool
            False:
                Keep existing FAISS database.

            True:
                Delete the existing in-memory FAISS index
                and rebuild it from the current knowledge_base.

        This is important after changing the
        EnterpriseDocumentLoader because the old FAISS
        database does not automatically know about newly
        generated business summary documents.
        """

        try:

            logger.info(
                "Starting Enterprise RAG Vector Database Build..."
            )

            # =================================================
            # REBUILD
            # =================================================

            if rebuild:

                logger.warning(
                    "REBUILD requested. "
                    "Clearing existing FAISS database..."
                )

                self.vector_store.clear(
                    confirm=True
                )

            # =================================================
            # EXISTING DATABASE
            # =================================================

            if (
                not rebuild
                and
                self.vector_store.index is not None
                and
                self.vector_store.index.ntotal > 0
            ):

                document_count = (
                    self.vector_store.index.ntotal
                )

                logger.info(
                    "Existing FAISS database detected: %s vectors",
                    document_count
                )

                return {

                    "status":
                        "already_exists",

                    "documents":
                        document_count,

                    "embedding_dimension":
                        self.embedding.EMBEDDING_DIMENSION,

                    "vector_store":
                        "FAISS",

                    "message":
                        (
                            "Existing vector database "
                            "was kept. Use rebuild=True "
                            "to rebuild it."
                        )

                }

            # =================================================
            # LOAD DOCUMENTS
            # =================================================

            logger.info(
                "Loading enterprise knowledge documents..."
            )

            documents = (
                self.loader.load_all_documents()
            )

            if not documents:

                logger.warning(
                    "No enterprise documents found."
                )

                return {

                    "status":
                        "empty",

                    "documents":
                        0,

                    "message":
                        (
                            "No documents found in "
                            "knowledge_base."
                        )

                }

            logger.info(
                "Enterprise documents loaded: %s",
                len(documents)
            )

            # =================================================
            # DOCUMENT TYPE STATISTICS
            # =================================================

            statistics = {}

            for document in documents:

                document_type = (
                    document.metadata.get(
                        "type",
                        "unknown"
                    )
                )

                statistics[
                    document_type
                ] = (
                    statistics.get(
                        document_type,
                        0
                    )
                    + 1
                )

            logger.info(
                "Document statistics: %s",
                statistics
            )

            # =================================================
            # GENERATE EMBEDDINGS
            # =================================================

            logger.info(
                "Generating document embeddings..."
            )

            vectors = (
                self.embedding.embed_llama_documents(
                    documents
                )
            )

            # =================================================
            # NORMALIZE EMBEDDING ARRAY
            # =================================================

            vectors_count = len(
                vectors
            )

            if vectors_count != len(
                documents
            ):

                raise RuntimeError(

                    "Embedding/document count mismatch. "

                    f"Documents: {len(documents)}, "

                    f"Embeddings: {vectors_count}"

                )

            # =================================================
            # VALIDATE VECTOR DIMENSION
            # =================================================

            if vectors.ndim != 2:

                raise RuntimeError(

                    "Invalid embedding array. "

                    f"Expected 2D array, got "
                    f"shape {vectors.shape}"

                )

            expected_dimension = (
                self.embedding.EMBEDDING_DIMENSION
            )

            actual_dimension = (
                vectors.shape[1]
            )

            if actual_dimension != (
                expected_dimension
            ):

                raise RuntimeError(

                    "Embedding dimension mismatch. "

                    f"Expected "
                    f"{expected_dimension}, "

                    f"got "
                    f"{actual_dimension}"

                )

            # =================================================
            # ADD DOCUMENTS
            # =================================================

            logger.info(
                "Adding documents to FAISS..."
            )

            self.vector_store.add_documents(

                vectors,

                documents

            )

            # =================================================
            # VALIDATE FAISS
            # =================================================

            if (
                self.vector_store.index.ntotal
                != len(documents)
            ):

                raise RuntimeError(

                    "FAISS/document count mismatch "
                    "after insertion. "

                    f"FAISS vectors: "
                    f"{self.vector_store.index.ntotal}, "

                    f"Documents: "
                    f"{len(documents)}"

                )

            # =================================================
            # SAVE
            # =================================================

            logger.info(
                "Saving FAISS database..."
            )

            self.vector_store.save()

            # =================================================
            # SUCCESS
            # =================================================

            logger.info(
                "Enterprise vector database "
                "built successfully."
            )

            return {

                "status":
                    "success",

                "documents":
                    len(documents),

                "embedding_dimension":
                    expected_dimension,

                "vector_store":
                    "FAISS",

                "document_types":
                    statistics,

                "rebuilt":
                    bool(rebuild)

            }

        except Exception as error:

            logger.exception(
                "Vector database build failed."
            )

            return {

                "status":
                    "error",

                "documents":
                    0,

                "message":
                    str(error)

            }

    # =====================================================
    # Force Rebuild
    # =====================================================

    def rebuild_vector_database(self):

        logger.warning(
            "Forcing complete Enterprise RAG rebuild..."
        )

        return self.build_vector_database(
            rebuild=True
        )

    # =====================================================
    # Retrieve Context
    # =====================================================

    def retrieve_context(
        self,
        question: str,
        top_k: int = 8
    ):
        """
        Retrieve relevant enterprise documents.

        Kept as a separate method so retrieval can be
        tested independently from Groq generation.
        """

        question = str(
            question or ""
        ).strip()

        if not question:

            return ""

        if (
            self.vector_store.index is None
            or
            self.vector_store.index.ntotal == 0
        ):

            return ""

        try:

            context = (
                self.retriever.retrieve_context(
                    question,
                    top_k=top_k
                )
            )

            return str(
                context or ""
            ).strip()

        except Exception as error:

            logger.exception(
                "Enterprise context retrieval failed."
            )

            return ""

    # =====================================================
    # Ask Enterprise AI
    # =====================================================

    @redis_cache(
        expire=1800
    )
    def ask(
        self,
        question: str
    ):

        # =================================================
        # VALIDATE
        # =================================================

        if question is None:

            return {

                "status":
                    "error",

                "message":
                    "Question is required."

            }

        question = str(
            question
        ).strip()

        if not question:

            return {

                "status":
                    "error",

                "message":
                    "Question cannot be empty."

            }

        try:

            logger.info(
                "RAG question: %s",
                question
            )

            # =================================================
            # CHECK VECTOR DATABASE
            # =================================================

            if (
                self.vector_store.index is None
                or
                self.vector_store.index.ntotal == 0
            ):

                logger.warning(
                    "FAISS vector database is empty."
                )

                return {

                    "status":
                        "error",

                    "question":
                        question,

                    "message":
                        (
                            "Enterprise knowledge "
                            "database is empty. "
                            "Build the vector database first."
                        )

                }

            # =================================================
            # RETRIEVE CONTEXT
            # =================================================

            context = (
                self.retrieve_context(
                    question,
                    top_k=8
                )
            )

            if not context:

                logger.warning(
                    "No relevant enterprise context found."
                )

                return {

                    "status":
                        "insufficient_context",

                    "question":
                        question,

                    "context":
                        "",

                    "answer":
                        (
                            "The available enterprise "
                            "knowledge base does not contain "
                            "enough relevant information to "
                            "answer this question reliably."
                        )

                }

            logger.info(
                "Enterprise context retrieved successfully."
            )

            # =================================================
            # BUSINESS PROMPT
            # =================================================

            prompt = BUSINESS_PROMPT.format(

                question=
                    question,

                context=
                    context

            )

            # =================================================
            # GROQ SYSTEM INSTRUCTION
            # =================================================

            system_prompt = """
You are an Enterprise AI Business Consultant.

You answer enterprise business questions using
ONLY the enterprise evidence provided in the
retrieved context.

IMPORTANT RULES:

1. Use the provided enterprise context as the
   primary source of truth.

2. Do not invent facts, numbers, regions,
   products, dates, trends, or business events.

3. Do not assume that a single sample represents
   the entire enterprise.

4. If the evidence is insufficient, explicitly
   say that the available enterprise data is
   insufficient.

5. Distinguish historical facts from predictions
   and recommendations.

6. For trend questions such as:
      - declining sales
      - increasing sales
      - growth
      - month-over-month change
      - year-over-year change

   require actual time-series evidence.

7. For comparison questions such as:
      - top categories
      - best products
      - worst regions
      - highest revenue regions

   use aggregated business-summary evidence when
   available.

8. Never infer a trend from isolated transactions.

9. If only one region/category/product is available,
   clearly state that the comparison is limited.

10. Recommendations must be based on available
    evidence.

11. Keep the answer professional and concise.

12. Structure the response when appropriate as:

    EXECUTIVE SUMMARY

    BUSINESS ANALYSIS

    EVIDENCE

    RISKS

    RECOMMENDATIONS

    CONFIDENCE
"""

            # =================================================
            # GROQ REQUEST
            # =================================================

            response = (
                self.llm.chat.completions.create(

                    model=settings.GROQ_MODEL,

                    messages=[

                        {
                            "role":
                                "system",

                            "content":
                                system_prompt

                        },

                        {
                            "role":
                                "user",

                            "content":
                                prompt

                        }

                    ],

                    temperature=0.1,

                    max_tokens=800

                )
            )

            # =================================================
            # VALIDATE RESPONSE
            # =================================================

            if not response:

                raise RuntimeError(
                    "Groq returned an empty response."
                )

            if not response.choices:

                raise RuntimeError(
                    "Groq returned no response choices."
                )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            if not answer:

                raise RuntimeError(
                    "Groq returned empty answer content."
                )

            answer = answer.strip()

            logger.info(
                "Groq response generated successfully."
            )

            # =================================================
            # RETURN RESULT
            # =================================================

            return {

                "status":
                    "success",

                "question":
                    question,

                "context":
                    context,

                "answer":
                    answer,

                "documents":
                    self.vector_store.index.ntotal

            }

        except Exception as error:

            logger.exception(
                "Enterprise RAG request failed."
            )

            return {

                "status":
                    "error",

                "question":
                    question,

                "message":
                    str(error)

            }

    # =====================================================
    # Health Check
    # =====================================================

    def health(
        self
    ):

        try:

            document_count = 0

            if (
                self.vector_store.index
                is not None
            ):

                document_count = (
                    self.vector_store.index.ntotal
                )

            return {

                "status":
                    "healthy",

                "llm":
                    "Groq",

                "model":
                    settings.GROQ_MODEL,

                "embedding_model":
                    self.get_embedding_model_name(),

                "embedding_dimension":
                    self.embedding.EMBEDDING_DIMENSION,

                "vector_store":
                    "FAISS",

                "documents":
                    document_count

            }

        except Exception as error:

            logger.exception(
                "Enterprise RAG health check failed."
            )

            return {

                "status":
                    "error",

                "message":
                    str(error)

            }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    rag = EnterpriseRAG()

    print(
        "\n=========================================="
    )

    print(
        "RAG HEALTH"
    )

    print(
        "=========================================="
    )

    print(
        rag.health()
    )

    # =====================================================
    # BUILD / REBUILD
    # =====================================================

    print(
        "\n=========================================="
    )

    print(
        "REBUILD VECTOR DATABASE"
    )

    print(
        "=========================================="
    )

    build_result = (
        rag.rebuild_vector_database()
    )

    print(
        build_result
    )

    # =====================================================
    # HEALTH AFTER BUILD
    # =====================================================

    print(
        "\n=========================================="
    )

    print(
        "RAG HEALTH AFTER BUILD"
    )

    print(
        "=========================================="
    )

    print(
        rag.health()
    )

    # =====================================================
    # RAG TEST
    # =====================================================

    print(
        "\n=========================================="
    )

    print(
        "RAG TEST"
    )

    print(
        "=========================================="
    )

    result = rag.ask(
        "What are our top performing product categories?"
    )

    print(
        "\nRESULT:"
    )

    print(
        result
    )

