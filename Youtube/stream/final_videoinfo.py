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
### 設定dataframe,後頭開始存資料
dflist = pd.DataFrame()
##建立row_data目錄
row_dict = r'./row_dict'
if not os.path.exists(row_dict): #若目錄不存在則新增一個
    os.mkdir(row_dict)

#=== 讀取0_100youtuber csv檔 並進入第一頁
df_all = pd.read_csv("youtubeChannelID111.csv")
channel_id = list(df_all['channelID'])[0:100]
print(channel_id)
channel_youtuber = list(df_all['channelName'])[0:100]
##定義函式save 取兩周內資料並儲存
def save(video_ID,channel_id, channel_of_youtuber, video_title,add_count, view_count): # 用pandas轉成dataframe
    data_con = pd.DataFrame(
        data=[{'video_id': video_ID,
               'channel_id': channel_id,
               'channel_of_youtuber': channel_of_youtuber,
               'video_title': cc.convert(video_title),
               'add_count': add_count,
               now_time: view_count}],
        columns=['video_id', 'channel_id', 'channel_of_youtuber', 'video_title', 'add_count', now_time]
    )
    return data_con
#注意header帶入的參數 進入第一頁
for i,each in enumerate(channel_id):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
    url = 'https://www.youtube.com/channel/{}/videos?view=0&sort=dd&shelf_id=0'.format(each)  # 某頻道的播放清單網址
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
            video_time = item['gridVideoRenderer']['publishedTimeText']['simpleText']
            title = item['gridVideoRenderer']['title']['simpleText']
            view_count = ''.join(item['gridVideoRenderer']['viewCountText']['simpleText'].split('：')[-1].split('次')[0].split(','))
            add_count = 1 #計次使用
            print(count, title, ' ', video_id, ' ',video_time, ' ', view_count)
            count += 1
            try:
                video_time = int(video_time.split('分鐘前')[0])
                if video_time < 60:
                    data_con = save(video_id, channel_id[i], channel_youtuber[i],title, add_count, view_count)
                    dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
            except ValueError:
                try:
                    n_video_time = int(video_time.split('小時前')[0])
                    if n_video_time < 24:
                        data_con = save(video_id, channel_id[i], channel_youtuber[i], title, add_count, view_count)
                        dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
                except ValueError:
                    try:
                        n_video_time = int(video_time.split('天前')[0])
                        if n_video_time < 7:
                            data_con = save(video_id, channel_id[i], channel_youtuber[i], title, add_count, view_count)
                            dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
                    except ValueError:
                        try:
                            n_video_time = int(video_time.split('週前')[0])
                            if n_video_time < 2:
                                data_con = save(video_id, channel_id[i], channel_youtuber[i], title, add_count, view_count)
                                dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
                        except :
                            pass
        except:
            continue

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
                    video_time = item['gridVideoRenderer']['publishedTimeText']['simpleText']
                    view_count = ''.join(item2_list[j].li.text.split('：')[-1].split('次')[0].split(','))
                    print(count, title, ' ', video_id, ' ', view_count)
                    count += 1
                    try:
                        video_time = int(video_time.split('分鐘前')[0])
                        if video_time < 60:
                            data_con = save(video_id, channel_id[i], channel_youtuber[i], title, add_count, view_count)
                            dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
                    except ValueError:
                        try:
                            video_time = int(video_time.split('小時前')[0])
                            if video_time < 24:
                                data_con = save(video_id, channel_id[i], channel_youtuber[i], title, add_count, view_count)
                                dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
                        except ValueError:
                            try:
                                video_time = int(video_time.split('天前')[0])
                                if video_time < 7:
                                    data_con = save(video_id, channel_id[i], channel_youtuber[i], title, add_count,view_count)
                                    dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
                            except IndexError:
                                continue
                            except ValueError:
                                try:
                                    video_time = int(video_time.split('週前')[0])
                                    if video_time < 2:
                                        data_con = save(video_id, channel_id[i], channel_youtuber[i], title, add_count,view_count)
                                        dflist = dflist.append(data_con, ignore_index=True)  # 將檔案存檔
                                except:
                                    pass
            except KeyError:
                pass
            print('==============================')
            pagecount += 1
#將兩周內資料存成csv檔
dflist.to_csv(r'./row_dict/row_data_%s.csv' % (now_time), index=False, encoding='utf-8-sig')
dflist.to_csv(r'./row_dict/row_data{}.csv'.format(''),encoding='utf-8-sig',index = False)

tend = time.time()
print(tend-tstart)