from backend.cache.cache_service import CacheService


if __name__ == "__main__":

    CacheService.clear()

    print("Redis cache cleared successfully")