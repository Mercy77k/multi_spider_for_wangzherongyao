import threading
import requests
import json
import os
import urllib.error
from queue import Queue
from urllib import parse
from urllib import request
from _queue import Empty

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'referer': 'https://pvp.qq.com/'
    }
url = 'https://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi?activityId=2735&sVerifyCode=ABCD&sDataType=JSON&iListNum=20&totalpage=0&page={}&iOrder=0&iSortNumClose=1&jsoncallback=jQuery111307407747907683988_1746689540190&iAMSActivityId=51991&_everyRead=true&iTypeId=2&iFlowId=267733&iActId=2735&iModuleId=2735&_=1746689540192'

class Producer(threading.Thread):
    def __init__(self, page_url_queue, image_url_queue):
        super().__init__()
        self.page_url_queue = page_url_queue
        self.image_url_queue = image_url_queue
        
    def run(self):
        while not self.page_url_queue.empty():
            # 获取请求页
            page_url = self.page_url_queue.get()
            res_json = get_page_json(page_url, headers=headers)
            
            # 取出每个图片对应的不同尺寸的图片的所有地址
            image_url_dict = {}
            for image_obj in res_json['List']:
                key = parse.unquote((image_obj['sProdName']))+ '_' +image_obj['iProdId']
                image_url = []
                for index in range(1, 9):
                    image_url.append(parse.unquote(image_obj[f'sProdImgNo_{index}'])[:-3] + '0')
             
                image_url_dict[key] = image_url
            
            # 创建image目录存储图片
            image_folder = './image'
            if not os.path.exists(image_folder):
                os.mkdir(image_folder)
                print('创建image目录')
            
            # 为每个图片创建目录存储
            for key in image_url_dict:
                dir_path = os.path.join(image_folder, key.strip(' '))
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)
                    print(f'创建目录:{key}')
            
                # 将图片名称和下载url放入队列
                for index, image_url in enumerate(image_url_dict[key]):
                    image_path = os.path.join(dir_path, f'{index+1}.jpg')
                    self.image_url_queue.put({'image_path': image_path, 'image_url': image_url})


class Customer(threading.Thread):
    def __init__(self, image_url_queue):
        super().__init__()
        self.image_url_queue = image_url_queue
        
    def run(self):
        while True:
            try:
                image = self.image_url_queue.get(timeout=20)
                if not os.path.exists(image['image_path']):
                    request.urlretrieve(image['image_url'], image['image_path'])
                    print(f'{image['image_path']}下载完成')
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f'下载{image['image_path']}出现错误')
                    continue
            except Empty as e:
                break
            

def get_page_json(url, headers):
    response = requests.get(url, headers=headers)
    start_index, end_index = response.text.find('(') + 1, response.text.rfind(')')
    res = json.loads(response.text[start_index:end_index])
    return res


# 启动多线程下载
def start():
    page_nums = int(get_page_json(url.format(0), headers=headers)['iTotalPages'])
    page_queue = Queue(page_nums)
    image_url_queue = Queue(200)
    for i in range(page_nums):
        page_url = url.format(i)
        page_queue.put(page_url)
        
    for j in range(5):
        th = Producer(page_queue, image_url_queue)
        th.start()
        
    for k in range(10):
        th = Customer(image_url_queue)
        th.start()
        
if __name__ == '__main__':
    start()