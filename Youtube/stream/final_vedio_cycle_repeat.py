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

##讀取原始的RowData
row_data = pd.read_csv(r'./row_dict/row_data%s.csv' %(""))
channel_id = list(set(row_data['channel_id']))
### 設定dataframe,後頭開始存資料
dflist = pd.DataFrame()
##建立repeat_data目錄
repeat_dict = r'./repeat_dict'
if not os.path.exists(repeat_dict): #若目錄不存在則新增一個
    os.mkdir(repeat_dict)

##定義函式repeat 取重複資料並儲存
def repeat(video_ID,channel_id,view_count):
    repeat_data = pd.DataFrame(
        data=[{ 'video_id': video_ID,
               'channel_id': channel_id,
                now_time:  view_count}],
        columns=['video_id', 'channel_id', now_time]
    )
    return repeat_data


#注意header帶入的參數 進入第一頁
for i,each in enumerate(channel_id):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
    url ='https://www.youtube.com/channel/{}/videos?view=0&sort=dd&shelf_id=0'.format(each)  # 某頻道的播放清單網址
    try:
        html = requests.get(url, headers=headers)
        if str(html) == '<Response [404]>':
            print('該頻道的網址寫作', 'https://www.youtube.com/channel/' + each + '/videos')
            url = 'https://www.youtube.com/channel/{}/videos'.format(each)
            html = requests.get(url, headers=headers)
        response = BeautifulSoup(html.text, 'html.parser')
        a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
        data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
        data_str = '{' + data_str.split('= {')[1].split('}]}}};')[0] + '}]}}}'#處理成完整的json格是再做json.loads
    except IndexError:
        html = requests.get(url, headers=headers)
        if str(html) == '<Response [404]>':
            print('該頻道的網址寫作', 'https://www.youtube.com/channel/' + each + '/videos')
            url = 'https://www.youtube.com/channel/{}/videos'.format(each)
            html = requests.get(url, headers=headers)
        response = BeautifulSoup(html.text, 'html.parser')
        a = response.select('script')  # 目標json在window["ytInitialData"]在當中，在a的倒數第3個
        data_str = str(a[-3].text)  # window["ytInitialData"] = {"responseContext":{... 的字串檔
        data_str = '{' + data_str.split('= {')[1].split('}]}}};')[0] + '}]}}}'  # 處理成完整的json格是再做json.loads
    data_dict = json.loads(data_str)

    #=== 取進入下一頁的參數
    set_dict = data_dict['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']
    try:
        continuation = set_dict['continuations'][0]['nextContinuationData']['continuation']
    except Exception:
        continuation = ''
    count = 1

    #開始取值
    set = set_dict['items']
    for item in set:
        try:
            video_id = item['gridVideoRenderer']['videoId']
            title = item['gridVideoRenderer']['title']['simpleText']
            view_count = ''.join(item['gridVideoRenderer']['viewCountText']['simpleText'].split('：')[-1].split('次')[0].split(','))
            add_count = 1 #計次使用
            print(count, title, ' ', video_id, ' ', view_count)
            count += 1
        except Exception:
            print(Exception)
            pass
        data = repeat(video_id, channel_id[i], view_count)
        dflist = dflist.append(data, ignore_index=True)

    print('==============================')
    # continuation = '4qmFsgI0EhhVQ3hVelEzd3Uwb0pQXzhZTFd0NzFXZ1EaGEVnWjJhV1JsYjNNZ0FEZ0JlZ0V5dUFFQQ%3D%3D'
    pagecount = 0
    while continuation and pagecount <2:
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
            try:
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


                for j in range(len(item_list)):
                    title = item_list[j].h3.a.text
                    video_id = item_list[j].h3.a['href'].split('v=')[-1]
                    view_count = ''.join(item2_list[j].li.text.split('：')[-1].split('次')[0].split(','))
                    print(count, title, ' ', video_id, ' ', view_count)
                    count += 1
                    try:
                        data = repeat(video_id, channel_id[i], view_count)
                        dflist = dflist.append(data, ignore_index=True)
                    except Exception:
                        print(Exception)
                        continue
            except KeyError:
                print(KeyError)
                pass
            print('==============================')
            pagecount += 1
#repeat_data 存成csv檔
repeat_data = pd.merge(row_data, dflist,on=['video_id','channel_id'],how = 'left')
repeat_data['add_count'] = repeat_data['add_count'].map(lambda x: x+1) ###當重複 add_count 會+1
print(repeat_data)
repeat_data.to_csv(r'./repeat_dict/repeat_data_%s.csv' % (now_time), index=False, encoding='utf-8-sig')
repeat_data.to_csv('./repeat_dict/repeat_data{}.csv'.format(''),encoding='utf-8-sig',index = False)

#將repeat_data和New_data合併並儲存
row_new_data_append = pd.read_csv(r'./new_dict/new_data%s.csv' % (''))
final_data = repeat_data.append(row_new_data_append,sort=False)
final_data = final_data.drop_duplicates(subset=['channel_id','video_id'], keep='first') #去重複Video_id的值
print(final_data)
final_data.to_csv(r'./row_dict/row_data%s.csv' %(""),encoding='utf-8-sig',index = False)
final_data.to_csv(r'./{}_data_{}.csv'.format('final',"beck_up"),encoding='utf-8-sig',index = False)
tend = time.time()
print(tend-tstart)
