from fastapi import APIRouter

from backend.monitoring.health import health
from backend.monitoring.metrics import Metrics

router = APIRouter(
    prefix="/monitor",
    tags=["Monitoring"]
)

@router.get("/health")
def check():

    Metrics.request()
    return health()


@router.get("/metrics")
def metrics():

    Metrics.request()
    return Metrics.stats()