import requests
from bs4 import BeautifulSoup
import os
import threading
import time

# 全局变量
i = 1
IMG_URL = []
IMG_NAME = []
PAGE_URLS = []
gLock = threading.Lock()
headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
    }
# 创建储存表情包的文件夹
file_path = './img'
if not os.path.exists(file_path):
    os.makedirs(file_path)


def get_the_page():
    while True:
        gLock.acquire()# 上锁
        if len(PAGE_URLS) == 0:
            gLock.release()# 解锁
            break
        # pop函数是从列表中取出最后一个数据，并将其在列表中删除
        page_url = PAGE_URLS.pop()
        gLock.release()
        html = requests.get(page_url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        img_list = soup.find_all("img", attrs={"class": "img-responsive lazy image_dta"})
        for img in img_list:
            img_url = img["data-backup"]# 图片链接
            img_name = img["alt"]# 图片名
            IMG_NAME.append(img_name)
            IMG_URL.append(img_url)


def get_the_picture():
    global i
    while True:
        if len(IMG_URL) == 0 and len(PAGE_URLS) == 0:
            break
        if len(IMG_URL) > 0:
            gLock.acquire()
            img_url = IMG_URL.pop()
            img_name = IMG_NAME.pop()
            gLock.release()
            response = requests.get(img_url)
            # 图片链接中包含了图片格式，使用split函数将其提取出来
            suffix = img_url.split(".")[-1]
            # 去除非法字符
            suffix = suffix.replace('/', '')
            intab = r'\/:*?"<>|'
            outtab = '、、：-？“《》-'
            trantab = str.maketrans(intab, outtab)
            suffix = suffix.translate(trantab)
            # 图片名有些为空，若为空则以数字代替图片名
            if img_name == '':
                img_path = '{}/{}.{}'.format(file_path, str(i), suffix)
                i += 1
            else:
                img_path = '{}/{}.{}'.format(file_path, img_name, suffix)
            if not os.path.exists(img_path):
                with open(img_path, 'wb')as f:
                    f.write(response.content)
                    print('下载成功')
            else:
                print('已经下载')


# 多线程处理
def main():
    for x in range(1, 11):
        page_url = "https://www.doutula.com/photo/list/?page=" + str(x)
        PAGE_URLS.append(page_url)
    
    # 每次处理5个
    for x in range(5):
        th = threading.Thread(target=get_the_page)
        th.start()

    for x in range(5):
        th = threading.Thread(target=get_the_picture)
        th.start()


if __name__ == '__main__':
    main()
