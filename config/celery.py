import os
from celery import Celery

# we tell celery where to find the django settings:
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("chronos_predictor")
# we load celery config from django settings, all keys prefixed with CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")
# we auto discover tasks from all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    # for testing that celery is working:
    print(f"[Celery] request: {self.request!r}")