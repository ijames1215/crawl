from bs4 import BeautifulSoup
from selenium import webdriver
import re, time, requests
import pandas as pd
import os
import datetime
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code

resource_path = r'/home/aejohnny1/crawler/tvbs_news/data'
if not os.path.exists(resource_path):
    os.mkdir(resource_path)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

def getYesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday

target_date=getYesterday()

url="https://news.tvbs.com.tw/realtime/"+str(target_date)


try:
    #==== 設定chrome_options，這邊一定要設定，否則在vm(centOS7)上使用Chrome driver會有很多錯誤，當然前提是centOS的環境也有架設好
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')  # 这句一定要加
    #更改執行的路徑'/usr/local/bin/chromedriver'(這是當時在centOS7上的安裝路徑)，與加入參數chrome_options
    driver = webdriver.Chrome('/./chromedriver', chrome_options=chrome_options)

    #使用windows下面這行開啟
    #driver = webdriver.Chrome()
    driver.get(url)
#res=requests.get(url=url, headers=headers)
#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless') # 啟動無頭模式
#chrome_options.add_argument('--disable-gpu') # windowsd必須加入此行
#driver = webdriver.Chrome(chrome_options = chrome_options)

    for i in range(50):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(0.6)
    soup=BeautifulSoup(driver.page_source,'html.parser')
    test_tvbs = pd.DataFrame()
    title_url=soup.select('ul[id="realtime_data"] a')

    for u in title_url:
        try:
            url_new = 'https://news.tvbs.com.tw/' + u['href']
            flag = u['href'].split('/')[1]
            if flag == 'live':
                continue
            else:
                print(flag)
                print(url_new)
            res = requests.get(url=url_new, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.select('div[class="newsdetail_content"] h1')

            print(title[0].text)
            date = soup.select('div[class="icon_time time leftBox2"]')
            date_new = date[0].text.split(' ')[0].replace('/', '')
            time = date[0].text.split(' ')[1].replace(':', '')
            #print(date_new)
            #print(time)

            content = soup.select('div[class="h7 margin_b20"] p')
            content_new = content[0].text
            #print(content_new)

            df = pd.DataFrame(
                data=[{
                    'title': title[0].text,
                    'date': date_new,
                    'time': time,
                    'content': content_new,
                    'link': url_new,
                    'flag': flag,

                }],
                columns=['title', 'date', 'time', 'content', 'link', 'flag'])

            test_tvbs = test_tvbs.append(df, ignore_index=True)
            test_tvbs.to_csv('/home/aejohnny1/crawler/tvbs_news/data/tvbs_news_{}.csv'.format(date_new), encoding='utf-8-sig',index=0)
        except IndexError:
            pass
    # === 成功爬完使用line重送訊息，訊息寫在 message 該變數
    message = 'TVBS_news: {} 的新聞已經由例行公事完成'.format(date_new)
    # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
    token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
    # 使用前面訂好的函式發送出訊息
    lineNotifyMessage(token, message)
    #driver.quit()
except Exception as e:
    message = 'TVBS_news: Expection occurs! message: {}'.format(e)
    # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
    token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
    #發生exception時送出該訊息
    #lineNotifyMessage(token, message)
    driver.quit()
