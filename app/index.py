from flask import Flask, jsonify
from flask_cors import CORS
from app.yt import getChannels, getChannelDetails, getRawComments
from app.tasks import background_task, celery, redis_client
import celery.states as states
import json


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
  cached_result = redis_client.get(videoId)
  if cached_result:
    print(f'Returning cached result for videoId {videoId} ...')
    return jsonify(json.loads(cached_result))
  comments = getRawComments(videoId)
  if isinstance(comments, dict) and comments.get('error'):
    return jsonify(comments.get('message', {'message': 'Error occurred'}))
  print(f'Collected comments from API for videoId {videoId} ...')
  task = background_task.delay(comments, videoId)
  print(f'Sending response for videoId {videoId} ...')
  return jsonify({'id': task.id})


@app.route('/check/<string:task_id>')
def get_result(task_id):
  res = celery.AsyncResult(task_id)
  if res.state == states.PENDING:
    return res.state
  else:
    return jsonify(res.result)
