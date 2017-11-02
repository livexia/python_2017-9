import requests
import time
import json

def get_proxy():
    return requests.get("http://127.0.0.1:32771/get/").content.decode()

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:32771/delete/?proxy={}".format(proxy))

def getHtml():
    proxy = get_proxy()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    }
    print("http://{}".format(proxy))
    html = requests.get('http://httpbin.org/ip', proxies={"http": "http://{}".format(proxy)}, timeout=20, verify=False)
    print('访问的代理地址为：' + html.content.decode())
    return html
    # delete_proxy(proxy)
    # return None

def get_proxy_pool_status():
    return requests.get("http://127.0.0.1:32771/get_status/").content.decode('utf-8')


if __name__ == '__main__':
    while 1:
        getHtml()
        time.sleep(10)
        if '"useful_proxy": 120' in get_proxy_pool_status():
            break
