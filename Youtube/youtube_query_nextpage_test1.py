import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import os
import time
import lxml.html
### 本程式不使用selenium
### 本程式模擬在youtube的搜尋列中輸入一關鍵字，直接抓取網頁的JSON資訊，找到進入下一頁的參數達到往下滑動頁面的動作(進入下頁等同將網頁往下滑)
### 進入下頁後再取一次JSON的資訊(影片資訊與再進入下一頁的參數)

#=== go to page1
url="https://www.youtube.com/results?"
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
           "content-type": "application/x-www-form-urlencoded"}
para = {"search_query": "博恩夜夜", "sp":"EgIQAQ%3D%3D"} #"search_query": "博恩夜夜"代表關鍵字是博恩夜夜 。"sp":"EgIQAQ%3D%3D" 代表此搜尋只找出影片
html = requests.get(url,headers=headers,params=para)

response = BeautifulSoup(html.text,'html.parser')

a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
data_str = '{' + data_str.split('= {')[1].split('{}};')[0] + '{}}'
data_dict = json.loads(data_str)
#print(data_dict)
#=== 取得 session_token
target = 'XSRF_TOKEN'
start = a[8].text.find(target) + len(target) + len('":"') #str.find('target',start index)可找出對應的足st = b[8].text.find('XSRF_TOKEN')
end = a[8].text.find('"',start)
session_token = a[8].text[start:end]
#print(session_token)

#=== 取進入下一頁的參數
set_para = data_dict['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['continuations'][0]
continuation = set_para['nextContinuationData']['continuation']
clickTrackingParams = set_para['nextContinuationData']['clickTrackingParams']
#print(continuation, clickTrackingParams)
print(set_para)
print(continuation)
print(clickTrackingParams)
#=== 開始取第一頁的資訊
set_a = data_dict['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
#一個頁面含有20個影片資訊 len(set_a)=20
print(set_a)

#列印第一頁的資訊
#print('page: 1')
# for item in set_a:
#     #print('video_title: ',item['videoRenderer']['title']['runs'][0]['text'])
#     print('video_info: ',item['videoRenderer']['title']['accessibility']['accessibilityData']['label'])
#     print('video_id: ', item['videoRenderer']['videoId'])
#     print('channel of video: ', item['videoRenderer']['ownerText']['runs'][0]['text'])
#     print('channel_id of video: ', item['videoRenderer']['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'])
#
# #=== go to next page
# for page in range(5):  #for 迴圈中的數字代表還要多找幾頁的內容
#     url="https://www.youtube.com/results?"
#     para = {"search_query": "博恩夜夜",
#             "sp": "EgIQAQ%3D%3D",
#             "ctoken": continuation,
#             "continuation": continuation,
#             "itct": clickTrackingParams}
#
#     data = {"session_token": session_token}
#     html = requests.post(url,data=data,headers=headers,params=para)
#
#     response = BeautifulSoup(html.text,'html.parser')
#     print(response)
#
#     a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
#     data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
#     data_str = '{' + data_str.split('= {')[1].split('{}};')[0] + '{}}'
#     data_dict = json.loads(data_str)
#
#     #===找到session_token
#     target = 'XSRF_TOKEN'
#     start = a[8].text.find(target) + len(target) + len('":"') #str.find('target',start index)可找出對應的足st = b[8].text.find('XSRF_TOKEN')
#     end = a[8].text.find('"',start)
#     session_token = a[8].text[start:end]
#     #print(session_token)
#
#     #=== 取進入下一頁的參數
#     set_para = data_dict['continuationContents']['itemSectionContinuation']['continuations'][0]
#     continuation = set_para['nextContinuationData']['continuation']
#     clickTrackingParams = set_para['nextContinuationData']['clickTrackingParams']
#     #print(continuation, clickTrackingParams)
#
#     #=== 開始取資訊
#     set_b = data_dict['continuationContents']['itemSectionContinuation']['contents']
#     # 列印下一頁的資訊
#     print('=======================================================================================================================')
#     print('page: {}'.format(page+2))
#     for item_b in set_b:
#         #print('video_title: ',item_b['videoRenderer']['title']['runs'][0]['text'])
#         print('video_info: ', item_b['videoRenderer']['title']['accessibility']['accessibilityData']['label'])
#         print('video_id: ', item_b['videoRenderer']['videoId'])
#         print('channel of video: ', item_b['videoRenderer']['ownerText']['runs'][0]['text'])
#         print('channel_id of video: ', item_b['videoRenderer']['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'])