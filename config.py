import os
MONGODB_SETTINGS = {
  'host': os.environ.get('MONGO_URL'),
  'db': os.environ.get('MONGO_DB')
}
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
FLASK_HTPASSWD_PATH = os.environ.get('FLASK_HTPASSWD_PATH')
FLASK_SECRET = os.environ.get('FLASK_SECRET')
