from googleapiclient.discovery import build
import pandas as pd

API_KEY = 'AIzaSyBwmm2uzFNzGAhp6pN1LDtlXKVjzauiyUw'
api_service_name = "youtube"
api_version = "v3"
youtube = build(api_service_name, api_version, developerKey=API_KEY)


def getChannels(name):
  channels = []
  if not name:
    return channels
  request = youtube.search().list(
      part="snippet",
      maxResults=5,
      q=name,
      type="channel"
  )
  response = request.execute()
  for item in response.get('items'):
    channel = {}
    channel['channelId'] = item['snippet']['channelId']
    channel['channelTitle'] = item['snippet']['channelTitle']
    channels.append(channel)

  return channels


def getVideoIds(playlistId):
  request = youtube.playlistItems().list(
      part="contentDetails",
      playlistId=playlistId,
      maxResults=50
  )
  response = request.execute()
  video_ids = []
  for i in range(len(response.get('items'))):
    video_ids.append(response.get('items')[i]["contentDetails"]['videoId'])
  next_page_token = response.get('nextPageToken')
  while next_page_token != None:
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId=playlistId,
        maxResults=50,
        pageToken=next_page_token)
    response = request.execute()
    for i in range(len(response.get('items'))):
      video_ids.append(response.get('items')[
                       i]["contentDetails"]['videoId'])
    next_page_token = response.get('nextPageToken')

  return video_ids


def getVideoDetails(videoIds):
  videoDetails = []
  for i in range(0, len(videoIds), 50):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=','.join(videoIds[i:i+50]))
    response = request.execute()
    for video in response['items']:
      videoStats = dict(title=video['snippet']['title'],
                        id=video['id'],
                        published=video['snippet']['publishedAt'],
                        views=video['statistics'].get('viewCount', 0),
                        likes=video['statistics'].get('likeCount', 0),
                        comments=video['statistics'].get(
          'commentCount', 0)
      )
      videoDetails.append(videoStats)

  return videoDetails


def getChannelDetails(id):
  request = youtube.channels().list(
      part="snippet,contentDetails,statistics",
      id=id
  )
  response = request.execute()
  item = response['items'][0]
  data = dict(channelTitle=item['snippet']['title'],
              channelId=response['items'][0]['id'],
              channelDescription=item['snippet']['description'],
              customUrl=item['snippet']['customUrl'],
              thumbnail=item['snippet']['thumbnails']['medium']['url'],
              viewCount=int(item['statistics']['viewCount']),
              subscriberCount=int(item['statistics']['subscriberCount']),
              videoCount=int(item['statistics']['videoCount']),
              playlistId=response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
  videoIds = getVideoIds(data['playlistId'])
  videoDetails = getVideoDetails(videoIds)
  df = pd.DataFrame(videoDetails)
  df['views'] = pd.to_numeric(df['views'])
  df['comments'] = pd.to_numeric(df['comments'])
  df['likes'] = pd.to_numeric(df['likes'])

  df_sorted = df.sort_values(by='views', ascending=False)
  data['maxViews'] = int(df['views'].max())
  data['maxComments'] = int(df['comments'].max())
  data['maxLikes'] = int(df['likes'].max())

  sorted_videoDetails = df_sorted.to_dict(orient='records')
  data['videoDetails'] = sorted_videoDetails
  return data


def getRawComments(videoId):
  comments = []
  response = youtube.commentThreads().list(
      part='snippet',
      videoId=videoId,
      textFormat='plainText',
      maxResults=100
  ).execute()
  next_page_token = response.get('nextPageToken')
  if not response['items']:
    print(f"Comments are disabled for video with ID: {
        videoId}. Skipping...")
    return comments
  for i in range(len(response.get('items'))):
    comments.append(response.get('items')[
                    i]['snippet']['topLevelComment']['snippet']['textDisplay'])
  while next_page_token != None and len(comments) <= 1000:
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=videoId,
        textFormat='plainText',
        maxResults=3,
        pageToken=next_page_token
    ).execute()

    for i in range(len(response.get('items'))):
      comments.append(response.get('items')[
          i]['snippet']['topLevelComment']['snippet']['textDisplay'])
    next_page_token = response.get('nextPageToken')

  return comments
