import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import os
import time
import lxml.html
import pandas as pd
from opencc import OpenCC

# 留言的目標url 是看網路文章得來的，從開發者人員工具中看不到這些網址
# reference: http://www.bithub00.com/2019/07/25/Youtube%E7%88%AC%E8%99%AB/
# reference: https://github.com/egbertbouman/youtube-comment-downloader

#目標影片，設定video_id
video_id = "2pzt4XbdANM"

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

# Get Youtube page with initial comments
first_page_comment_url = 'https://www.youtube.com/all_comments?v=' + video_id

#先進入 https://www.youtube.com/all_comments?v=video_id (進入該頁面的目的是拿到session_token)
response = session.get(first_page_comment_url)
html = response.text

#===找到session_token
target = 'XSRF_TOKEN'
start = html.find(target) + len(target) + len('\': \"') #str.find('target',start index)可找出對應的足碼
end = html.find('"',start)
session_token = html[start:end]

#設定函式去request
def ajax_request(session, url, params, data):
    response = session.post(url, params=params, data=data)
    response_dict = json.loads(response.text)
    return response_dict.get('page_token', None), response_dict['html_content']

# 開始進入留言區
count = 1
data_con = pd.DataFrame(columns=['video_id','留言者','留言','留言時間'])

###設定簡體轉繁體方法
cc = OpenCC('s2t')  # convert from Simplified Chinese to Traditional Chinese

#進入留言區第一頁時要帶的資料比較不同 data / params (order_menu : True)
data = {'video_id': video_id,'session_token': session_token}
params = {'action_load_comments': 1, 'order_by_time': True, 'filter': video_id, 'order_menu': True}

# 先設定page_token為真使while作動; 待會跑到最後一頁時，page_token 為空值，因此while停止
page_token = True

#每一頁留言(仿留言往下滑)
while page_token:
    response_2 = ajax_request(session, 'https://www.youtube.com/comment_ajax' , params, data)

    #留言區的第二頁之後的帶的資料 data / params
    data = {'video_id': video_id, 'session_token': session_token}
    params = {'action_load_comments': 1, 'order_by_time': True, 'filter': video_id}

    # response_2[0] 為 page_token
    # response_2[1] 為 回傳訊息的留言內容區

    page_token = response_2[0]
    data['page_token'] = page_token

    res = BeautifulSoup(response_2[1], 'html.parser')
    # 使用標籤取出每一頁的留言
    coent = res.select('div.comment-text-content')  # 留言
    user_name = res.select('a.user-name')  # 留言者
    coent_time = res.select('span.time')  # 留言時間

    #開始記錄留言進dataframe (data_con)
    for i in range(len(coent_time)):

        #加入pa.dataframe時順便將簡體轉成繁體
        data_con = data_con.append({'video_id': video_id, '留言者': cc.convert(user_name[i].text.strip()),'留言': cc.convert(''.join(coent[i].text.strip().split('\n'))), '留言時間':coent_time[i].text.strip()}, ignore_index=True)
        #print(user_name[i].text.strip(),coent[i].text.strip(), coent_time[i].text.strip())

    print('第{}頁, page_token: {}'.format(count, page_token))
    count += 1

#印出所有結果
print(data_con)

#存成csv檔
data_con.to_csv(r'./youtube_comment_{}.csv'.format(video_id), index=0, encoding='utf-8-sig')
