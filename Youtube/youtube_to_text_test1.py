import subprocess
import os
from bs4 import BeautifulSoup
from pytube import YouTube
import speech_recognition as sr

####### 使用前預作的安裝檔 ########
### pip install speech_recognition
### pip install pytube
### pip install subprocess (如果需要再安裝)
### 下載ffmpeg， https://www.ffmpeg.org/download.html，將ffmpeg.exe檔放在這支程式同個檔案目錄
### 可能要改pytube套件中，mixins.py這支程式中的apply_descrambler()的fuction
### 改mixins.py中的敘述: https://github.com/nficano/pytube/issues/467

#https://clay-atlas.com/blog/2019/11/08/python-chinese-packages-pytube-moviepy-download-youtube-convert/


#取得工作目錄
work_path = os.getcwd()

#愈下載的影片，輸入video_id
video_id = 'qAkGvIFv9uA'  #Jqpu8MnNmAM  qAkGvIFv9uA CjXsHl88iI4

vid_url = "https://www.youtube.com/watch?v=" + video_id

#使用pytube套件來下載影片，建立YouTube()類別的實例
yt = YouTube(vid_url)
print(yt.title)
vd_length = yt.player_config_args.get('player_response').get('videoDetails').get('lengthSeconds')
#設定下載影片的品質
vd = yt.streams.filter(file_extension='mp4', res='360p').first()
#檔名
filename = 'video_t3'
#下載
vd.download(work_path,filename=filename)
#將mp4檔轉成wav檔
command = "ffmpeg -i {}.mp4 -ab 160k -ac 2 -ar 44100 -vn {}.wav".format(filename, filename)
subprocess.call(command, shell=True)

#利用speech_recognitionj做語音轉檔
loop = (int(vd_length)) // 20
r = sr.Recognizer()
audio = []
with sr.AudioFile('{}.wav'.format(filename)) as source:
    for i in range(loop):
        audio.append(r.record(source, duration=20)) #影片中每20秒做一次語音辨識

print('開始翻譯:')
#印出翻譯內容
for i in range(loop):
    #這邊sr.Recognizer()選擇google的翻譯模型(r.recognize_google)
    command1 = r.recognize_google(audio[i],language="zh-TW")
    print(command1)
    print('')
