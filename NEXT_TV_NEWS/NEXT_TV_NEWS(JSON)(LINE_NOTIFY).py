import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import os
import pandas as pd

# 昨天日期
yesterday = (datetime.strftime(datetime.now() - timedelta(1), '%Y%m%d'))


# ===== 設定line發送函式 https://bustlec.github.io/note/2018/07/10/line-notify-using-python/ ====
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code
# ==== 設定line發送函式 https://bustlec.github.io/note/2018/07/10/line-notify-using-python/ ====


# 設定爬下來的新聞要放的資料夾
res_path = r'./NEXT_TV'
if not os.path.exists(res_path):
    os.mkdir(res_path)


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
# 壹新聞首頁
url = "http://www.nexttv.com.tw/NextTV/News/"


##### 先從首頁取得每個新聞分類的id #####
res = requests.get(url, headers=headers)
res.encoding = 'utf-8'  # 加上這行中文字才不會是亂碼
soup = BeautifulSoup(res.text, 'html.parser')
cate_id = soup.select("ul.clearfix.columnListUL.fl.cell_13611_ li")

cate_id_list = []
for i in cate_id:
    cate_id_list.append(i["data-id"])
    #print(i.text) 印出分類名


#====================分類 & ID 對應========================================================
# 最新144,145,146,147,148,149,150,118,120,121,122,124,453
# 選戰金句1122, 政治144, 社會145, 地方146, 財經147, 國際148, 生活149, 娛樂150, 體育151, 音樂454,
# 戲劇455, 舞蹈457, 親子458, 演唱會459, 旅遊460, 體育461, 電影462
# =========================================================================================
cate_id_list = cate_id_list[1::]  # ((不要第一個"最新"的分類(因為包含其他分類)))


# 新聞列表dataframe
news_list = pd.DataFrame(columns=['title', 'date', 'time', 'content', 'link', 'flag'])


######輸入需要的新聞區間(抓歷史訊息用的)########
# start_datetime = datetime.strptime('2020-01-16 00:00', '%Y-%m-%d %H:%M')
# end_datetime = datetime.strptime('2020-01-16 23:59', '%Y-%m-%d %H:%M')

# 用此URL找到JSON檔(用來取得[文章標題]和[文章URL])
jsn_url = 'http://www.nexttv.com.tw/m2o/loadmore.php'

############# 測試用 ##################
# test_list = [144]
######################################

# form data (count設越多要的資料越多(抓歷史資料的時候約設6000, 抓單日約設250) /
#            column_id代表新聞分類的id, 將由抓好的分類id取代)
form_data = {'offset': '0', 'count': '250', 'not_need_child_column': '1', 'sign': '', 'column_id': '0'}

# 先建一個空的dataframe, 用來暫存迴圈每一層(每一篇)新聞資料
df = pd.DataFrame()


#################開始爬文#####################
try:
    for id in cate_id_list:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("開始爬取分類ID:"+str(id)+'===========================>>>>>>>>>>>>>>>>>>>>>>>')
        print()
        form_data['column_id'] = id  # 每次進入一個分類
        jsn_res = requests.post(jsn_url, headers=headers, data=form_data)
        js = json.loads(jsn_res.text)  # 每個分類的所有文章

        for n, news in enumerate(js):
            try:
                title = news['title']  # 新聞標題
                flag = news['column_name']  # 新聞分類
                news_url = news['content_url']  # 新聞URL

                # 用傳統TAG方式取文章內容及日期時間(因JSON檔找不到新聞內文)
                con_res = requests.get(news_url, headers=headers)
                con_res.encoding = 'utf-8'  # 加上這行中文字才不會是亂碼
                con_soup = BeautifulSoup(con_res.text, 'html.parser')

                # 日期+時間
                publish_date = con_soup.select("div.article-toolbar.clearfix")[0].select('span.time')[0].text
                # 日期
                date = publish_date.split(" ")[0].replace("-","")
                # 時間
                time = str(publish_date.split(" ")[1].replace(":",""))
                # 內文
                news_content = con_soup.select("div.article-main")[0].text

                # 日期str改成datetime格式(((用來決定取得日期區間)))(抓歷史訊息用)
                # publish_date1 = datetime.strptime(publish_date, '%Y-%m-%d %H:%M')
            except:
                print("<<<一筆資料擷取失敗({})>>>".format(n))
                pass

            if date == yesterday:  # 只印出日期是昨天的日期
                print(n, title, date, time)
                print(news_content)
                print(news_url, flag)
                print()
                print("============================================================")
                print()
                df = pd.DataFrame(
                    data=[{
                        'title': title,
                        'date': date,
                        'time': time,
                        'content': news_content,
                        'link': news_url,
                        'flag': flag}], columns=['title', 'date', 'time', 'content', 'link', 'flag'])
                news_list = news_list.append(df)

    print("已全部搜尋完成!")
    news_list.to_csv(r'./NEXT_TV/NEXT_TV_{}.csv'.format(yesterday), index=0, encoding="utf-8-sig")
    # 加上utf-8-sig後在EXCEL看才不會是亂碼

    # =======成功爬完使用line重送訊息，訊息寫在 message 該變數==========================================
    message = '壹新聞NEXT_TV: {} 的新聞已經由例行公事完成'.format(yesterday)
    # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
    token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
    # 使用前面訂好的函式發送出訊息
    lineNotifyMessage(token, message)
    # =================================================================================================


# 發生exception時的處理==================================================================================
except Exception as e:
    message = 'Expection occurs! message: {}'.format(e)
    # 帶入權杖，這串token是當時在line網站上建立line notify時會跑出來的金鑰，官方說法是權杖
    token = 'p8jxzXyw8xl2NOuPjSi8s5NOP0qFTPXDQ2idzOSZZK8'
    # 發生exception時送出該訊息
    lineNotifyMessage(token, message)
# =======================================================================================================