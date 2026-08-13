import time

from backend.celery_app import celery

from rag.document_loader import EnterpriseDocumentLoader


@celery.task
def rebuild_rag():

    time.sleep(5)

    EnterpriseDocumentLoader()

    return "Knowledge Base Updated"