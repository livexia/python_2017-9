# -*- coding: UTF-8 -*-
from pymongo import MongoClient
import requests
import traceback
import re

def insert_into_mongdb(database, col, data):
    client = MongoClient('localhost',27018)
    db = client.get_database(database)
    collection = db.get_collection(col)
    try:
        col_id = collection.save(data)
        print(col_id)
    except Exception as e:
        print(r'Insert into mongodb error: ', e)
    finally:
        return 0

def get_proxy():
    ip = requests.get("http://127.0.0.1:32771/get/").text
    proxy = {
        'http': 'http://{}'.format(ip),
        'https': 'http://{}'.format(ip)
             }
    return proxy

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:32771/delete/?proxy={}".format(proxy))

# your spider code

def getHtml():
    try:
        proxy = get_proxy()
        html = requests.get('https://ident.me/', proxies=proxy)
        if html.text == re.findall(r'\/\/(.*?)\:', proxy)[0]:
            return 'success,ip = {}'.format(html.text)
        else:
            return 'error'
    except Exception:
        return 'error'

while 1:
    print(getHtml())