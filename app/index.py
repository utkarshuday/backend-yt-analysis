from flask import Flask, jsonify
from flask_cors import CORS
from app.yt import getChannels, getChannelDetails, getRawComments
from celery import Celery
import celery.states as states
import os

host = os.environ['UPSTASH_REDIS_HOST']
password = os.environ['UPSTASH_REDIS_PASSWORD']
port = os.environ['UPSTASH_REDIS_PORT']
connection_link = "rediss://:{}@{}:{}?ssl_cert_reqs=CERT_REQUIRED".format(
    password, host, port)

celery = Celery('tasks', backend='redis://localhost:6379',
                broker='redis://localhost:6379', result_expires=60 * 60 * 16)

app = Flask(__name__)
CORS(app)


@app.route('/')
def get_home_page():
  return '<h1>Youtube Analysis</h1>'


@app.route("/channels/<string:name>")
def get_searched_channel(name):
  channels = getChannels(name)
  return jsonify(channels)


@app.route("/channel-details/<string:id>")
def get_channel_details(id):
  details = getChannelDetails(id)
  return jsonify(details)


@app.route('/sentiments/<string:videoId>')
def get_sentiment_analysis(videoId):
  print(f'Started process for videoId {videoId} ...')
  comments = getRawComments(videoId)
  if isinstance(comments, dict) and comments.get('error'):
    return jsonify(comments.get('message', {'message': 'Error occurred'}))
  print(f'Collected comments from API for videoId {videoId} ...')
  task = celery.send_task('tasks.sentiment_scores', args=[comments, videoId])
  print(f'Sending response for videoId {videoId} ...')
  return jsonify({'id': task.id})


@app.route('/check/<string:task_id>')
def get_result(task_id):
  res = celery.AsyncResult(task_id)
  if res.state == states.PENDING:
    return res.state
  else:
    return jsonify(res.result)
