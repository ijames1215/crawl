#udn新聞分類 要聞 選舉 娛樂 運動 全球 社會 專題 產經 股市 房市 健康 生活 文教 討論 地方 兩岸 數位 旅遊 閱讀 雜誌 購物
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from urllib import request, parse
import os
import time
import lxml.html
import datetime
import csv

udn_path = r'/home/aejohnny1/crawler/udn_news/data' #存至此目錄
if not os.path.exists(udn_path): #若目錄不存在則新增一個
    os.mkdir(udn_path)

# 昨天日期
yesterday = (datetime.date.today() - datetime.timedelta(1)); yesterday = ''.join(str(yesterday).split('-'))
#print(yesterday)
def save(title, date, time, content, Link,flag):
    df = pd.DataFrame(
        data=[{
            'title': title,
            'date': date,
            'time': time,
            'content': content,
            'link': Link,
            'flag':flag
        }],
        columns=['title', 'date', 'time', 'content', 'link','flag'])
    return df
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code
i=2
url = 'https://udn.com/news/get_breaks_article/%s/1/99?_=1578018848907'%(i)
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
url_all = soup.select('h2')
joblist=pd.DataFrame()#存資料
date=str(datetime.date.today() + datetime.timedelta(+1)).split('-')[0]+ str(datetime.date.today() + datetime.timedelta(+1)).split('-')[1]+str(datetime.date.today() + datetime.timedelta(+1)).split('-')[2]
ture_day=str(datetime.date.today() + datetime.timedelta(+1)).split('-')[0]+ str(datetime.date.today() + datetime.timedelta(+1)).split('-')[1]+str(datetime.date.today() + datetime.timedelta(+1)).split('-')[2]
time=''
while(True):#爬文
    try:
        print(url)
        for each_article in url_all:
            try:
                repeat=False
                content=''
                title=each_article.a.text
                article_url='https://udn.com/'+each_article('a')[0]['href']
                article_res=requests.get(article_url)
                article_soup=BeautifulSoup(article_res.text,'html.parser')
                list=article_soup.select('div[id="article_body"]')
                list_date=article_soup.select('div[class="story_bady_info_author"]')
                flag=article_soup.select('div[class="only_web"]')[4]('a')[1].text

                try: #儲存日期
                    date = list_date[0]('span')[0].text.split(' ')[0].split('-')[0] + \
                          list_date[0]('span')[0].text.split(' ')[0].split('-')[1] + \
                          list_date[0]('span')[0].text.split(' ')[0].split('-')[2]
                    time=list_date[0]('span')[0].text.split(' ')[1].split(':')[0]+list_date[0]('span')[0].text.split(' ')[1].split(':')[1]
                    if (ture_day != date and ture_day != str(datetime.date.today() + datetime.timedelta(+1)).split('-')[0] + #日期為明天不存
                            str(datetime.date.today() + datetime.timedelta(+1)).split('-')[1] +
                            str(datetime.date.today() + datetime.timedelta(+1)).split('-')[2]) : #跟前一篇不同日期就儲存
                        joblist.to_csv(udn_path+'/udn_%s.csv' % (yesterday),encoding="utf-8-sig", index=0)
                        joblist = pd.DataFrame()
                    ture_day = date #前篇文章日期
                except:
                    print("沒有日期")
                    print('標題:', each_article.a.text)
                print(date+''+time+''+title+' '+article_url)
                try: #判斷是否存過這個標題
                    for title_repeat in joblist['title']: #跟前面存的所有標題比對一次
                        if (title == title_repeat):
                            print("這篇存過了")
                            repeat = True
                            break
                except:
                    print('第一篇')
                for main_get in list[0]('p'): #儲存內文
                    content+=main_get.text
                if 'z-index: 100' in content: #問題文章不存
                    print('這篇有問題')
                    repeat = True
                df=save(title,date,str(time),content,article_url,flag)
                if(repeat==False):#存過的標題不做儲存
                    joblist=joblist.append(df,ignore_index=True)
                else:
                    print(title + '存過的 ' + title_repeat)
            except:
                print("失敗")
        i+=1
        url = 'https://udn.com/news/get_breaks_article/%s/1/99?_=1578018848907'%(i)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        url_all = soup.select('h2')
        if(date==str(datetime.date.today() + datetime.timedelta(-2)).split('-')[0]+ str(datetime.date.today() + datetime.timedelta(-2)).split('-')[1]+str(datetime.date.today() + datetime.timedelta(-2)).split('-')[2]): #抓完昨天的文章
            message = 'Udn_news: {} 的新聞已經由例行公事完成'.format(yesterday)
            # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
            token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
            # 使用前面訂好的函式發送出訊息
            #lineNotifyMessage(token, message)
            break
    except Exception as e:
        message = 'Udn_news: Expection occurs! message: {}'.format(e)
        # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
        token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
        #發生exception時送出該訊息
        #lineNotifyMessage(token, message)