import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import os
import time
import lxml.html
###本程式主旨: 到發燒影片頁面中，從JSON資訊中取得影片資訊
###發燒影片get到的資訊(約7x多個)不需要翻頁，但注意資訊被分在兩個List中

# 發燒影片網址
url="https://www.youtube.com/feed/trending"
#header
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
#get web response
html = requests.get(url,headers=headers)
response = BeautifulSoup(html.text,'html.parser')
a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
#print(data_str.split('= {')[1].split(']}}}}}}};')[0])

#處理成完整的json格是再做json.loads
data_str = '{' + data_str.split('= {')[1].split(']}}}}}}};')[0] + ']}}}}}}}'
data_dict = json.loads(data_str)

#===找到session_token
target = 'XSRF_TOKEN'
start = a[8].text.find(target) + len(target) + len('":"') #str.find('target',start index)可找出對應的足st = b[8].text.find('XSRF_TOKEN')
end = a[8].text.find('"',start)
session_token = a[8].text[start:end]
print(session_token)

#開始取資料
#=== 注意! data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents']下的List會含有內容(似乎一個頁面至多2個元素，一個元素中最多存50項影片資訊)，需用for迴圈遍歷此List

n_section = len(data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'])

count = 1
for i in range(n_section):
    print('section: {} \n'.format(i+1))
    set_a = data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][i]['itemSectionRenderer']['contents'][0]['shelfRenderer']['content']['expandedShelfContentsRenderer']['items']
    #目前set_a含有多個(猜測至多50個)影片
    set_a[0]['videoRenderer']

    for item in set_a:
        print('video #{}'.format(count)); count += 1
        print('video_title:',item['videoRenderer']['title']['runs'][0]['text'])
        print('video_id:',item['videoRenderer']['videoId']) #'https://www.youtube.com/watch?v='+ vedio_id
        print('video_length:',item['videoRenderer']['lengthText']['simpleText'])
        print('view_count:',item['videoRenderer']['viewCountText']['simpleText'])
        print('publishedTime:',item['videoRenderer']['publishedTimeText']['simpleText'])
        print('channel_name:',item['videoRenderer']['ownerText']['runs'][0]['text'])
        print('channel_id:',item['videoRenderer']['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'])#'https://www.youtube.com/channel/' + channel_id
        print('====================================================================================')