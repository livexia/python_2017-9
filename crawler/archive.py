import http.cookiejar
import urllib.request
import urllib.parse
import re
import json
import base64
import requests

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

    #TODO 验证码输入
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

# TODO PhantomJs+Selenium的学习部分
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
