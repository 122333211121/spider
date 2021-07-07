import requests
from bs4 import BeautifulSoup
import os
import threading
import time

i = 1
IMG_URL = []
IMG_NAME = []
PAGE_URLS = []
gLock = threading.Lock()
headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
    }
file_path = './img'
if not os.path.exists(file_path):
    os.makedirs(file_path)


def get_the_page():
    while True:
        gLock.acquire()
        if len(PAGE_URLS) == 0:
            gLock.release()
            break
        page_url = PAGE_URLS.pop()
        gLock.release()
        html = requests.get(page_url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        img_list = soup.find_all("img", attrs={"class": "img-responsive lazy image_dta"})
        for img in img_list:
            img_url = img["data-backup"]
            img_name = img["alt"]
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
            gLock.release()
            response = requests.get(img_url)
            suffix = img_url.split(".")[-1]
            suffix.replace('/', '')
            intab = r'\/:*?"<>|'
            outtab = '、、：-？“《》-'
            trantab = str.maketrans(intab, outtab)
            gLock.acquire()
            img_name = IMG_NAME.pop()
            gLock.release()
            if img_name == '':
                img_path = '{}/{}.{}'.format(file_path, str(i), suffix.translate(trantab))
                i += 1
            else:
                img_path = '{}/{}.{}'.format(file_path, img_name, suffix.translate(trantab))
            if not os.path.exists(img_path):
                with open(img_path, 'wb')as f:
                    f.write(response.content)
                    print('下载成功')
            else:
                print('已经下载')



def main():
    for x in range(1, 11):
        page_url = "https://www.doutula.com/photo/list/?page=" + str(x)
        PAGE_URLS.append(page_url)

    for x in range(5):
        th = threading.Thread(target=get_the_page)
        th.start()

    for x in range(5):
        th = threading.Thread(target=get_the_picture)
        th.start()


if __name__ == '__main__':
    main()