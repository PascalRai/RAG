from celery import Celery

from app.core.settings import settings
from app.services.ingestion.ingestion_task_pipeline import ingestion_pipeline

# Configure the Celery app
celery_app = Celery(
    "ingestion",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)
celery_app.config_from_object("app.services.ingestion.celeryconfig")

@celery_app.task(
    name="ingestion_pipeline_task",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
    retry_backoff=True
)
def ingestion_task(file_path: str, index_name: str):
    return ingestion_pipeline(file_path, index_name)

# celery -A app.services.ingestion.ingestion_task.celery_app worker --loglevel=info --concurrency=1
# concurrency here run ML models; so 1 for now.