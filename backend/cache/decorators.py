
"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Redis Cache Decorator

Provides safe Redis caching for service functions and
methods while preserving the complete function arguments
inside the cache key.

Author : Feroz Ali
=========================================================
"""

import functools
import hashlib
import json
import logging

from backend.cache.cache_service import CacheService


logger = logging.getLogger("RedisCache")


# =========================================================
# Configuration
# =========================================================

CACHE_DEBUG = True


# =========================================================
# Stable Object Serialization
# =========================================================

def _serialize_value(value):
    """
    Convert a Python value into a stable JSON-compatible
    representation for cache-key generation.

    Important:
    - Strings are preserved.
    - Numbers are preserved.
    - Lists are serialized recursively.
    - Dictionaries are sorted.
    - Objects such as `self` are represented by their class
      name instead of memory addresses.
    """

    if value is None:
        return None

    # -----------------------------------------------------
    # Primitive values
    # -----------------------------------------------------

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool
        )
    ):
        return value

    # -----------------------------------------------------
    # Lists / tuples
    # -----------------------------------------------------

    if isinstance(
        value,
        (list, tuple)
    ):
        return [
            _serialize_value(item)
            for item in value
        ]

    # -----------------------------------------------------
    # Sets
    # -----------------------------------------------------

    if isinstance(value, set):

        return sorted(
            [
                _serialize_value(item)
                for item in value
            ],
            key=str
        )

    # -----------------------------------------------------
    # Dictionaries
    # -----------------------------------------------------

    if isinstance(value, dict):

        return {
            str(key):
                _serialize_value(item)

            for key, item in sorted(
                value.items(),
                key=lambda pair: str(pair[0])
            )
        }

    # -----------------------------------------------------
    # Objects
    # -----------------------------------------------------

    return {
        "__type__":
            value.__class__.__module__
            + "."
            + value.__class__.__name__
    }


# =========================================================
# Cache Decorator
# =========================================================

def redis_cache(expire=3600):

    """
    Cache the result of a function in Redis.

    The complete logical input is included in the cache key.

    This is especially important for RAG/Copilot questions:

        Question A -> Cache Key A
        Question B -> Cache Key B

    Therefore one Copilot question cannot accidentally return
    another question's cached answer.
    """

    def decorator(function):

        @functools.wraps(function)
        def wrapper(*args, **kwargs):

            # =================================================
            # Build Cache Key
            # =================================================

            try:

                serialized_args = [
                    _serialize_value(arg)
                    for arg in args
                ]

                serialized_kwargs = {
                    str(key):
                        _serialize_value(value)

                    for key, value in sorted(
                        kwargs.items(),
                        key=lambda pair: str(pair[0])
                    )
                }

                raw_key = {

                    "module":
                        function.__module__,

                    "function":
                        function.__qualname__,

                    "args":
                        serialized_args,

                    "kwargs":
                        serialized_kwargs

                }

                key_string = json.dumps(
                    raw_key,
                    sort_keys=True,
                    ensure_ascii=False,
                    separators=(
                        ",",
                        ":"
                    )
                )

                hash_key = hashlib.sha256(
                    key_string.encode("utf-8")
                ).hexdigest()

                cache_key = (
                    f"ai_cache:"
                    f"{function.__module__}:"
                    f"{function.__qualname__}:"
                    f"{hash_key}"
                )

                # -------------------------------------------------
                # Redis GET
                # -------------------------------------------------

                cached_result = CacheService.get(
                    cache_key
                )

                if cached_result is not None:

                    if CACHE_DEBUG:

                        logger.info(
                            "Redis HIT -> %s | key=%s",
                            function.__qualname__,
                            hash_key[:12]
                        )

                    return cached_result

            except Exception as cache_error:

                # -------------------------------------------------
                # Cache-key generation must never break application
                # -------------------------------------------------

                logger.warning(
                    "Redis cache-key generation failed for %s: %s",
                    function.__qualname__,
                    cache_error
                )

                cache_key = None

            # =====================================================
            # Execute Original Function
            # =====================================================

            result = function(
                *args,
                **kwargs
            )

            # =====================================================
            # Save Result
            # =====================================================

            if cache_key is not None:

                try:

                    CacheService.set(
                        cache_key,
                        result,
                        expire
                    )

                    if CACHE_DEBUG:

                        logger.info(
                            "Redis SAVE -> %s | key=%s",
                            function.__qualname__,
                            hash_key[:12]
                        )

                except Exception as cache_error:

                    # -------------------------------------------------
                    # Redis failure must never break application
                    # -------------------------------------------------

                    logger.warning(
                        "Redis SAVE failed for %s: %s",
                        function.__qualname__,
                        cache_error
                    )

            return result

        return wrapper

    return decorator


# =========================================================
# Cache Key Helper
# =========================================================

def generate_cache_key(
    function,
    args,
    kwargs
):
    """
    Generate the same cache key format used by redis_cache().

    Useful for debugging cache behavior.
    """

    serialized_args = [
        _serialize_value(arg)
        for arg in args
    ]

    serialized_kwargs = {
        str(key):
            _serialize_value(value)

        for key, value in sorted(
            kwargs.items(),
            key=lambda pair: str(pair[0])
        )
    }

    raw_key = {

        "module":
            function.__module__,

        "function":
            function.__qualname__,

        "args":
            serialized_args,

        "kwargs":
            serialized_kwargs

    }

    key_string = json.dumps(
        raw_key,
        sort_keys=True,
        ensure_ascii=False,
        separators=(
            ",",
            ":"
        )
    )

    hash_key = hashlib.sha256(
        key_string.encode("utf-8")
    ).hexdigest()

    return (
        f"ai_cache:"
        f"{function.__module__}:"
        f"{function.__qualname__}:"
        f"{hash_key}"
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "REDIS CACHE DECORATOR TEST"
    )

    print(
        "=" * 60
    )

    # -----------------------------------------------------
    # Test function
    # -----------------------------------------------------

    @redis_cache(expire=60)
    def test_question(question):

        print(
            "Executing actual function..."
        )

        return {
            "question": question,
            "answer": (
                f"Answer generated for: {question}"
            )
        }

    # -----------------------------------------------------
    # Question 1
    # -----------------------------------------------------

    question_1 = (
        "What is the total sales of Technology category?"
    )

    result_1 = test_question(
        question_1
    )

    print(
        "\nQuestion 1:"
    )

    print(
        result_1
    )

    # -----------------------------------------------------
    # Question 2
    # -----------------------------------------------------

    question_2 = (
        "What is the total sales of Furniture category?"
    )

    result_2 = test_question(
        question_2
    )

    print(
        "\nQuestion 2:"
    )

    print(
        result_2
    )

    # -----------------------------------------------------
    # Question 3
    # -----------------------------------------------------

    question_3 = (
        "Which regions have the highest sales?"
    )

    result_3 = test_question(
        question_3
    )

    print(
        "\nQuestion 3:"
    )

    print(
        result_3
    )

    # -----------------------------------------------------
    # Generate keys manually
    # -----------------------------------------------------

    key_1 = generate_cache_key(
        test_question.__wrapped__,
        (question_1,),
        {}
    )

    key_2 = generate_cache_key(
        test_question.__wrapped__,
        (question_2,),
        {}
    )

    key_3 = generate_cache_key(
        test_question.__wrapped__,
        (question_3,),
        {}
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "CACHE KEY TEST"
    )

    print(
        "=" * 60
    )

    print(
        "Technology key:",
        key_1
    )

    print(
        "Furniture key:",
        key_2
    )

    print(
        "Region key:",
        key_3
    )

    print(
        "\nKeys are different:",
        len(
            {
                key_1,
                key_2,
                key_3
            }
        ) == 3
    )

    print(
        "\n"
        + "=" * 60
    )

