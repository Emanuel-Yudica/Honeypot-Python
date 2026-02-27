import os
from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

app = Celery(
    'honeypot',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    include=['celery_worker.tasks']
)

app.conf.task_track_started = True

# Esto le dice a Celery: "Busca un archivo tasks.py dentro de la carpeta celery_worker"
# En app.py
app.autodiscover_tasks(['celery_worker'])