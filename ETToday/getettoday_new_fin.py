import json
from lxml import etree
import requests
from bs4 import BeautifulSoup
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import pandas as pd
import os
import datetime
#xpath contains 寫法: https://blog.csdn.net/weixin_30347335/article/details/95240345 or https://www.guru99.com/using-contains-sbiling-ancestor-to-find-element-in-selenium.html

#url= "https://www.ettoday.net/news/news-list.htm"

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code

resource_path = r'/home/aejohnny1/crawler/ettoday_news/data'
if not os.path.exists(resource_path):
    os.mkdir(resource_path)

testList = pd.DataFrame()

def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday

target_date = str(getYesterday()).replace('-','')


url = "https://www.ettoday.net/news/news-list-{}-{}-{}-0.htm".format(target_date[0:4],target_date[4:6],target_date[6::])
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
try:
    #==== 設定chrome_options，這邊一定要設定，否則在vm(centOS7)上使用Chrome driver會有很多錯誤，當然前提是centOS的環境也有架設好
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')  # 这句一定要加

    #更改執行的路徑'/usr/local/bin/chromedriver'(這是當時在centOS7上的安裝路徑)，與加入參數chrome_options
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)
    #driver = webdriver.Chrome('./chromedriver')
    driver.get(url) #get(url)是連結網址
    tmp_date = int(target_date)
    tmp_hr = '0000'
    final_hr = '0001'
    page_set = 0
    #=== 翻頁: 一旦翻到目標日的前一日的新聞會停止翻頁
    while tmp_date >= int(target_date) and page_set < 6: #final_hr != tmp_hr:
        tmp_hr = final_hr
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        date_post = driver.find_elements_by_xpath("//div[@class='part_list_2']/h3/span")
        time.sleep(1)
        t = date_post[-1].text.split()[0]
        tmp_date = int(('').join(t.split('/')))
        t2 = date_post[-1].text.split()[-1]
        final_hr = ('').join(t2.split(':'))
        #print(final_hr)
        if final_hr == tmp_hr:
            page_set += 1
        else:
            page_set = 0
    #=== 取得網站回傳內容取新聞標題(n_t[i].text)、發布時間(data_post)、與新聞網址(n_t[i].get_attribute('href'))
    #re_dr = driver.page_source #get_source 是selenium的方法，可以取得網頁原始碼
    all_title = driver.find_element_by_xpath("//div[@class='part_list_2']/h3/a").text #driver.find_element_by_xpath: element只找一個
    n_t = driver.find_elements_by_xpath("//div[@class='part_list_2']/h3/a") #driver.find_elements_by_xpath: elements找所有符合的List
    date_post = driver.find_elements_by_xpath("//div[@class='part_list_2']/h3/span")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    title_time = soup.select('div[class="part_list_2"] span')
    print(len(n_t))


    #建立每篇新聞列表
    data_list = []
    for i in range(len(n_t)):
        data_list.append([n_t[i].text,n_t[i].get_attribute('href'),date_post[i].text])

    #=== 找出當日的最後一邊文章編號:endnum
    endnum = len(n_t)-1
    x = data_list[-1][2].split()[0]
    tmp_date2 = int(('').join(x.split('/')))
    while tmp_date2 < int(target_date):
        endnum -= 1
        x = data_list[endnum][2].split()[0]
        tmp_date2 = int(('').join(x.split('/')))

    print('==========')
    print(endnum)
    print(data_list[endnum])

    #開始造訪當天所有文章並存下文章內容
    #f = open('ettoday_article_{}.txt'.format(target_date), 'w', encoding='utf-8') #開啟txt檔
    for j,item in enumerate(data_list[0:endnum+1]):
        article_url = item[1]
        res_article = requests.get(article_url, headers=headers)
        html2 = etree.HTML(res_article.content.decode())
        # 標題
        cont_title = html2.xpath("//header/h1/text()")
        # 報導時間
        date_pos = html2.xpath("//time/text()")

        article_time1 = title_time[j].text.split(' ')[-1].replace(':', '')
        #print(article_time1)
        # 內文
        content = html2.xpath("//div[contains(@class,'story')]/p/text()")  # content is a list
        content = ' '.join(content)
        #flag
        soup_article = BeautifulSoup(res_article.text, 'html.parser')
        flag = (soup_article.select('span[itemprop="name"]')[1]).text
        # #寫入資料
        # f.write(cont_title[0] + '\n')
        # f.write(date_pos[0].strip() + '\n')
        # f.write(content + '\n')
        # f.write("------------------------------------------------------------" + '\n')
        # time.sleep(1) #休息1秒
    #f.close()
        df = pd.DataFrame(
                data=[{
                    'title':cont_title[0],
                    'date': target_date,
                    'time': article_time1,
                    'content': content,
                    'link': n_t[j].get_attribute('href'),
                    'flag': flag,

                }],
                columns=['title', 'date', 'time', 'content', 'link', 'flag'])

        testList = testList.append(df, ignore_index=True)
        testList.to_csv('/home/aejohnny1/crawler/ettoday_news/data/ettoday_news_{}.csv'.format(target_date), encoding='utf-8-sig',index=0)

 #=== 成功爬完使用line重送訊息，訊息寫在 message 該變數
    message = 'ETtoday: {} 的新聞已經由例行公事完成'.format(target_date)
    # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
    token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
    # 使用前面訂好的函式發送出訊息
    #lineNotifyMessage(token, message)
except Exception as e:
    message = 'ETtoday News:Expection occurs! message: {}'.format(e)
    # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
    token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
    #發生exception時送出該訊息
    #lineNotifyMessage(token, message)
    driver.quit()
driver.quit()