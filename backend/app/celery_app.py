from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "storyofdubai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.pipeline.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Dubai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Named queues — scrapers, enrichment, default
    task_queues={
        "scrapers": {"exchange": "scrapers", "routing_key": "scrapers"},
        "enrichment": {"exchange": "enrichment", "routing_key": "enrichment"},
        "default": {"exchange": "default", "routing_key": "default"},
    },
    task_default_queue="default",
    # Route specific tasks to specific queues
    task_routes={
        "app.pipeline.tasks.scrape_*": {"queue": "scrapers"},
        "app.pipeline.tasks.enrich_*": {"queue": "enrichment"},
    },
    # Beat schedule — Dubai timezone (UTC+4)
    beat_schedule={
        "scrape-google-places-daily": {
            "task": "app.pipeline.tasks.scrape_google_places_all_areas",
            "schedule": crontab(hour=2, minute=0),  # 2 AM Dubai
        },
        "run-scoring-engine-daily": {
            "task": "app.pipeline.tasks.run_scoring_engine_all",
            "schedule": crontab(hour=4, minute=0),  # 4 AM Dubai
        },
        "run-ai-enrichment-daily": {
            "task": "app.pipeline.tasks.run_ai_enrichment_pending",
            "schedule": crontab(hour=5, minute=0),  # 5 AM Dubai
        },
        "trigger-nextjs-rebuild-daily": {
            "task": "app.pipeline.tasks.trigger_nextjs_rebuild",
            "schedule": crontab(hour=6, minute=0),  # 6 AM Dubai
        },
    },
)
