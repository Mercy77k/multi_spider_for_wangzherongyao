import requests
import json
from urllib import parse
from urllib import request
import urllib.error
import time
import os

def get_page_json(url, headers):
    response = requests.get(url, headers=headers)
    start_index, end_index = response.text.find('(') + 1, response.text.rfind(')')
    res = json.loads(response.text[start_index:end_index])
    return res


def decoding_url(url):
    return parse.unquote(url)

def extract_image_url(image_obj):
    image_url = []
    for index in range(1, 9):
        image_url.append(decoding_url(image_obj[f'sProdImgNo_{index}'])[:-3] + '0')
    return image_url


def get_every_image_url(response_json):
    image_url_dict = {}
    for image_obj in response_json['List']:
        key = decoding_url(image_obj['sProdName']) + '_' +image_obj['iProdId']
        if key in image_url_dict:
            i = 2
            new_key = key + f'_{i}'
            while new_key in image_url_dict:
                i += 1
                new_key = key + f'_{i}'
            image_url_dict[new_key] = extract_image_url(image_obj)
        else:
            image_url_dict[key] = extract_image_url(image_obj)
            
    return image_url_dict

def get_pages_nums(url, headers):
    response = get_page_json(url, headers=headers)
    pages_nums = response['iTotalPages']
    return pages_nums

def save_image(total_image_url_dict):
    floder_name = 'images'
    if not os.path.exists(floder_name):
        os.mkdir(floder_name)
        print(f'创建文件夹{floder_name}')
    
    for key in total_image_url_dict:
        dir_path = os.path.join(floder_name, key.strip(' '))
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            print(f'创建文件夹{dir_path}')
        for index, image_url in enumerate(total_image_url_dict[key]):
            try:
                image_path = os.path.join(dir_path, f'{index+1}.jpg')
                if not os.path.exists(image_path):
                    request.urlretrieve(image_url, image_path)
                    print('{}下载完毕'.format(total_image_url_dict[key][index]))
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f'下载{image_path}出现异常，跳过')
                    continue
                
def count_files_in_directories(base_path='./images'):
    result = {}
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)
        if os.path.isdir(full_path):
            file_count = sum([len(files) for _, _, files in os.walk(full_path)])
            if file_count > 8:
                result[entry] = file_count
    return result

                
if __name__ == "__main__":
    headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'referer': 'https://pvp.qq.com/'
    }
    url = 'https://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi?activityId=2735&sVerifyCode=ABCD&sDataType=JSON&iListNum=20&totalpage=0&page=0&iOrder=0&iSortNumClose=1&jsoncallback=jQuery111307407747907683988_1746689540190&iAMSActivityId=51991&_everyRead=true&iTypeId=2&iFlowId=267733&iActId=2735&iModuleId=2735&_=1746689540192'
    url_temp = 'https://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi?activityId=2735&sVerifyCode=ABCD&sDataType=JSON&iListNum=20&totalpage=0&page={}&iOrder=0&iSortNumClose=1&jsoncallback=jQuery111307407747907683988_1746689540190&iAMSActivityId=51991&_everyRead=true&iTypeId=2&iFlowId=267733&iActId=2735&iModuleId=2735&_=1746689540192'
    
    # total_image_url_list = {}
    for i in range(int(get_pages_nums(url, headers))):
        page_json = get_page_json(url_temp.format(i), headers=headers)
        image_url_dict = get_every_image_url(page_json)
        
        # print(f'{i}:{len(image_url_dict)}')
        # total_image_url_list.update(image_url_dict)
        
        save_image(image_url_dict)
    
    # print(len(total_image_url_list))
    # for key in total_image_url_list:
    #     print(key, total_image_url_list[key])
    
    
    # filtered_dirs = count_files_in_directories()
    # for dirname, count in filtered_dirs.items():
    #     print(f"目录: {dirname}，文件数: {count}")

    


    
    
    
    