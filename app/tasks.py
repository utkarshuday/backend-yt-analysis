import os
from celery import Celery
from app.sentiments import getSentimentScores
import redis
import json

host = os.environ['UPSTASH_REDIS_HOST']
password = os.environ['UPSTASH_REDIS_PASSWORD']
port = os.environ['UPSTASH_REDIS_PORT']
connection_link = "rediss://:{}@{}:{}?ssl_cert_reqs=CERT_REQUIRED".format(
    password, host, port)

celery = Celery('tasks', backend='redis://localhost:6379',
                broker='redis://localhost:6379', result_expires=60 * 60 * 16)
redis_client = redis.StrictRedis(
    host='localhost', port=6379, db=0, decode_responses=True)

# celery = Celery('tasks', backend=connection_link,
#                 broker=connection_link, result_expires=60 * 60 * 16)
# redis_client = redis.StrictRedis(
#     host=host, port=port, password=password, ssl=True, decode_responses=True)


@celery.task
def background_task(comments, videoId):
  result = getSentimentScores(comments, videoId)
  redis_client.set(videoId, json.dumps(result), ex=60 * 60 * 16)
  return result
