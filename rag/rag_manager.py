
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

RAG Singleton Manager

Author : Feroz Ali
=========================================================
"""

import threading
import logging

from typing import Any, Dict


from rag.rag_pipeline import EnterpriseRAG


logger = logging.getLogger("RAGManager")


class RAGManager:
    """
    Singleton manager for the Enterprise RAG system.

    Responsibilities:
        - Create one EnterpriseRAG instance
        - Provide safe access to RAG methods
        - Expose RAG ask functionality
        - Expose knowledge-base build functionality
        - Provide health information
        - Allow RAG reset/reinitialization
    """

    # =====================================================
    # Singleton State
    # =====================================================

    _instance = None

    _lock = threading.Lock()

    # =====================================================
    # Get Singleton Instance
    # =====================================================

    @classmethod
    def get_instance(cls):
        """
        Return the single EnterpriseRAG instance.

        Uses double-checked locking so the RAG system
        is initialized only once.
        """

        # -------------------------------------------------
        # Fast path
        # -------------------------------------------------

        if cls._instance is None:

            with cls._lock:

                # -------------------------------------------------
                # Double-check inside lock
                # -------------------------------------------------

                if cls._instance is None:

                    logger.info(
                        "Creating Enterprise RAG Instance..."
                    )

                    try:

                        cls._instance = EnterpriseRAG()

                        logger.info(
                            "Enterprise RAG Instance Created Successfully"
                        )

                    except Exception:

                        logger.exception(
                            "Failed to create Enterprise RAG instance"
                        )

                        cls._instance = None

                        raise

        return cls._instance

    # =====================================================
    # Ask RAG
    # =====================================================

    @classmethod
    def ask(
        cls,
        question: str
    ) -> Dict[str, Any]:
        """
        Send a question to the Enterprise RAG system.

        The rest of the application should use this
        method instead of directly creating EnterpriseRAG.
        """

        question = str(
            question or ""
        ).strip()

        # -------------------------------------------------
        # Validate question
        # -------------------------------------------------

        if not question:

            return {

                "status":
                    "error",

                "answer":
                    "",

                "context":
                    "",

                "message":
                    "RAG question cannot be empty."

            }

        try:

            rag = cls.get_instance()

            logger.info(
                "RAG Question: %s",
                question
            )

            result = rag.ask(
                question
            )

            # -------------------------------------------------
            # Normalize dictionary response
            # -------------------------------------------------

            if isinstance(
                result,
                dict
            ):

                return result

            # -------------------------------------------------
            # Normalize string response
            # -------------------------------------------------

            if isinstance(
                result,
                str
            ):

                return {

                    "status":
                        "success",

                    "answer":
                        result,

                    "context":
                        ""

                }

            # -------------------------------------------------
            # Normalize unexpected response
            # -------------------------------------------------

            return {

                "status":
                    "success",

                "answer":
                    str(result),

                "context":
                    ""

            }

        except Exception as error:

            logger.exception(
                "RAG Ask Failed"
            )

            return {

                "status":
                    "rag_unavailable",

                "answer":
                    "",

                "context":
                    "",

                "message":
                    str(error)

            }

    # =====================================================
    # Build Vector Database
    # =====================================================

    @classmethod
    def build_vector_database(
        cls
    ) -> Dict[str, Any]:
        """
        Build or rebuild the Enterprise FAISS knowledge base.

        Delegates the actual work to EnterpriseRAG.
        """

        try:

            rag = cls.get_instance()

            logger.info(
                "Starting Enterprise RAG Vector Database Build..."
            )

            # -------------------------------------------------
            # EnterpriseRAG must provide this method.
            # -------------------------------------------------

            result = rag.build_vector_database()

            logger.info(
                "Enterprise RAG Vector Database Build Completed"
            )

            # -------------------------------------------------
            # Normalize result
            # -------------------------------------------------

            if isinstance(
                result,
                dict
            ):

                return result

            return {

                "status":
                    "success",

                "result":
                    result

            }

        except Exception as error:

            logger.exception(
                "RAG Vector Database Build Failed"
            )

            return {

                "status":
                    "error",

                "result":
                    None,

                "message":
                    str(error)

            }

    # =====================================================
    # Health Check
    # =====================================================

    @classmethod
    def health(
        cls
    ) -> Dict[str, Any]:
        """
        Return health information about the RAG system.

        Does not initialize RAG unnecessarily.
        """

        # -------------------------------------------------
        # RAG has not been initialized
        # -------------------------------------------------

        if cls._instance is None:

            return {

                "status":
                    "not_initialized",

                "rag":
                    False,

                "llm":
                    "Groq",

                "embedding_model":
                    (
                        "sentence-transformers/"
                        "all-MiniLM-L6-v2"
                    ),

                "embedding_dimension":
                    384,

                "vector_store":
                    "FAISS",

                "documents":
                    0

            }

        # -------------------------------------------------
        # Get health information from EnterpriseRAG
        # -------------------------------------------------

        try:

            rag_health = cls._instance.health()

            if not isinstance(
                rag_health,
                dict
            ):

                rag_health = {}

            return {

                "status":
                    rag_health.get(
                        "status",
                        "healthy"
                    ),

                "rag":
                    True,

                "llm":
                    rag_health.get(
                        "llm",
                        "Groq"
                    ),

                "model":
                    rag_health.get(
                        "model"
                    ),

                "embedding_model":
                    rag_health.get(
                        "embedding_model",
                        (
                            "sentence-transformers/"
                            "all-MiniLM-L6-v2"
                        )
                    ),

                "embedding_dimension":
                    rag_health.get(
                        "embedding_dimension",
                        384
                    ),

                "vector_store":
                    rag_health.get(
                        "vector_store",
                        "FAISS"
                    ),

                "documents":
                    rag_health.get(
                        "documents",
                        0
                    )

            }

        except Exception as error:

            logger.exception(
                "RAG Health Check Error"
            )

            return {

                "status":
                    "error",

                "rag":
                    False,

                "llm":
                    "Groq",

                "embedding_model":
                    (
                        "sentence-transformers/"
                        "all-MiniLM-L6-v2"
                    ),

                "embedding_dimension":
                    384,

                "vector_store":
                    "FAISS",

                "documents":
                    0,

                "message":
                    str(error)

            }

    # =====================================================
    # Reset RAG
    # =====================================================

    @classmethod
    def reset(
        cls
    ):
        """
        Reset the Enterprise RAG singleton.

        Useful when rebuilding the RAG system or when
        configuration/model state needs to be reloaded.
        """

        with cls._lock:

            cls._instance = None

            logger.info(
                "Enterprise RAG Instance Reset"
            )

    # =====================================================
    # Is RAG Initialized?
    # =====================================================

    @classmethod
    def is_initialized(
        cls
    ) -> bool:
        """
        Check whether EnterpriseRAG has already been
        initialized.
        """

        return cls._instance is not None


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "RAG MANAGER TEST"
    )

    print(
        "=" * 60
    )

    # -----------------------------------------------------
    # Health before initialization
    # -----------------------------------------------------

    print(
        "\nRAG Manager Health Before Initialization:\n"
    )

    print(
        RAGManager.health()
    )

    # -----------------------------------------------------
    # Initialize RAG
    # -----------------------------------------------------

    print(
        "\nInitializing Enterprise RAG...\n"
    )

    try:

        rag = RAGManager.get_instance()

        print(
            "RAG initialized:",
            rag is not None
        )

    except Exception as error:

        print(
            "RAG initialization failed:",
            error
        )

    # -----------------------------------------------------
    # Health after initialization
    # -----------------------------------------------------

    print(
        "\nRAG Manager Health After Initialization:\n"
    )

    print(
        RAGManager.health()
    )

    # -----------------------------------------------------
    # Initialization state
    # -----------------------------------------------------

    print(
        "\nRAG Initialized:"
    )

    print(
        RAGManager.is_initialized()
    )

    print(
        "\n"
        + "=" * 60
    )

