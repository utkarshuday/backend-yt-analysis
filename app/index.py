from flask import Flask, jsonify
from flask_cors import CORS
from app.yt import getChannels, getChannelDetails, getRawComments
from app.sentiments import getSentimentScores

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
  print(f'Collected comments from API for videoId {videoId} ...')
  result = getSentimentScores(comments, videoId)
  print(f'Sending response for videoId {videoId} ...')
  return jsonify(result)
