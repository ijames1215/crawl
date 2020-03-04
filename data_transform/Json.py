import requests
from bs4 import BeautifulSoup
import json
from urllib import request, parse
import pandas as pd
import os
import time
import shutil
import csv
from pprint import pprint
#把目標資料夾所有csv轉成json
Folder_Path = r'E:\csv'  #要拼接的所有文件
SaveFile_Path = r'E:\json'  # 保存路徑

os.chdir(Folder_Path) #換工作路徑
file_list = os.listdir() #這個資料夾內所有的檔案名稱
file_csv=[]
for file in file_list: #只讀csv檔
    if '.csv' in file:
        file_csv.append(file)
for i in range(0, len(file_csv)):  # 讀所有檔案
    a = 0  # 紀錄是否為表頭
    with open(Folder_Path+'/%s'%(file_csv[i]), 'r', encoding="utf-8-sig") as f:  # 讀檔案
        SaveFile_Name = r'%s'% (file_csv[i])  # 使用的csv名
        jsonname=SaveFile_Name[0:-4]
        csvfile=open('E:/csv/%s'%(file_csv[i]),'r',encoding='utf-8-sig')#csv檔案路徑
        jsonfile=open('E:/json/%s.json'%(jsonname),'w',encoding='utf-8-sig')#存成json檔案路徑
        fie=('field1','title','date','time','content','Link','flag')#標籤
        reader=csv.DictReader(csvfile,fie)
        jsonfile.write('[')
        a=0
        for row in reader:
            if a == 0:
                pass
            else :
                json.dump(row,jsonfile,separators=(',',':'),ensure_ascii=False)
                jsonfile.write(',')
                jsonfile.write('\n')
            a=1
        jsonfile.write('{}')
        jsonfile.write(']')