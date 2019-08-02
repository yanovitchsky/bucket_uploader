from flask import Flask, render_template, jsonify, make_response, abort, request
from random import *
from flask_cors import CORS
import requests
from flask_mongoengine import MongoEngine

app = Flask(__name__,
  static_folder = "./dist/static",
  template_folder = "./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MONGODB_DB'] = 'bucket_uploader_test'

db = MongoEngine(app)

BUCKET_TYPE = ('Amazon S3', 'Google Storage')
class Bucket(db.Document):
  name = db.StringField(required=True, max_length=120)
  bucket_url = db.StringField(required=True, max_length=120)
  aws_access_key = db.StringField(max_length=120)
  aws_secret_key = db.StringField(max_length=120)
  credentials = db.StringField(max_length=500)
  bucket_type = db.StringField(required=True, max_length=20, choices=BUCKET_TYPE)

class TransferJob(db.Document):
  job_id: db.StringField(required=True)
  files = db.ListField(db.StringField())
  source = db.ReferenceField(Bucket)
  sink = db.ReferenceField(Bucket)


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

@app.route('/api/random')
def random_number():
  response = {
    "randomNumber": randint(1, 100)
  }
  return jsonify(response)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
  if app.debug:
    return requests.get('http://localhost:8080/{}'.format(path)).text
  else:
    return render_template('index.html')
