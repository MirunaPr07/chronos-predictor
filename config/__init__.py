from .celery import app as celery_app
# we expose the celery app here so django loads it on startup
__all__ = ["celery_app"]