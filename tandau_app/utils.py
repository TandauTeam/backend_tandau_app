# utils.py
import json
from collections import defaultdict
from .models import *
import requests
from urllib.parse import urlparse, parse_qs
from datetime import timedelta
from django.conf import settings
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

url = os.environ["URL_PROD"]

def calculate_max_percentage(responses):
    answer_sum_per_type = defaultdict(int)

    for response in responses:
        person_type = response.get('person_type')
        person_answer = response.get('person_answer')
        answer_sum_per_type[person_type] += person_answer

    max_percentage = -1
    max_person_type = None
    for person_type, answer_sum in answer_sum_per_type.items():
        percentage = (answer_sum / 5 * 10) * 100
        if percentage > max_percentage:
            max_percentage = percentage
            max_person_type = person_type

    return max_person_type

def update_user_person_type(user_id, max_person_type):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.person_type = max_person_type
        user.save()
        return True, user
    except CustomUser.DoesNotExist:
        return False, None

def load_person_info(max_person_type):
    with open('tandau_app/location/person_types.json', 'r') as f:
        json_data = json.load(f)

    for data in json_data:
        if max_person_type in data:
            return data[max_person_type]

    return None

def get_youtube_video(request):
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    last_day = datetime.now() - timedelta(days=64)
    new_videos = Video.objects.filter(timestamp__gte=last_day).order_by('-timestamp')[:4]

    # If there are no new videos in the last day, fallback to videos shown 1 week ago
    if not new_videos:
        last_week = datetime.now() - timedelta(weeks=1)
        new_videos = Video.objects.filter(timestamp__gte=last_week).order_by('-timestamp')[:4]
    
    list_show = []
    for i in new_videos:
        ids = extract_video_id(i.youtube_link)
        # print(ids)
        list_show.append(ids)

    video_list = []
    for video in list_show:
        video_url = f'https://www.youtube.com/watch?v={video[0]}'
        video_data = get_video_data(video, youtube_api_key)
        if video_data:
            video_list.append(
                {'title': video_data['title'], 
                 'description': video_data['description'],
                 'thumbnails': video_data['thumbnails'],
                 'url': video_url})
    
    return video_list


def get_youtube_video_total(request):
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    last_day = datetime.now() - timedelta(days=7)
    new_videos = Video.objects.filter(timestamp__gte=last_day).order_by('-timestamp')

    # If there are no new videos in the last day, fallback to videos shown 1 week ago
    if not new_videos:
        last_week = datetime.now() - timedelta(weeks=2)
        new_videos = Video.objects.filter(timestamp__gte=last_week).order_by('-timestamp')
    
    list_show = []
    for i in new_videos:
        ids = extract_video_id(i.youtube_link)
        # print(ids)
        list_show.append(ids)

    video_list = []
    for video in list_show:
        video_url = f'https://www.youtube.com/watch?v={video[0]}'
        video_data = get_video_data(video, youtube_api_key)
        if video_data:
            video_list.append(
                {'title': video_data['title'], 
                 'description': video_data['description'],
                 'thumbnails': video_data['thumbnails'],
                 'url': video_url})
    
    return video_list

def generate_response_data(person_info):
    title_name = person_info['title_name']
    description = person_info['description']
    image = person_info['image']
    image =  f"{url}/{image}"
    list_info = person_info['list_info']
    profession_list = person_info['profession_list']
    for item in list_info:
        if "image" in item:
            item["image"] = f"{url}/{item['image']}"

    response_data = {
        "title_name": title_name,
        "description": description,
        "image": image,
        "list_info": list_info,
        "profession_list": profession_list
    }

    return response_data



def get_video_data(video_id, api_key):
    youtube_api_url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id[0]}&key={api_key}&part=snippet'
   
    response = requests.get(youtube_api_url)
    if response.status_code == 200:
        video_data = response.json()
        if 'items' in video_data and len(video_data['items']) > 0:
            return video_data['items'][0]['snippet']
    return None

def extract_video_id(video_url):
    parsed_url = urlparse(video_url)
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get('v')
    if video_id:
        return video_id
    else:
        return None