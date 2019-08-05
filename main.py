import os
import sys
import requests
from flask import Flask, render_template, jsonify, make_response, abort, request
from random import *
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from mongoengine import Q
from google.cloud import storage
from datetime import datetime,timedelta,timezone
import json
import googleapiclient.discovery
from werkzeug.utils import secure_filename
from boto3.session import Session
from bson import ObjectId
from celery import Celery
from flask_htpasswd import HtPasswdAuth


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

#Configuration
app = Flask(__name__, 
  static_folder = "./dist/static",
  template_folder = "./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
# app.config['MONGODB_DB'] = 'bucket_uploader_test'
app.config.from_pyfile('config.py')
db = MongoEngine(app)
UPLOAD_FOLDER =  os.path.abspath('upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

celery = make_celery(app)

print(app.config['FLASK_HTPASSWD_PATH'])
htpasswd = HtPasswdAuth(app)

# models
BUCKET_TYPE = ('Amazon S3', 'Google Storage')
TRANSFER_TYPE = ('S3', 'GCS', 'LOCAL')
class Bucket(db.Document):
  name = db.StringField(required=True, max_length=120)
  aws_access_key = db.StringField(max_length=120)
  aws_secret_key = db.StringField(max_length=120)
  credentials = db.StringField(max_length=5000)
  project_id = db.StringField(max_length=5000)
  bucket_type = db.StringField(required=True, max_length=20, choices=BUCKET_TYPE)
  created_at = db.DateTimeField(default=datetime.now())
  updated_at = db.DateTimeField(default=datetime.now())

class TransferJob(db.Document):
  name = db.StringField(required=True)
  project_id = db.StringField(required=True)
  success = db.BooleanField(default=False)
  files = db.ListField(db.StringField())
  source = db.ReferenceField(Bucket)
  sink = db.ReferenceField(Bucket)
  schedule = db.DateTimeField(required=True)
  type = db.StringField(required=True, max_length=20, choices=TRANSFER_TYPE)
  created_at = db.DateTimeField(default=datetime.now())
  updated_at = db.DateTimeField(default=datetime.now())

# Utilities functions
def can_delete(bucket):
  return TransferJob.objects(Q(source=bucket) | Q(sink=bucket)).count() == 0

def make_aws_request(source, sink, project_id, files, schedule_time):
  now = schedule_time
  description = f'{source.name}_{now.day}_{now.month}_{now.year}'
  transfer_job = {
    'description': description,
    'status': 'ENABLED',
    'projectId': project_id,
    'schedule': {
      'scheduleStartDate': {
        'day': now.day,
        'month': now.month,
        'year': now.year
      },
      'scheduleEndDate': {
        'day': now.day,
        'month': now.month,
        'year': now.year
      },
      'startTimeOfDay': {
        'hours': now.hour,
        'minutes': now.minute,
        'seconds': now.second
      }
    },
    'transferSpec': {
      'objectConditions': {
        'includePrefixes': files,
      },
      'awsS3DataSource': {
        'bucketName': source.name,
        'awsAccessKey': {
          'accessKeyId': source.aws_access_key,
          'secretAccessKey': source.aws_secret_key
        }
      },
      'gcsDataSink': {
        'bucketName': sink.name
      }
    }
  }
  return transfer_job

def make_google_request(source, sink, project_id, files, schedule_time):
  now = schedule_time
  description = f'{source.name}_{now.day}_{now.month}_{now.year}'
  transfer_job = {
    'description': description,
    'status': 'ENABLED',
    'projectId': project_id,
    'schedule': {
      'scheduleStartDate': {
        'day': now.day,
        'month': now.month,
        'year': now.year
      },
      'scheduleEndDate': {
        'day': now.day,
        'month': now.month,
        'year': now.year
      },
      'startTimeOfDay': {
        'hours': now.hour,
        'minutes': now.minute,
        'seconds': now.second
      }
    },
    'transferSpec': {
      'objectConditions': {
        'includePrefixes': files,
      },
      'gcsDataSource': {
        'bucketName': source.name
      },
      'gcsDataSink': {
        'bucketName': sink.name
      }
    }
  }
  return transfer_job

def upload_to_google(files, sink_bucket, transfer_job):
  try:
    credential_file_path = os.path.abspath(f'sink_credential_{sink_bucket.name}.json')
    credential_file = open(credential_file_path, 'w')
    credential_file.write(sink_bucket.credentials)
    credential_file.close()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_file_path
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    client = storage.Client()
    bucket = client.get_bucket(sink_bucket.name)
    for file in files:
      filename = file.split('/')[-1]
      blob = bucket.blob(filename)
      blob.upload_from_filename(filename=file)
      os.remove(file)
    os.remove(credential_file_path)
    transfer_job.success = True
    transfer_job.save()
  except:
    error = sys.exc_info()
    e = error[0]
    traceback = error[2]
    print(f'error => {e}; {traceback}')
    transfer_job.success = False
    transfer_job.save()
    # print(traceback)

def start_transfer(source, sink, files):
    now = datetime.now(timezone.utc) + timedelta(minutes = 1)
    tj = TransferJob(
      project_id=sink.project_id,
      files=files,
      source=source,
      sink=sink,
      schedule=now,
      type=('S3' if sink.bucket_type == 'Amazon S3' else 'GCS')
    )
    try:
      credential_file_path = f'sink_credential_{sink.name}.json'
      credential_file = open(credential_file_path, 'w')
      credential_file.write(sink.credentials)
      credential_file.close()
      os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(credential_file_path)
      # print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
      storagetransfer = googleapiclient.discovery.build('storagetransfer', 'v1', cache_discovery=False)
      print('before making transfer')
      transfer_job = make_aws_request(source, sink, sink.project_id, files, now) if source.bucket_type == 'Amazon S3' else make_google_request(source, sink, sink.project_id, files, now)
      result = storagetransfer.transferJobs().create(body=transfer_job).execute()
      tj.name = result['name']
      tj.success = True
      return tj.save()
    except:
      e = sys.exc_info()[0]
      print(f'error => {e}')
      tj.success = False
      return tj.save()

def s3_files(bucket):
  session = Session(aws_access_key_id=bucket.aws_access_key, aws_secret_access_key=bucket.aws_secret_key)
  s3 = session.resource('s3')
  my_bucket = s3.Bucket(bucket.name)
  summaries = my_bucket.objects.all()
  files = list(map(lambda s: {
    'name': s.key,
    'size': s3.Object(bucket.name, s.key).content_length
  }, summaries))
  return files

def gcs_files(bucket):
  credential_file_path = f'sink_credential_{bucket.name}.json'
  credential_file = open(credential_file_path, 'w')
  credential_file.write(bucket.credentials)
  credential_file.close()
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(credential_file_path)
  print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
  client = storage.Client()
  bucket = client.get_bucket(bucket.name)
  return list(map(lambda x: {
    'name': x.name, 
    'size': x.size
  }, bucket.list_blobs()))


def get_files(bucket):
  if bucket.bucket_type == 'Amazon S3':
    return s3_files(bucket)
  else:
    return gcs_files(bucket)

# routes
@app.errorhandler(404)
def not_found(error):
  return make_response(jsonify({'error': 'Not found'}), 404)

# CRUD buckets
@app.route('/api/buckets', methods = ['GET'])
def get_buckets():
  buckets = Bucket.objects.all()
  response = list(
    map(
      lambda bucket: 
        {
          'id': str(bucket.id),
          'name': bucket.name, 
          'bucket_type': bucket.bucket_type, 
          'deletable': can_delete(bucket)
        }, buckets
      )
    )
  return jsonify({"buckets": response})

@app.route('/api/buckets', methods = ['POST'])
def create_bucket():
  if not request.json:
    abort(404)
  bucket = Bucket(**request.json)
  bucket.save()
  return jsonify({"bucket": bucket}), 201

@app.route('/api/buckets/<bucket_id>', methods=['DELETE'])
def delete_bucket(bucket_id):
  try:
    bucket = Bucket.objects.get(id=bucket_id)
    bucket.delete()
    return '', 204
  except:
    return not_found()

@app.route('/api/buckets/<bucket_id>/files', methods=['GET'])
def get_bucket_files(bucket_id):
  bucket = Bucket.objects.get(id=bucket_id)
  print(bucket)
  files = get_files(bucket)
  response = {'files': files}
  return jsonify(response)

@app.route('/api/transfers', methods=['GET'])
def get_transfers():
  tjs = TransferJob.objects.all()
  response = list(
    map(
      lambda tj: 
        {
          'id': str(tj.id),
          'name': tj.name, 
          'success': tj.success, 
          'sink': (None if tj.sink is None else tj.sink.name),
          'source': (None if tj.sink is None else tj.sink.name),
          'createdAt': datetime.timestamp(tj.created_at)
        }, tjs
      )
    )
  return jsonify({"transfers": response})

@app.route('/api/transfers', methods=['POST'])
def transfer_bucket():
  params = request.json
  source_id = params['sourceId']
  sink_id = params['sinkId']
  files = params['files']
  transfer_job.delay(source_id, sink_id, files)
  return jsonify({"success": True})

@app.route('/api/transfers/<transfer_id>/status', methods=['GET'])
def get_transfer_status(transfer_id):
  tj = TransferJob.objects.get(id=transfer_id)
  if tj.type == 'LOCAL':
    return jsonify({'status': None})
  else:
    credential_file_path = f'sink_credential_{tj.sink.name}.json'
    credential_file = open(credential_file_path, 'w')
    credential_file.write(tj.sink.credentials)
    credential_file.close()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(credential_file_path)
    storagetransfer = googleapiclient.discovery.build('storagetransfer', 'v1')
    filterString = (
      '{{"project_id": "{project_id}", '
          '"job_names": ["{job_name}"]}}'
    ).format(project_id=tj.sink.project_id, job_name=tj.name)

    result = storagetransfer.transferOperations().list(
      name="transferOperations",
      filter=filterString
    ).execute()
    return jsonify(result)

@app.route('/api/upload', methods=['POST'])
def upload_file():
  bucket_id = request.form['bucket_id']
  file_list = []
  if 'files' in request.files :
    files = request.files.getlist('files')
    for file in files:
      filename = secure_filename(file.filename)
      name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      file.save(name)
      file_list.append(name)
    local_file_upload.delay(bucket_id, file_list)
    return jsonify({'success': True})
  else:
    return jsonify({'error': True}), 500



@app.errorhandler(404)
def not_found(error=None):
  message = {
    'status': 404,
    'message': 'Not Found: ' + request.url,
  }
  resp = jsonify(message)
  resp.status_code = 404

  return resp
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@htpasswd.required
def catch_all(path, user):
  # if app.debug:
  #   return requests.get('http://localhost:8080/{}'.format(path)).text
  # else:
  return render_template('index.html')

@celery.task
# @route.add('/queues/upload', methods=['POST'])
def local_file_upload(bucket_id, files):
  bucket = Bucket.objects.get(id=bucket_id)
  timestamp = datetime.timestamp(datetime.now())
  tj = TransferJob(
    name=f'local_{timestamp}',
    project_id='none',
    files=files,
    sink=bucket,
    schedule=datetime.now(),
    type='LOCAL'
  )
  # new_pid = os.fork()
  # if new_pid == 0:
  upload_to_google(files, bucket, tj)
  # os.waitpid(new_pid,0)
  return True

@celery.task
# @app.route('/queues/transfer', methods=['POST'])
def transfer_job(source_id, sink_id, files):
  # new_pid = os.fork()
  # if new_pid == 0:
  source = Bucket.objects(id=source_id).first()
  sink = Bucket.objects(id=sink_id).first()
  start_transfer(source, sink, files)
  # os.waitpid(new_pid,0)
  return True

  if __name__ == "__main__":
    app.run(host='0.0.0.0')