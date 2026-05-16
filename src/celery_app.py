from celery import Celery
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

celery_app = Celery(
    "worker",
    broker=f"sqla+sqlite:///{os.path.join(BASE_DIR, 'celerydb.sqlite')}",
    backend=f"db+sqlite:///{os.path.join(BASE_DIR, 'results.sqlite')}"
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)
from .tasks import *