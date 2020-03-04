import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import os
import time
import lxml.html
### 該程式主旨: 已知一頻道的channel_ID，進到它的播放清單頁面中，從JSON資訊中取得所有播放清單的playlistId
### 注意:若播放清單的頁面不是只有已建立的清單，如:https://www.youtube.com/user/kyoko38/playlists菜啊嘎的播放清單還包含其他儲存的清單等，json寫法不同

#header
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

#輸入某頻道的channel_id
channel_id = 'newscloudworld'  #可測試的channel_id: jasonjason1124; kyoko38; MARIOFREAK821; eravideo004; kenpmges; newscloudworld; RockRecordsTaipei
#for https://www.youtube.com/channel/{channel_id}/playlists;可測試的channel_id: UCpGGLFkG4heKm6hnJYn5HxA; UCDrswN-SqWh7Kii62h9aXGA

# 某頻道的播放清單網址 (jasonjason1124 是 howhow)
url = 'https://www.youtube.com/user/{}/playlists'.format(channel_id)
#=== get web response
#注意: 有的頻道網址寫作https://www.youtube.com/channel/{channel_id}/playlists，非https://www.youtube.com/user/{channel_id}/playlists
#似乎較舊的頻道是https://www.youtube.com/user/{channel_id}/playlists，較新的頻道都寫成channel/{channel_id}/playlists
html = requests.get(url,headers=headers)
if str(html) == '<Response [404]>':
    print('該頻道的網址寫作 https://www.youtube.com/channel/{channel_id}/playlists')
    url = 'https://www.youtube.com/channel/{}/playlists'.format(channel_id)
    html = requests.get(url,headers=headers)

response = BeautifulSoup(html.text,'html.parser')
a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔

#處理成完整的json格是再做json.loads
data_str = '{' + data_str.split('= {')[1].split('}]}}};')[0] + '}]}}}'
#print(data_str)
data_dict = json.loads(data_str)

#data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][2]['tabRenderer']['content']['sectionListRenderer']['contents'][0] ###需要注意這邊的list元素量是否會大於1個，
#該頻道若為多個清單總表，存放列表(list)的數量就會大於1，並且，json中的key值也不同，
#只有一個播放清單總表: ...['itemSectionRenderer']['contents'][0]['gridRenderer']['items']...
#多個播放清單總表: ...['itemSectionRenderer']['contents'][0]['shelfRenderer']...

n_list_count = len(data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][2]['tabRenderer']['content']['sectionListRenderer']['contents'])

if n_list_count == 1: #該頻道只有1個播放清單總表
    set_a = data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][2]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
    count = 1
    print('播放清單總表名: {}'.format(data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][2]['tabRenderer']['content']['sectionListRenderer']['subMenu']['channelSubMenuRenderer']['contentTypeSubMenuItems'][0]['title']))
    for item in set_a:
        print('playlist #{}'.format(count));
        count += 1
        print('playlist_ID:', item['gridPlaylistRenderer']['playlistId'])  # 查看完整清單的網址: 'https://www.youtube.com/playlist?list=' + playlistId
        print('playlist_title:', item['gridPlaylistRenderer']['title']['runs'][0]['text'])
        print('videoCount in this playlist:', item['gridPlaylistRenderer']['videoCountText']['runs'][0]['text'])

else: #該頻道有1個以上的播放清單總表
    set_a_list = data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][2]['tabRenderer']['content']['sectionListRenderer']['contents']
    for set_a in set_a_list:
        print('播放清單總表名: {}'.format(set_a['itemSectionRenderer']['contents'][0]['shelfRenderer']['title']['runs'][0]['text']))
        count = 1
        set_b = set_a['itemSectionRenderer']['contents'][0]['shelfRenderer']['content']['horizontalListRenderer']['items']
        for item in set_b:
            print('playlist #{}'.format(count));count += 1
            print('playlist_ID:', item['gridPlaylistRenderer']['playlistId'])  # 查看完整清單的網址: 'https://www.youtube.com/playlist?list=' + playlistId
            print('playlist_title:', item['gridPlaylistRenderer']['title']['runs'][0]['text'])
            print('videoCount in this playlist:', item['gridPlaylistRenderer']['videoCountText']['runs'][0]['text'])
        print('====================================================================================================')
        print('\n')
