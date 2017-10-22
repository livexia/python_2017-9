import re
import json
import base64
import rsa
import binascii
import time
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar

class Sina_login():
    def __init__(self, username = None, password = None):
        self.username = username
        self.password = password
        self.servertime = None
        self.nonce = None
        self.pubkey = None
        self.rsakv = None
        self.post_data = {}
        self.headers = []
        self.proxy_url = {'http': 'http://127.0.0.1:1080/'}  # 用户代理地址
        self.cookie = None #http.cookiejar.CookieJar()
        self.opener = None

    def get_data(self, username, password):
        self.headers = [('Origin','https://login.sina.com.cn'),
                        ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0'),
                        ('Referer','https://weibo.com/')
                        ]
        self.username = urllib.parse.quote_plus(username)
        # 用户名base64加密
        self.username = base64.b64encode(self.username.encode("utf-8"))
        self.username = self.username.decode()

        self.password = password
        pre_login_params = {
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.19)",
            "su": self.username,
            "_": int(time.time() * 1000),
        }
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        self.opener = urllib.request.build_opener() #预获取数据不加cookie，不加代理
        self.opener.addheaders = self.headers
        while 1:
            count = 0
            try:
                pre_login = self.opener.open(url, pre_login_params).read().decode("utf8")  # 不传入参数第一次对登陆页面发起请求获取隐藏参数
            except urllib.error.HTTPError as e:
                print("Error Code: ", e.code)
                count += 1
            except urllib.error.URLError as e:
                print("Reason: ", e.reason)
                count += 1
            else:
                print("获取prelogin.php 成功")
                break
            if count == 5:  # 当错误计数达到五个时退出循环
                print("获取prelogin.php 失败")
                exit()
        jsonStr = re.findall(r'\((\{.*?\})\)', pre_login)[0]
        data = json.loads(jsonStr)
        servertime = data["servertime"]
        nonce = data["nonce"]
        pubkey = data["pubkey"]
        rsakv = data["rsakv"]

        #密码rsa加密
        rsaPubkeyHead = int(pubkey, 16) #pubkey十六进制转十进制
        rsaPubkeyTail = int('10001', 16) #'10001'十六进制转十进制
        rsaPubkey = rsa.PublicKey(rsaPubkeyHead, rsaPubkeyTail)
        password = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
        password = rsa.encrypt(password.encode("utf-8"),rsaPubkey)
        password = binascii.b2a_hex(password)   #最后的密文以十六进制输出

        self.password = password.decode()
        self.servertime = servertime
        self.nonce = nonce
        self.pubkey = pubkey
        self.rsakv = rsakv

        self.post_data = {
            "cdult": "3",
            "domain": "sina.com.cn",
            "encoding": "UTF-8",
            "entry": "sso",
            "from": "null",
            "gateway": "1",
            "pagerefer": "",
            "prelt": "0",
            "returntype": "TEXT",
            "savestate": "30",
            "service": "sso",
            "sp": self.password,
            "sr": "1920*1080",
            "su": self.username,
            "useticket": "0",
            "vsnf": "1"
        }

        return self

    def login(self):
        username = input("输入用户名：")
        password = input("输入密码：")
        self.get_data(username,password)
        login_url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        self.cookie = http.cookiejar.CookieJar()
        cookieproc = urllib.request.HTTPCookieProcessor(self.cookie)
        proxy_handler = urllib.request.ProxyHandler(self.proxy_url)
        self.opener = urllib.request.build_opener(cookieproc, proxy_handler)
        self.opener.addheaders = self.headers
        post_data = urllib.parse.urlencode(self.post_data).encode('UTF8')
        print(post_data)

        while 1:
            count = 0
            try:
                response = self.opener.open('https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)', post_data)  # 登陆页面传入post参数，成功登陆，保留cookie
            except urllib.error.HTTPError as e:
                print("Error Code: ", e.code)
                count += 1
            except urllib.error.URLError as e:
                print("Reason: ", e.reason)
                count += 1
            else:
                print(response.read().decode('utf-8', 'ignore'))
                print("登陆 成功")
                break
            if count == 5:  # 当错误计数达到五个时退出循环
                print("登陆 失败")
                exit()

    def openurl(self, url, post_data = None):
        url_content = self.opener.open(url, post_data).read().decode('utf-8').strip()
        print(url_content)









test = Sina_login()
test.login()
test.openurl('https://weibo.cn/5643396361/info')   #打开我的个人信息页面验证登陆是否成功