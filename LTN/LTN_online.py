from bs4 import BeautifulSoup
import time
import pandas as pd
import json
import requests
import datetime
import os
import csv
dflist = pd.DataFrame()
###setting path
ltn_dict = r'./ltn_dict'  #存至此目錄

###if directory not exist add it
if not os.path.exists(ltn_dict): #若目錄不存在則新增一個
    os.mkdir(ltn_dict)



###setting today and yesterday
today = datetime.date.today() ; today = str(today)
def getYesterday():
    today=datetime.date.today()
    oneday=datetime.timedelta(days=1)
    yesterday=today-oneday
    return yesterday
yesterday = str(getYesterday())

#crawl five category News
part_list = ['politics','society','life','world',"novelty"]
for topic in part_list:
    int_pages = 1
    url = 'https://news.ltn.com.tw/ajax/breakingnews/%s/'%(topic) + str(int_pages)
    request_session = requests.session()  #request在同一個session
    respond = request_session.get(url=url)
    js = json.loads(respond.text) #將json格式轉成python_json格式
    all =js['data'] #取出data底下的內容
    n = 1
    for i in all:
        try:
            print("第", n, "篇")
            title = i['title']  ;  print("title:",title)
            url = i['url']  ;  print("URL:",url)
            flag = i['type_cn']  ;  print("flag",flag)
            each_res = requests.get(url)
            each_soup = BeautifulSoup(each_res.text)
            each_html = each_soup.findAll("div", {'class': "whitecon"})
            str_ = ''
            n += 1
            ###文字清理
            for p_news_text in each_html:
                p_news_text = p_news_text('p')
                for news_all in p_news_text:
                    str_ += news_all.text.split('不用抽')[0]
            ###取得昨天所有新聞
            date_time = each_soup.select("span[class='time']")[0].text
            date = date_time.split()[0]
            if date == yesterday:
                date = date.replace('-', '') ; print(date)
            else :
                continue
            ##取得新聞發文時間
            time = date_time.split()[1].split(':')[0] + date_time.split()[1].split(':')[1] ; print(time)
        except:
            pass
        ###建立Pandas DataFrame
        df = pd.DataFrame(  # 用pandas轉成dataframe
            data=[{
                'title': title,
                'date': date,
                'time': time,
                'content': str_,
                'Link': url,
                'flag':flag
            }],
            columns=['title','date','time','content','Link','flag']
        )
        dflist = dflist.append(df, ignore_index=True)

    for page_2 in range(2,27) : #資料取得,因第一頁和第2頁之後json格式不一樣
        url = "https://news.ltn.com.tw/ajax/breakingnews/%s/%s"%( topic , page_2)
        res = requests.get(url)
        soup = BeautifulSoup(res.text,'html.parser')
        json_string = str(soup)
        js = json.loads(json_string)
        i = 20
        j = 500 #LTN新聞共500篇
        while(i < j):
            try:
                url_main = js['data'][str(i)]['url']
                res = requests.get(url_main)
                soup = BeautifulSoup(res.text,'html.parser')
                str_ = ''
                print( "第" , i+1 , "篇")
                print("flag", js['data'][str(i)]['type_cn'])
                print( "title:" + js['data'][str(i)]['title'])
                print("URL:" + js['data'][str(i)]['url'])
                news = soup.select("div[class='text boxTitle boxText']")
                ###文字清理
                for page in news:
                    page = page('p')
                    for news_all in page:
                        str_ += news_all.text.split('不用抽')[0]
                ###取得昨天所有新聞
                date_time = soup.select("span[class='time']")[0].text
                date = date_time.split()[0]
                if date == yesterday:
                    date = date.replace('-', '')
                    ##取得新聞發文時間
                    time = date_time.split()[1].split(':')[0] + date_time.split()[1].split(':')[1]
                    df = pd.DataFrame(
                        data = [{   # 用pandas轉成dataframe
                            'title':js['data'][str(i)]['title'],
                            'date':date,
                            'time': time,
                            'content': str_,
                            'Link':js['data'][str(i)]['url'],
                            'flag':js['data'][str(i)]['type_cn']
                        }],
                        columns = ['title','date','time','content','Link','flag']
                    )
                    dflist = dflist.append(df,ignore_index=True) #將檔案存檔
                    i += 1
                elif date == today: #當日期為今日還是要 i+=1,因是用ajax爬蟲,需換頁
                    i += 1
                    pass
                else:  #昨日後都不要
                    break
                if (i % 20 == 0):  # 20篇一個json
                    page_2 += 1
                    url = "https://news.ltn.com.tw/ajax/breakingnews/%s/%s" % (topic, page_2)
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    json_string = str(soup)
                    js = json.loads(json_string)
            except:
                break
    dflist.to_csv(ltn_dict + '/ltn_%s.csv'%(today),encoding='utf-8-sig')  ##DataFrame存檔成csv檔案類型

#csv轉json
csvfile=open(ltn_dict + '/ltn_%s.csv'%(today),'r',encoding='utf-8')#csv檔案路徑
jsonfile=open(ltn_dict + '/ltn_%s.json'%(today),'w',encoding='utf-8')#存成json檔案路徑
file=('field1','title','date','time','content','Link','flag')#標籤
reader=csv.DictReader(csvfile,file)
jsonfile.write('[')
for row in reader:
    json.dump(row,jsonfile,separators=(',',':'),ensure_ascii=False)
    jsonfile.write(',')
    jsonfile.write('\n')
jsonfile.write('{}')
jsonfile.write(']')
