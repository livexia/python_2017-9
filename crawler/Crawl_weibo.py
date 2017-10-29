import rsa
import binascii
import base64
import re
import json
import http.cookiejar
import urllib.request
import urllib.parse
import requests


def login1(username, password):
    print('这里是login1')
    username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
    session = requests.Session()
    res = session.post(loginURL, data = postData)
    jsonStr = res.content.decode('gbk')
    info = json.loads(jsonStr)
    print(info)
    if info["retcode"] == "0":
        res1 = session.get(info['crossDomainUrlList'][0]).content.decode('gb2312')
        jsonStr = re.findall(r'\((\{.*?\})\)', res1)[0]
        login_data = json.loads(jsonStr)
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


def encode_password(password, servertime, nonce, pubkey):
    rsaPubkey = int(pubkey, 16)
    RSAKey = rsa.PublicKey(rsaPubkey, 65537) #创建公钥
    codeStr = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #根据js拼接方式构造明文
    pwd = rsa.encrypt(codeStr.encode('utf-8'), RSAKey)  #使用rsa进行加密
    return binascii.b2a_hex(pwd)  #将加密信息转换为16进制。

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
                         ]

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
        resp_my = opener.open(info).read().decode('gb2312')
        jsonStr = re.findall(r'\((\{.*?\})\)', resp_my)[0]
        login_data = json.loads(jsonStr)
        if login_data['result']:
            print("登录成功！")
            print('用户唯一id：' +
                  login_data['userinfo']['uniqueid'])
        else:
            print("登录失败！")
    return opener

if __name__ == '__main__':
    print('请登录微博！')
    username = input('输入账号：')
    password = input('输入密码：')
    opener = login1(username,password)