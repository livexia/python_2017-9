# -*- coding: UTF-8 -*-

import time
import rsa
import binascii
import base64
import re
import json
import os
import sys
import http.cookiejar
import urllib.request
import urllib.parse
import gzip
from io import StringIO
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import lxml
import random
# from PIL import Image
import subprocess
from selenium import webdriver
from General import *
from PIL import Image
import subprocess




def login1(username, password):
    print('这里是login1')
    username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36","Content-Type": "application/x-www-form-urlencoded","Host": "login.sina.com.cn", "Origin": "http://open.weibo.com", "Referer": "http://open.weibo.com/wiki/%E6%8E%88%E6%9D%83%E6%9C%BA%E5%88%B6%E8%AF%B4%E6%98%8E","Upgrade-Insecure-Requests": "1", "Accept-Encoding": "gzip"
    }  # 头
    postData = {
        "entry": "mweibo",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1920*1080",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }  # 请求的表单数据
    loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
    session = requests.Session()
    res = session.post(loginURL, data=postData, headers = headers)
    jsonStr = res.content.decode('gbk')
    print(jsonStr)
    exit()
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        res1 = session.get(info['crossDomainUrlList'][0]).content.decode('gb2312')
        print(info['crossDomainUrlList'][0])
        exit(0)
        jsonStr = re.findall(r'\((\{.*?\})\)', res1)[0]
        login_data = json.loads(jsonStr)
        print(login_data)
        if login_data['result']:
            print("登录成功！")
            # 把cookies添加到headers中
            cookies = session.cookies.get_dict()
            cookies = [key + "=" + value for key, value in cookies.items()]
            cookies = "; ".join(cookies)
            session.headers["cookie"] = cookies
        else:
            print("登陆失败")
    else:
        print("登录失败，原因： %s" % info["reason"])
    return session


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


def login2(username, password):
    print('这里是login2')
    cookie = http.cookiejar.CookieJar()
    cookieproc = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookieproc)
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36"),
                         ("Content-Type", "application/x-www-form-urlencoded"),
                         ("Host", "login.sina.com.cn"),
                         ("Origin", "http://open.weibo.com"),
                         ("Referer", "http://open.weibo.com/wiki/%E6%8E%88%E6%9D%83%E6%9C%BA%E5%88%B6%E8%AF%B4%E6%98%8E"),
                         ("Upgrade-Insecure-Requests", "1")
                         ]  #头

    su = encode_username(username)

    url_prelogin = 'https://login.sina.com.cn/sso/prelogin.php?entry=account&callback=sinaSSOController.preloginCallBack&su=MTU5Njg4MDE2NDY%3D&rsakt=mod&client=ssologin.js(v1.4.15)'
    url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js'

    resp_prelogin = opener.open(url_prelogin).read().decode('utf-8')
    jsonStr = re.findall(r'\((\{.*?\})\)', resp_prelogin)[0]
    data = json.loads(jsonStr)
    sp = encode_password(password,data['servertime'],data['nonce'],data['pubkey'])

    postdata = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'userticket': '1',
        'ssosimplelogin': '1',
        'vsnf': '1',
        'vsnval': '',
        'su': su,
        'service': 'miniblog',
        'servertime': data['servertime'],
        'nonce': data['nonce'],
        'pwencode': 'rsa2',
        'sp': sp,
        'encoding': 'UTF-8',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META',
        'rsakv': data['rsakv'],
    }

    resp_login = opener.open(url_login, urllib.parse.urlencode(postdata).encode('utf-8')).read().decode('gbk')
    if re.findall(r"reason\=(.*?)\"", resp_login):
        print('登陆失败：' +
              urllib.parse.unquote_to_bytes(re.findall(r"reason\=(.*?)\"", resp_login)[1]).decode('gb2312') +
              '\n错误代码：' +
              re.findall(r"retcode\=(.*?)\&", resp_login)[0])
    else:
        info = re.findall(r"location\.replace\(\'(.*?)\'", resp_login)[0]
        print(info)
        exit()
        resp_my = opener.open(info).read().decode('gb2312')
        jsonStr = re.findall(r'\((\{.*?\})\)', resp_my)[0]
        login_data = json.loads(jsonStr)
        if login_data['result']:
            print("登录成功！")
            print('用户唯一id：' + login_data['userinfo']['uniqueid'])
        else:
            print("登录失败！")
    return opener

def login_towap(username, password):
    print("这里是login_towap")
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
    postData = {
        "username": username,
        "password": password,
        "savestate": "1",
        "r": "http://weibo.cn/",
        "ec": "0",
        "pagerefer": "",
        "entry": "mweibo",
        "wentry": "",
        "loginfrom": "",
        "client_id": "",
        "code": "",
        "qq": "",
        "mainpageflag": "1",
        "hff": "",
        "hfp": ""
    }
    url_prelogin = r'https://login.sina.com.cn/sso/prelogin.php?checkpin=1&entry=mweibo&su=' + base64.b64encode(username.encode(encoding="utf-8")).decode('utf-8') + '&callback=jsonpcallback'
    loginURL = r'https://passport.weibo.cn/sso/login'
    session = requests.Session()

    pre_login=session.get(url_prelogin).content.decode('gbk')
    prelogin_info = json.loads(re.findall(r'\((\{.*?\})\)', pre_login)[0])
    if prelogin_info['showpin'] == 1:
        print('需要输入验证码')
        postData.update(process_verify_code(session, prelogin_info['pcid']))
    print(postData)

    resp = session.post(loginURL, data=postData, headers=headers)
    jsonStr = resp.content.decode('gbk')
    info = json.loads(jsonStr)
    print(info)

    if info["retcode"] == 20000000:
        status = 0
        urllist = info['data']['crossdomainlist'].values()
        for url in urllist:
            resp = session.get(url)
            if '"retcode":20000000' in resp.text:
                status += 1
        if status == 3:
            print("登录成功！")
            cookies = session.cookies.get_dict()
            cookies = [key + "=" + value for key, value in cookies.items()]
            cookies = "; ".join(cookies)
            session.headers["cookie"] = cookies
        else:
            print("登陆失败")
            exit()
    # else:
    #     print("登录失败，原因： %s" % info["msg"])
    #     exit()
    return session

def login(username, password):
    print('这里是login')
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
        else:
            print("登录失败！")

    return session

#TODO:对wap端抓取数据
def get_html(session, url, savetofile = True):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://open.weibo.com",
        "Upgrade-Insecure-Requests": "1", "Accept-Encoding": "gzip"
        }

    uid = re.findall(r'weibo[\.\/][comn\/u]*\/([0-9]*)', url)[0]
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

    print(page)

    #TODO:获取用户微博主体信息
    if savetofile:
        with open(filepath, 'w', encoding='utf-8') as f:
            pass
    for i in range(1, page + 1):
        url_with_page = url + '?page={}'.format(i)
        print("正在爬取第{}页！".format(i))
        resp = session.get(url_with_page)
        soup = BeautifulSoup(resp.content, 'lxml')
        weibolist = soup.find_all("div", {"class", "c"})
        weibolist.pop(0)
        weibolist.pop()
        weibolist.pop()
        weibo_dict = {}
        j = 0
        for item in weibolist:
            weibo_dict = {}
            weibo = []
            weiboinfo = []
            for span in item.find_all("span"):
                weibo.append(span.text)
                try:
                    if span.find('a') != None:
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
            weibo_dict['content'] = weibo
            weibo_dict['weiboinfo'] = weiboinfo
            print(u"\u2714", end = "")
            insert_into_mongdb("weibo", "weibocontents", weibo_dict)
            j += 1
            if savetofile:
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(weibo_dict))
        time.sleep(2)




#PhantomJs+Selenium的学习部分
def get_html_by_webdriver(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://open.weibo.com",
        "Upgrade-Insecure-Requests": "1", "Accept-Encoding": "gzip"
        }
    html = None
    retry = 3
    while (retry > 0):
        try:
            resp = session.get(url, headers = headers)
            srchtml = resp.text
            filepath = 'result/' + re.findall(r'com\/([0-9]*)', url)[0] + '.html'
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(srchtml)
            browser = webdriver.PhantomJS()
            filepath = os.path.abspath(filepath)
            browser.get('file:///' + filepath)
            html = browser.page_source
            browser.quit()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            soup = BeautifulSoup(resp.content, 'lxml')
            username = soup.find_all("h1", {"class", "username"})
            print(username)
            break
        except requests.RequestException as e:
            print('url error:', e)
            retry = retry - 1
            continue
        except Exception as e:
            print('error:', e)
            retry = retry - 1
            continue
    return html

#入口
def main():
    print('请登录微博！')
    if sys.argv[1] == '' or sys.argv[2] == '':
        username = input('输入账号：')
        password = input('输入密码：')
    else:
        username = sys.argv[1]
        password = sys.argv[2]
    opener = login(username, password)
    # url = r'https://weibo.com/212319908'  #pc端
    # url = r'https://m.weibo.cn/u/2761139954'  #mobile端
    # url1 = r'https://weibo.cn/2761139954'     #wap端
    url = [
        r'https://weibo.cn/2761139954',
        r'https://weibo.cn/1765335300'
    ]
    # get_html_by_webdriver(opener, url)
    for u in url:
        get_html(opener, u, True)


main()