import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import os
import  datetime
import time
import re
import urllib.parse
from opencc import OpenCC
import pandas as pd


tstart = time.time()#####計時開始

##設定簡體轉繁體##
cc = OpenCC('s2t')
##設定現在時間##
today = datetime.date.today() ; today = ''.join(str(today).split('-'))
now_time = time.strftime("%H", time.localtime())
now_time = today + ' ' + str(now_time)
print(now_time)

### 設定dataframe,後頭開始存資料
dflist = pd.DataFrame()
##建立new_data目錄
new_dict = r'./new_dict'
if not os.path.exists(new_dict): #若目錄不存在則新增一個
    os.mkdir(new_dict)

#=== 讀取0_100youtuber csv檔 並進入第一頁
df_all = pd.read_csv("youtubeChannelID111.csv")
channel_id = list(df_all['channelID'])[0:100]
print(channel_id)
channel_youtuber = list(df_all['channelName'])[0:100]
add_count = 1
###定義函式save_new 取兩周內資料並儲存
def save_new(video_ID,channel_id, channel_of_youtuber, video_title,add_count, view_count):
    data_new = pd.DataFrame(  # 用pandas轉成dataframe
        data=[{ 'video_id': video_ID,
               'channel_id': channel_id,
               'channel_of_youtuber': channel_of_youtuber,
               'video_title': video_title,
                'add_count': add_count,
                now_time:  view_count}],
        columns=['video_id', 'channel_id', 'channel_of_youtuber', 'video_title','add_count', now_time]
    )
    return data_new
for i,each in enumerate(channel_id):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
    try:
        url = 'https://www.youtube.com/channel/{}/videos?view=0&sort=dd&shelf_id=0'.format(each)  # 某頻道的播放清單網址
        html = requests.get(url, headers=headers)
        if str(html) == '<Response [404]>':
            print('該頻道的網址寫作', 'https://www.youtube.com/user/' + each + '/videos')
            url = 'https://www.youtube.com/channel/{}/videos'.format(each)
            html = requests.get(url, headers=headers)
        response = BeautifulSoup(html.text, 'html.parser')
        a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
        data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
        data_str = '{' + data_str.split('= {')[1].split('}]}}};')[0] + '}]}}}'  # 處理成完整的json格是再做json.loads
    except IndexError:
        url = 'https://www.youtube.com/channel/{}/videos'.format(each)  # 某頻道的播放清單網址
        html = requests.get(url, headers=headers)
        if str(html) == '<Response [404]>':
            print('該頻道的網址寫作', 'https://www.youtube.com/user/' + each + '/videos')
            url = 'https://www.youtube.com/channel/{}/videos'.format(each)
            html = requests.get(url, headers=headers)
        response = BeautifulSoup(html.text, 'html.parser')
        a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
        data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
        data_str = '{' + data_str.split('= {')[1].split('}]}}};')[0] + '}]}}}'  # 處理成完整的json格是再做json.loads
    data_dict = json.loads(data_str)

    # === 取進入下一頁的參數
    set_dict = data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']
    try:
        continuation = set_dict['continuations'][0]['nextContinuationData']['continuation']
    except Exception:
        continuation = ''
    count = 1
    # 開始取值
    set = set_dict['items']
    for item in set:
        try:
            video_id = item['gridVideoRenderer']['videoId']
            video_time = item['gridVideoRenderer']['publishedTimeText']['simpleText']
            title = item['gridVideoRenderer']['title']['simpleText']
            view_count = ''.join(item['gridVideoRenderer']['viewCountText']['simpleText'].split('：')[-1].split('次')[0].split(','))
            add_count = 1  # 計次使用
            print(count, title, ' ', video_id, ' ', video_time, ' ', view_count)
            count += 1
        except KeyError:
            pass
        try:
            video_time = int(video_time.split('分鐘前')[0])
            if video_time < 60:
                data_new = save_new(video_id, channel_id[i], channel_youtuber[i], title, add_count, view_count)
                dflist = dflist.append(data_new, ignore_index=True)  # 將檔案存檔
        except Exception:
            try:
                video_time = int(video_time.split('小時前')[0])
                if video_time < 24:
                    data_new = save_new(video_id, channel_id[i], channel_youtuber[i], title, add_count, view_count)
                    dflist = dflist.append(data_new, ignore_index=True)  # 將檔案存檔
            except Exception:
                pass
    print('==============================')
# new_data存成csv檔
print(dflist)
dflist.to_csv(r'./new_dict/new_data_%s.csv' % (now_time), index=False, encoding='utf-8-sig')
dflist.to_csv(r'./new_dict/new_data{}.csv'.format(''), index=0, encoding='utf-8-sig')

