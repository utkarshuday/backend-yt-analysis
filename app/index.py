from flask import Flask, jsonify
from flask_cors import CORS
from app.yt import getChannels, getChannelDetails, getRawComments
from app.tasks import background_task, celery, redis_client
from app.errors import YouTubeQuotaExceededError, APIRequestError
import celery.states as states
import json


app = Flask(__name__)
CORS(app)


@app.errorhandler(YouTubeQuotaExceededError)
def handle_youtube_quota_exceeded_error(error):
  response = jsonify({
      "error": "YouTube API quota has been exceeded",
      "message": str(error)
  })
  response.status_code = 429
  return response


@app.errorhandler(APIRequestError)
def handle_api_request_error(error):
  response = jsonify({
      "error": "Youtube Data API request failed",
      "message": str(error)
  })
  response.status_code = 500
  return response


@app.errorhandler(Exception)
def handle_generic_error(error):
  response = jsonify({
      "error": "An unexpected error occurred",
      "message": str(error)
  })
  response.status_code = 500
  return response


@app.route('/')
def get_home_page():
  return '<h1>Youtube Analysis</h1>'


@app.route("/channels/<string:name>")
def get_searched_channel(name):
  try:
    channels = getChannels(name)
    return jsonify(channels)
  except:
    raise


@app.route("/channel-details/<string:id>")
def get_channel_details(id):
  try:
    details = getChannelDetails(id)
    return jsonify(details)
  except:
    raise


@app.route('/sentiments/<string:videoId>')
def get_sentiment_analysis(videoId):
  try:
    print(f'Started process for videoId {videoId} ...')
    cached_result = redis_client.get(videoId)
    if cached_result:
      print(f'Returning cached result for videoId {videoId} ...')
      return jsonify(json.loads(cached_result))
    comments = getRawComments(videoId)
    print(f'Collected comments from API for videoId {videoId} ...')
    task = background_task.delay(comments, videoId)
    print(f'Sending response for videoId {videoId} ...')
    return jsonify({'id': task.id})
  except:
    raise


@app.route('/check/<string:task_id>')
def get_result(task_id):
  try:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
      return res.state
    else:
      return jsonify(res.result)
  except:
    raise
