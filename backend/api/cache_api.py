from fastapi import APIRouter

from backend.cache.cache_service import CacheService

router = APIRouter(
    prefix="/cache",
    tags=["Cache"]
)


@router.delete("/clear")
def clear_cache():

    CacheService.clear()

    return {
        "message": "Redis cache cleared successfully."
    }