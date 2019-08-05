web: gunicorn main:app
worker: celery worker -A main.celery --loglevel=info