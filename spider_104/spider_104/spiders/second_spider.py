# -*- coding: utf-8 -*-
import scrapy
from spider_104.items import Spider_104Item
import re
##part1
class SecondSpiderSpider(scrapy.Spider):
    name = 'second_spider'
    allowed_domains = ['104.com.tw']

    job_search_list = ['爬蟲工程師','數據分析師','資料科學']
    url_part1 = 'https://www.104.com.tw/jobs/search/?ro=0&keyword='
    url_part2 = '&order=1&asc=0&page='
    url_part3 = '&mode=s&jobsource=2018indexpoc'

    start_urls = []
    for job in job_search_list:
        start_urls.append(url_part1 + job + url_part2 + '1' + url_part3)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    # 塞起始網頁(需要爬取的工程師種類)，callback parse函數
##part2
    def parse(self, response):
        # 用selector抓網址，然後寫迴圈
        print("開始爬取:", response.url)

        url_part1 = 'https://www.104.com.tw/jobs/search/?ro=0&keyword='
        url_part2 = '&order=1&asc=0&page='
        url_part3 = '&mode=s&jobsource=2018indexpoc'
##正則表達案(regular exotression)
        keyword = re.findall(r"keyword=(.*)&order.*index", response.url)[0]
        page = int(re.findall(r"page=(.*)&mode.*index", response.url)[0])

        res = response.xpath('//article/div/h2/a/@href').extract()
        for urls in res:
            # 用迴圈判斷是否為廣告連結，不是的話yield parse_item函數
            if 'hotjob' not in urls:
                new_url = 'https:' + urls
                yield scrapy.Request(new_url, self.parse_item, headers=self.headers)

# part4 ---------------------------------------------------------------
        print(len(res))
        print("爬取結束")
        # 判斷是否有下一頁，如果有下一頁，新網址塞進去然後callback自己， 沒有的話   pass(?) ->目前為不理他
        page += 1
        # 有下一頁，新網址塞進去然後callback自己
        if page < 5 and len(res) > 0:
            next_url = url_part1 + keyword + url_part2 + str(page) + url_part3
            print('換頁啦~~~~!!', next_url)
            yield scrapy.Request(next_url, self.parse, headers=self.headers)

    # parse函數負責抓取搜尋頁面的所有連結，先判斷是廣告還是需要的文章，生成需要爬取的文章列表，接著針對需爬取的網址寫迴圈，
    # callback 爬取頁面的函數 parse_item, 接著判斷是否有下一頁，若有的話生成新的頁面網址new_url,並遞迴引用parse函數


##part3
    def parse_item(self, response):
        item = Spider_104Item()
        item['job'] = str.strip(response.xpath('//article/header/div/h1/text()').extract()[0])
        item['company'] = response.xpath('//h1/span/a[1]/text()').extract()[0]
        return item

    # 這邊主要會傳入單個工作頁面的網址，爬取進去之後將回傳的網頁內容解析為bs格式，或是使用selector選擇想要的內容
    # 最後將需要的物件打包成item回傳，記得要先將物件名稱登錄於items檔案\
