import time

from backend.celery_app import celery

from backend.services.report_service import ReportService


@celery.task
def generate_reports():

    time.sleep(5)

    ReportService.sales_report()

    ReportService.inventory_report()

    return "Reports Generated"