import time

from backend.celery_app import celery

from backend.models.sales_prediction import SalesPrediction


@celery.task
def run_sales_prediction():

    time.sleep(5)

    SalesPrediction.train_model()

    return "Sales Prediction Completed"