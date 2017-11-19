# -*- coding: UTF-8 -*-

import time
import rsa
import binascii
import base64
import re
import json
import os
import sys
import urllib.request
import urllib.parse
import requests
from bs4 import BeautifulSoup
import random
from selenium import webdriver
from General import *
from PIL import Image
import subprocess
import traceback


def process_verify_code(session, pcid):
    url = 'http://login.sina.com.cn/cgi/pin.php?r={randint}&s=0&p={pcid}'.format(
        randint=int(random.random() * 1e8), pcid=pcid)
    filename = 'crawler/image/verify_code/{}.png'.format(pcid)
    if os.path.isfile(filename):
        os.remove(filename)
    resp = session.get(url)
    if resp.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(resp.content)
    if os.path.isfile(filename):  # get verify code successfully
        with Image.open(filename) as verify_code:
            verify_code.show()
            code = input('请输入验证码:')
        os.remove(filename)
        return dict(pcid=pcid, door=code)
    else:
        return dict()


def encode_password(password, servertime, nonce, pubkey):
    rsaPubkey = int(pubkey, 16)
    RSAKey = rsa.PublicKey(rsaPubkey, 65537)  # 创建公钥
    codeStr = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 根据js拼接方式构造明文
    pwd = rsa.encrypt(codeStr.encode('utf-8'), RSAKey)  # 使用rsa进行加密
    return binascii.b2a_hex(pwd)  # 将加密信息转换为16进制。


def encode_username(username):
    su = base64.b64encode(username.encode(encoding="utf-8"))
    return su


def login(username, password):
    print('这里是login')
    ticket = None
    headers = {
        'Host': 'passport.weibo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept': '*/*',
        'Accept-Language':
            'zh-CN,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=',
        'Connection': 'keep-alive'
    }

    session = requests.Session()
    su = encode_username(username)

    preData = {
        "entry": "sso",
        "callback": "sinaSSOController.preloginCallBack",
        "su": su,
        "rsakt": "mod",
        "checkpin": "1",
        "client": "ssologin.js(v1.4.15)",
        "_": int(time.time() * 1000)
    }

    url_prelogin = 'https://login.sina.com.cn/sso/prelogin.php'
    url_login = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js'
    prelogin = session.get(url_prelogin, params=preData).content.decode('gbk')
    prelogin_info = json.loads(re.findall(r'\((\{.*?\})\)', prelogin)[0])
    sp = encode_password(password, prelogin_info['servertime'], prelogin_info['nonce'], prelogin_info['pubkey'])

    if prelogin_info['showpin'] == 1:
        print('需要输入验证码')
        postData = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'pcid': '',
            'door': '',
            'vsnf': '1',
            'vsnval': '',
            'su': su,
            'service': 'miniblog',
            'servertime': prelogin_info['servertime'],
            'nonce': prelogin_info['nonce'],
            'pwencode': 'rsa2',
            'sp': sp,
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
            'rsakv': prelogin_info['rsakv'],
        }
        postData.update(process_verify_code(session, prelogin_info['pcid']))
    else:
        postData = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'pcid': '',
            'door': '',
            'vsnf': '1',
            'vsnval': '',
            'su': su,
            'service': 'miniblog',
            'servertime': prelogin_info['servertime'],
            'nonce': prelogin_info['nonce'],
            'pwencode': 'rsa2',
            'sp': sp,
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
            'rsakv': prelogin_info['rsakv'],
        }

    resp_login = session.post(url_login, data=postData)
    final_url = re.findall(r'(http[^s].*?)\"\)', resp_login.text)[0].replace("%2F", "/").replace("%3F", "?").replace("%3D", "=").replace("%26", "&").replace("%3A",":")
    resp_final = session.get(final_url)

    if re.findall(r"reason\=(.*?)\"", resp_login.text):
        print('登陆失败：' +
              urllib.parse.unquote_to_bytes(re.findall(r"reason\=(.*?)\"", resp_login.text)[1]).decode('gb2312') +
              '\n错误代码：' +
              re.findall(r"retcode\=(.*?)\&", resp_login.text)[0])
    else:
        jsonStr = re.findall(r'\((\{.*?\})\)', resp_final.text)[0]
        login_data = json.loads(jsonStr)
        if login_data['result']:
            print("登录成功！")
            print('用户唯一id：' + login_data['userinfo']['uniqueid'])

            loginurl = "https://login.sina.com.cn/sso/login.php?url=https%3A%2F%2Fweibo.cn%2Fpub%2F"
            url = session.get(loginurl).text
            url = re.findall(r"(https.*?)\"\)", url)[0]
            if "登陆" not in session.get(url).text:
                print("登陆阶段完成")
            else:
                print("登陆阶段失败")
        else:
            print("登录失败！")
    return session


def get_html(session, url, stopinfo, savetofile=True):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://open.weibo.com",
        "Upgrade-Insecure-Requests": "1", "Accept-Encoding": "gzip"
        }

    if stopinfo[1] == '0':
        uid = re.findall(r'weibo[\.\/][comn\/u]*\/([0-9]*)', url)[0]
    else:
        uid = stopinfo[1]
    lastpage = int(stopinfo[0])
    info_url = 'https://weibo.cn/' + uid + '/info'
    filepath = 'crawler/result/' + re.findall(r'weibo[\.\/][comn\/u]*\/([0-9]*)', url)[0] + '.json'
    resp = session.get(info_url)
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

    resp = session.get(url)
    soup = BeautifulSoup(resp.content, 'lxml')
    page = int(soup.find("div", id="pagelist").find("input", type = "hidden")['value'])   #获取微博静态页数

    if savetofile:
        with open(filepath, 'w', encoding='utf-8') as f:
            pass
    if lastpage == 0:
        lastpage += 1
    try:
        for i in range(lastpage, page + 1):
            url_with_page = url + '?page={}'.format(i)
            print("正在爬取第{}页！".format(i))
            resp = session.get(url_with_page)
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
                stopinfo[1] = uid
                stopinfo[2] = weibo_dict['_id']
                weibo_dict['content'] = weibo
                weibo_dict['weiboinfo'] = weiboinfo
                print(u"\u2714", end = "")
                insert_into_mongdb("weibo", "weibocontents", weibo_dict)
                j += 1
                if savetofile:
                    with open(filepath, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(weibo_dict))
            stopinfo[0] = str(i)
            # print(stopinfo[0],stopinfo[1])
            time.sleep(2)
        return ['0','0','']
    except Exception as e:
        print(traceback.format_exc())
        return stopinfo



#入口
def main():
    print('请登录微博！')
    if sys.argv[1] == '' or sys.argv[2] == '':
        username = input('输入账号：')
        password = input('输入密码：')
    else:
        username = sys.argv[1]
        password = sys.argv[2]
    session = login(username, password)

    time.sleep(5)

    pageinfo = input("输入断点(输入0,0(页数，用户id)表示取消断点)：").split(',')

    pageinfo.append('0')
    print(type(pageinfo[0]))
    url = [
        r'https://weibo.cn/2761139954',
        r'https://weibo.cn/1765335300'
    ]
    for u in url:
        pageinfo = get_html(session, u, pageinfo, True)


main()