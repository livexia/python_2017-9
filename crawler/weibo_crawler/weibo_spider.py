# -*- coding: UTF-8 -*-


import sys
import requests
from bs4 import BeautifulSoup
import traceback
import time
from general import *


class WeiboSpider():
    stopinfo = []
    session = requests.Session()

    def __init__(self, stopinfo):
        self.stopinfo = stopinfo

    def get_html(self, url, savetofile=True):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://open.weibo.com",
            "Upgrade-Insecure-Requests": "1", "Accept-Encoding": "gzip"
            }

        if self.stopinfo['page'] == '-1':
            uid = re.findall(r'weibo[\.\/][comn\/u]*\/([0-9]*)', url)[0]
            lastpage = 1
            info_url = 'https://weibo.cn/' + uid + '/info'
            resp = self.session.get(info_url)
            # print(resp.text)
            soup = BeautifulSoup(resp.content, 'lxml')
            info_dict = {}
            info_dict['_id'] = uid
            for item in soup.find_all("div", {'class': 'c'})[3].find_all('br'):
                info = item.previous_sibling
                info = re.split(r"[:\：]", info, 1)
                info_dict[info[0]] = info[1]
                if "简介" in info:
                    break
            insert_into_mongdb("weibo", "userinfo", info_dict)
        else:
            uid = self.stopinfo['uid']
            lastpage = int(self.stopinfo['page'])

        resp = self.session.get(url)
        soup = BeautifulSoup(resp.content, 'lxml')
        page = int(soup.find("div", id="pagelist").find("input", type="hidden")['value'])  # 获取微博静态页数
        self.stopinfo['total_page'] = page

        filepath = 'result/' + self.stopinfo['uid'] + '.json'
        self.stopinfo['uid'] = uid

        if savetofile:
            create_file(filepath)
        try:
            for i in range(lastpage, page + 1):
                json_to_file('breakpoint.json', self.stopinfo)
                url_with_page = url + '?page={}'.format(i)
                print("正在爬取第{}页！".format(i))
                try:
                    proxy = get_proxy()
                    html = requests.get('https://ident.me/', proxies=proxy)
                    if html.text == re.findall(r'\/\/(.*?)\:', proxy)[0]:
                        proxy = get_proxy()
                    else:
                        proxy = None
                except Exception:
                    proxy = None
                resp = self.session.get(url_with_page, proxies=proxy)
                soup = BeautifulSoup(resp.content, 'lxml')
                weibolist = soup.find_all("div", {"class", "c"})
                weibolist.pop(0)
                weibolist.pop()
                weibolist.pop()
                j = 0
                for item in weibolist:
                    weibo_dict = {}
                    weibo = []
                    weiboinfo = []
                    for span in item.find_all("span"):
                        weibo.append(span.text)
                        try:
                            if span.find('a'):
                                weibo.append(span.find("a")['href'])
                        except Exception as e:
                            print("\nerror: ", e)
                            print(span.text)
                            exit()
                    for a in item.find_all("a"):
                        if a.text == "原图":
                            weibo.append("图片：" + a['href'])
                        elif a.text != "收藏" and a.text != '':
                            weiboinfo.append(a.text)
                    weibo_dict['_id'] = item.get('id')
                    weibo_dict['uid'] = uid
                    self.stopinfo['_id'] = weibo_dict['_id']
                    weibo_dict['content'] = weibo
                    weibo_dict['weiboinfo'] = weiboinfo
                    print(u"\u2714", end = "")
                    insert_into_mongdb("weibo", "weibocontents", weibo_dict)
                    j += 1
                    if savetofile:
                        append_json_to_file(filepath, weibo_dict)
                self.stopinfo['page'] = str(i)
                time.sleep(2)
            return ['0','0','']
        except Exception as e:
            print(traceback.format_exc())
