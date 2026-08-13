from backend.cache.cache_service import CacheService

CacheService.set(
    "company",
    {
        "name": "Enterprise AI",
        "country": "Pakistan"
    }
)

print(CacheService.get("company"))