import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import os
import time
#import lxml.html
###該程式主旨: 已知某一影片的video_ID，進到它的頁面中，從JSON資訊中取得該影片資訊

# 輸入某影片的video_ID
viedo_id = 'JazII6CW-98'
url="https://www.youtube.com/watch?v=" + viedo_id #網址: 'https://www.youtube.com/watch?v=' + video_id

#header
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

#get web response
html = requests.get(url,headers=headers)
response = BeautifulSoup(html.text,'html.parser')

a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
#處理成完整的json格是再做json.loads
data_str = '{' + data_str.split('= {')[1].split('}};\n')[0] + '}}'
data_dict = json.loads(data_str)
#print(data_dict)

#===開始取資料
#該影片相關資訊
set_a = data_dict['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']

#該影片的頻道相關資訊
set_b = data_dict['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']

#列印結果
print('video_title: ',set_a['title']['runs'][0]['text'])
print('video_view_count: ',set_a['viewCount']['videoViewCountRenderer']['viewCount']['simpleText'])
print('video_post_date: ',set_a['dateText']['simpleText'])
print('video_like_count: ',set_a['videoActions']['menuRenderer']['topLevelButtons'][0]['toggleButtonRenderer']['defaultText']['simpleText'])
print('video_dislike_count: ',set_a['videoActions']['menuRenderer']['topLevelButtons'][1]['toggleButtonRenderer']['defaultText']['simpleText'])
print('channel of video: ', set_b['title']['runs'][0]['text'])
print('channel_id of video: ', set_b['title']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'])