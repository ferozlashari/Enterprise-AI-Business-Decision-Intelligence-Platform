from fastapi import APIRouter

from backend.tasks.prediction_tasks import run_sales_prediction
from backend.tasks.report_tasks import generate_reports
from backend.tasks.rag_tasks import rebuild_rag

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


@router.post("/sales")
def sales():

    task = run_sales_prediction.delay()

    return {"task_id": task.id}


@router.post("/reports")
def reports():

    task = generate_reports.delay()

    return {"task_id": task.id}


@router.post("/rag")
def rag():

    task = rebuild_rag.delay()

    return {"task_id": task.id}