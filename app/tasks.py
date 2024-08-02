from celery import Celery
from app.sentiments import getSentimentScores
import redis
import json

celery = Celery('tasks', backend='redis://localhost:6379',
                broker='redis://localhost:6379', result_expires=60 * 60 * 16)
redis_client = redis.StrictRedis(
    host='localhost', port=6379, db=0, decode_responses=True)


@celery.task
def background_task(comments, videoId):
  result = getSentimentScores(comments, videoId)
  redis_client.set(videoId, json.dumps(result), ex=60 * 60 * 16)
  return result
