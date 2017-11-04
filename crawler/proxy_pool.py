# -*- coding: UTF-8 -*-

import requests
import time
import json
import re

def get_proxy():
    return requests.get("http://115.159.124.234:32769/get/").content.decode()

def delete_proxy(proxy):
    requests.get("http://115.159.124.234:32769/delete/?proxy={}".format(proxy))

def getHtml():
    retry_count = 2
    proxy = get_proxy()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    print("Try proxy:{}".format(proxy))
    useable_ip = []
    while retry_count > 0:
        try:
            # 使用代理访问
            html = requests.get('http://ident.me/', proxies={"http": "http://{}".format(proxy)}, headers = headers, timeout=20, verify=False)
            print(html.status_code,html.text())
            return html
        except Exception as e:
            retry_count -= 1
    # 出错3次, 删除代理池中代理
    delete_proxy(proxy)
    print("Delete proxy:{}".format(proxy))
    return None

def get_proxy_pool_status():
    return requests.get("http://115.159.124.234:32769/get_status/").content.decode('utf-8')


if __name__ == '__main__':
    while 1:
        getHtml()
        time.sleep(0.5)
        # print("剩余可用IP数：" + str(json.loads(get_proxy_pool_status())["useful_proxy"]))
        # if '"useful_proxy": 0' in get_proxy_pool_status():
        #     break
