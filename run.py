import os
import sys
import requests
from flask import Flask, render_template, jsonify, make_response, abort, request
from random import *
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from google.cloud import storage
from datetime import datetime,timedelta,timezone
import json
import googleapiclient.discovery

#Configuration
app = Flask(__name__, 
  static_folder = "./dist/static",
  template_folder = "./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['MONGODB_DB'] = 'bucket_uploader_test'
db = MongoEngine(app)

# models
BUCKET_TYPE = ('Amazon S3', 'Google Storage')
class Bucket(db.Document):
  name = db.StringField(required=True, max_length=120)
  aws_access_key = db.StringField(max_length=120)
  aws_secret_key = db.StringField(max_length=120)
  credentials = db.StringField(max_length=5000)
  bucket_type = db.StringField(required=True, max_length=20, choices=BUCKET_TYPE)

class TransferJob(db.Document):
  name: db.StringField(required=True)
  project_id = db.StringField(required=True)
  files = db.ListField(db.StringField())
  source = db.ReferenceField(Bucket)
  sink = db.ReferenceField(Bucket)
  schedule = db.DateTimeField(required=True)

# Utilities functions
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

def upload_to_google(files, sink_bucket):
  print(f'files are {files}')
  try:
    credential_file_path = f'sink_credential_{sink_bucket.name}.json'
    credential_file = open(credential_file_path, 'w')
    credential_file.write(sink_bucket.credentials)
    credential_file.close()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(credential_file_path)
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    client = storage.Client()
    bucket = client.get_bucket(sink_bucket.name)
    for file in files:
      filename = file.split('/')[-1]
      blob = bucket.blob(filename)
      blob.upload_from_filename(filename=file)
      # os.remove(file)
    os.remove(credential_file_path)
  except:
    error = sys.exc_info()
    e = error[0]
    traceback = error[2]
    print(f'error => {e}; {traceback}')
    # print(traceback)

def start_transfer(source, sink, project_id, files):
  # try:
    now = datetime.now(timezone.utc) + timedelta(minutes = 1)
    tj = TransferJob(
      project_id=project_id,
      files=files,
      source=source,
      sink=sink,
      schedule=now
    )
    credential_file_path = f'sink_credential_{sink.name}.json'
    credential_file = open(credential_file_path, 'w')
    credential_file.write(sink.credentials)
    credential_file.close()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(credential_file_path)
    # print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    storagetransfer = googleapiclient.discovery.build('storagetransfer', 'v1')
    print('before making transfer')
    transfer_job = make_aws_request(source, sink, project_id, files, now) if source.bucket_type == 'Amazon S3' else make_google_request(source, sink, project_id, files, now)
    result = storagetransfer.transferJobs().create(body=transfer_job).execute()
    tj.name = result['name']
    tj.save()
  # except:
  #   e = sys.exc_info()[0]
  #   print(f'error => {e}')


# routes
@app.errorhandler(404)
def not_found(error):
  return make_response(jsonify({'error': 'Not found'}), 404)

# CRUD buckets
@app.route('/api/buckets', methods = ['GET'])
def get_buckets():
  buckets = Bucket.objects.all()
  return jsonify({"buckets": buckets})

@app.route('/api/buckets', methods = ['POST'])
def create_bucket():
  if not request.json:
    abort(404)
  bucket = Bucket(request.json)
  bucket.save()
  return jsonify({"bucket": bucket}), 201

@app.route('/api/push')
def transfer():
  # if not request.json:
  #   abort(404)
  print("in transfer")
  try:
    bucket = Bucket.objects(bucket_type='Google Storage').first()
    files = ['/Users/yannakoun/Downloads/yann_pic.jpg', '/Users/yannakoun/Downloads/mac-screenshot.pkg']
    new_pid = os.fork()
    if new_pid == 0:
      upload_to_google(files=files, sink_bucket=bucket)
    os.waitpid(new_pid,0)
    response = {"success": True}
    return jsonify(response)
  except :
    e = sys.exc_info()[0]
    response = {"error": f'{e}'}
    return jsonify(response)

@app.route('/api/buckets/transfer')
def transfer_bucket():
  # params = request.json
  params = {
    "sourceId": "5d45ae82c24c29cd0231973e",
    "sinkId": "5d456eda09e4246e57e80446",
    "files": ["QPP Software Requirements.docx"],
    "project_id": "sitomobile" 
  }
  source_id = params['sourceId']
  sink_id = params['sinkId']
  source = Bucket.objects(id=source_id).first()
  sink = Bucket.objects(id=sink_id).first()
  files = params['files']
  project_id = params['project_id']
  # try:
    # new_pid = os.fork()
    # if new_pid == 0:
  start_transfer(source, sink, project_id, files)
    # os.waitpid(new_pid,0)
  return jsonify({"success": True})
  # except:
  #   error = sys.exc_info()
  #   e = error[0]
  #   traceback = error[2]
  #   print(f'error => {e}; {traceback}')
  #   response = {"error": f'{e}', "traceback": f'{traceback}'}
  #   return jsonify(response)

@app.route('/api/random')
def random_number():
  response = {
    "randomNumber": randint(1, 100)
  }
  return jsonify(response)

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#   if app.debug:
#     return requests.get('http://localhost:8080/{}'.format(path)).text
#   else:
#     return render_template('index.html')