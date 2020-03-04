import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import os
import time
# import lxml.html
import re
import urllib.parse
from opencc import OpenCC
import pandas as pd

### 本程式不使用selenium
### 本程式使用已知的channel_id，進入頻道的'影片'頁面，直接抓取網頁的JSON資訊，找到進入下一頁的參數達到往下滑動頁面的動作(進入下頁等同將網頁往下滑)
### 進入下頁後再取一次JSON的資訊(影片資訊與再進入下一頁的參數)

#=== 進入第一頁
channel_id = 'UCxUzQ3wu0oJP_8YLWt71WgQ' #UCPcF3KTqhD67ADkukx_OeDg'  #UCxUzQ3wu0oJP_8YLWt71WgQ

#注意header帶入的參數
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
url = 'https://www.youtube.com/channel/{}/videos'.format(channel_id)

html_main = requests.get(url,headers=headers)

response_main = BeautifulSoup(html_main.text,'html.parser')
main = response_main.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
data_str = str(main[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
data_str = '{' + data_str.split('= {')[1].split('}};\n')[0] + '}}'
data_dict = json.loads(data_str)

#=== 取進入下一頁的參數
set_dict = data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']
continuation = set_dict['continuations'][0]['nextContinuationData']['continuation']

count = 1

#設定dataframe,後頭開始存資料
data_con = pd.DataFrame(columns=['channel_id','video_title','video_id','view_count'])
###設定簡體轉繁體方法
cc = OpenCC('s2t')  # convert from Simplified Chinese to Traditional Chinese

#開始取值
set = set_dict['items']
for item in set:
    video_id = item['gridVideoRenderer']['videoId']
    title = item['gridVideoRenderer']['title']['simpleText']
    view_count = item['gridVideoRenderer']['viewCountText']['simpleText'].split('：')[-1]
    print(count, title, ' ', video_id, ' ', view_count)
    count += 1
    data_con = data_con.append({'channel_id': channel_id,'video_title': cc.convert(title),
                     'video_id': video_id,'view_count': view_count}, ignore_index=True)
print('==============================')

#continuation = '4qmFsgI0EhhVQ3hVelEzd3Uwb0pQXzhZTFd0NzFXZ1EaGEVnWjJhV1JsYjNNZ0FEZ0JlZ0V5dUFFQQ%3D%3D'

while continuation:
    #======== 進入第二頁之後
    url="https://www.youtube.com/browse_ajax?"   #AppleWebKit/537.36 (KHTML, like Gecko)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)  Chrome/79.0.3945.79 Safari/537.36', #特別設定的header
               "content-type": "application/x-www-form-urlencoded"}

    para = {'ctoken': continuation,
            'continuation': continuation}
            #'itct': 'CDIQybcCIhMIx5HpptOR5wIVxZnCCh0mTAlx'} #"search_query": "博恩夜夜"代表關鍵字是博恩夜夜 。"sp":"EgIQAQ%3D%3D" 代表此搜尋只找出影片
    html = requests.get(url,headers=headers,params=para)
    print(html)
    a = json.loads(str(html.text))
    #print(a.keys())

    #找下一頁的金鑰 (利用正則表達式)
    response_next= str(a['load_more_widget_html'])
    if not response_next: #沒有下一頁的情況，a['load_more_widget_html']會是空值，將continuation設成''，使翻頁的while跳脫
        continuation = ''
    else:
        continuation = str(re.findall(r';continuation=(.*?)"', response_next)[0])
        # 這邊取到continuation記得要做一次uncoding，否則下一頁進不去
        continuation = urllib.parse.unquote(continuation)
        print(continuation)
    #取該頁資料
    response = BeautifulSoup(a['content_html'],'html.parser')
    item_list = response.select('div.yt-lockup-content')
    item2_list = response.select('ul.yt-lockup-meta-info')


    for i in range(len(item_list)):
        title = item_list[i].h3.a.text
        video_id = item_list[i].h3.a['href'].split('v=')[-1]
        view_count = item2_list[i].li.text.split('：')[-1]
        print(count, title, ' ', video_id, ' ', view_count)
        count += 1
        data_con = data_con.append({'channel_id': channel_id, 'video_title': cc.convert(title),
                         'video_id': video_id, 'view_count': view_count}, ignore_index=True)
    print('==============================')
#存成csv檔
data_con.to_csv(r'./channel_allvideo_{}.csv'.format(channel_id), index=0, encoding='utf-8-sig')