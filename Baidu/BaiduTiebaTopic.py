
# coding: utf-8

# 本周目标：百度贴吧的一个简单爬虫


import requests
from bs4 import BeautifulSoup
import json
from crawler.weibo_crawler.general import insert_into_mongdb
import time

def baidu_tieba_topic():
    url = 'http://tieba.baidu.com/hottopic/browse/topicList?res_type=1'
    base_url = 'https://tieba.baidu.com{}'
    session = requests.Session()
    resp = session.get(url)
    content = BeautifulSoup(resp.content, 'lxml')
    raw = content.find_all('li', {'class': "topic-top-item"})
    date = time.time()
    result = []
    for index,item in enumerate(raw):
        result.append({
            "date": date,
            "top-rank": index+1,
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
        insert_into_mongdb("baidu", "baidu_tieba_topic", item)
    return result


baidu_tieba_topic()

