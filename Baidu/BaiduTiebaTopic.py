
# coding: utf-8

# 本周目标：百度贴吧的一个简单爬虫


import requests
from bs4 import BeautifulSoup
import json
from crawler.weibo_crawler.general import insert_into_mongdb
import datetime
import re
import jieba

def baidu_tieba_topic(save_to_mongodb=False):
    url = 'http://tieba.baidu.com/hottopic/browse/topicList?res_type=1'
    base_url = 'https://tieba.baidu.com{}'
    session = requests.Session()
    resp = session.get(url)
    content = BeautifulSoup(resp.content, 'lxml')
    raw = content.find_all('li', {'class': "topic-top-item"})
    date = datetime.datetime.today().strftime("%Y-%m-%d-%H")
    result = []
    for index,item in enumerate(raw):
        file_path = 'result/{}.txt'.format(item.find('a', {'class': "topic-text"}).text)
        result.append({
            "date": date,
            "top-rank": index+1,
            'file_path': file_path,
            "topic-cover": item.find('img')['src'],
            "topic-text": item.find('a', {'class': "topic-text"}).text,
            "topic-url": item.find('a', {'class': "topic-text"})['href'],
            "topic-num": item.find('span', {'class': "topic-num"}).text,
            "topic-top-item-desc": item.find('p', {'class': "topic-top-item-desc"}).text
        })
    for index, url in enumerate(result):
        url = url['topic-url']
        resp = session.get(url)
        raw = BeautifulSoup(resp.content, 'lxml')
        result[index]['selected-feed'] = []
        for url in raw.find('div', {'id': 'selected-feed'}).find_all(
            'a', {'class': 'title track-thread-title'}):
            result[index]['selected-feed'].append(base_url.format(url['href']))
    for item in result:
        with open(item['file_path'], 'wb') as f:
            pass
        for i in item['selected-feed']:
            get_content(i, item['file_path'])
        if save_to_mongodb:
            insert_into_mongdb("baidu", "baidu_tieba_topic", item)
    return result


def get_content(url, file_path):
    url = url.split('?')[0]
    session = requests.Session()
    resp = session.get(url)
    content = BeautifulSoup(resp.content, 'lxml')
    try:
        page = int(content.find('li', {'class': 'l_reply_num'}).find_all('span')[1].text)
    except Exception:
        print(url)
    else:
        current_page = 1
        all_word = ''
        while current_page <= page:
            current_url = url + '?pn=' + str(current_page)
            resp = session.get(current_url)
            content = BeautifulSoup(resp.content, 'lxml').find('div', {'class': 'p_postlist'})
            content = content.find_all('div', {'class': ['l_post', 'l_post_bright', 'j_l_post clearfix']})
            for i in content:
                i = i['data-field']
                try:
                    i = json.loads(i)['content']['content']
                except Exception:
                    pass
                else:
                    i = re.sub(r'(\<img .*?\>)', '', i)
                    i = re.sub(r'(\<a href.*?\>.*?\<\/a\>)', '', i)
                    i = re.sub(r'(\<br\>)', '', i)
                    i = re.sub(r'(\<div.*?\>.*?\<\/div\>)', '', i)
                    if 'video' in i:
                        print(i)
                    if i != '':
                        all_word += " ".join(jieba.cut(i, cut_all=True))
            current_page += 1
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(all_word)


baidu_tieba_topic(save_to_mongodb=False)
