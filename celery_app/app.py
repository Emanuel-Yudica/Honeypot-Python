from celery import Celery

app = Celery(
    'honeypot',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['celery_worker.tasks']
)

app.conf.task_track_started = True

# Esto le dice a Celery: "Busca un archivo tasks.py dentro de la carpeta celery_worker"
# En app.py
app.autodiscover_tasks(['celery_worker'])