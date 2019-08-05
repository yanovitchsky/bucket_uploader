import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_SETTINGS = {
  'host': os.environ.get('MONGO_URL'),
  'db': os.environ.get('MONGO_DB')
}
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
FLASK_HTPASSWD_PATH = os.environ.get('FLASK_HTPASSWD_PATH')
FLASK_SECRET = os.environ.get('FLASK_SECRET')
CELERY_ALWAYS_EAGER=os.environ.get('CELERY_ALWAYS_EAGER')
UPLOAD_FOLDER = os.path.abspath(os.environ.get('UPLOAD_FOLDER'))