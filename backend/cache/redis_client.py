"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Redis Client

Author : Feroz Ali
=========================================================
"""


import redis
import logging


from config.settings import settings



logger = logging.getLogger("Redis")



# =====================================================
# Redis Connection
# =====================================================


try:


    redis_client = redis.from_url(

        settings.REDIS_URL,

        decode_responses=True,

        socket_connect_timeout=5,

        socket_timeout=5,

        retry_on_timeout=True

    )


    # Test Connection

    redis_client.ping()


    logger.info(

        "Redis Connected Successfully"

    )



except Exception as e:


    logger.error(

        f"Redis Connection Failed : {e}"

    )


    redis_client = None





# =====================================================
# Redis Health Check
# =====================================================


def redis_health():


    try:


        if redis_client is None:


            return {


                "status": "failed",

                "message": "Redis client unavailable"

            }



        redis_client.ping()



        return {


            "status": "healthy",

            "message": "Redis running"

        }



    except Exception as e:


        return {


            "status": "failed",

            "message": str(e)

        }