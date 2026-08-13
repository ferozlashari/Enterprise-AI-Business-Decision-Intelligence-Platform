"""
=========================================================
Enterprise AI Business Decision Intelligence Platform

Redis Cache Service

Author : Feroz Ali
=========================================================
"""


import json
import logging

from backend.cache.redis_client import redis_client



logger = logging.getLogger(__name__)




class CacheService:



    # =====================================================
    # Get Cache
    # =====================================================

    @staticmethod
    def get(key: str):


        try:


            value = redis_client.get(key)


            if value is None:

                return None



            if isinstance(value, bytes):

                value = value.decode("utf-8")



            return json.loads(value)



        except Exception as e:


            logger.error(

                f"Redis GET Error : {e}"

            )


            return None






    # =====================================================
    # Set Cache
    # =====================================================

    @staticmethod
    def set(
        key: str,
        value,
        expire=3600
    ):


        try:


            redis_client.set(

                key,

                json.dumps(

                    value,

                    default=str

                ),

                ex=expire

            )


            return True



        except Exception as e:


            logger.error(

                f"Redis SET Error : {e}"

            )


            return False






    # =====================================================
    # Delete Cache
    # =====================================================

    @staticmethod
    def delete(key: str):


        try:


            return redis_client.delete(key)



        except Exception as e:


            logger.error(

                f"Redis DELETE Error : {e}"

            )


            return False






    # =====================================================
    # Check Exists
    # =====================================================

    @staticmethod
    def exists(key: str):


        try:


            return bool(

                redis_client.exists(key)

            )



        except Exception as e:


            logger.error(

                f"Redis EXISTS Error : {e}"

            )


            return False






    # =====================================================
    # Get Remaining TTL
    # =====================================================

    @staticmethod
    def ttl(key: str):


        try:


            return redis_client.ttl(key)



        except Exception as e:


            logger.error(

                f"Redis TTL Error : {e}"

            )


            return -1






    # =====================================================
    # Clear Current Database
    # =====================================================

    @staticmethod
    def clear():


        try:


            redis_client.flushdb()


            return True



        except Exception as e:


            logger.error(

                f"Redis CLEAR Error : {e}"

            )


            return False






    # =====================================================
    # Clear All Databases
    # =====================================================

    @staticmethod
    def clear_all():


        try:


            redis_client.flushall()


            return True



        except Exception as e:


            logger.error(

                f"Redis CLEAR ALL Error : {e}"

            )


            return False