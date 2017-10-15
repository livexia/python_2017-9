import re
import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar


def login_csdn():
    proxy_handler = urllib.request.ProxyHandler({'http': 'http://127.0.0.1:1080/'}) #用户代理
    cookie = http.cookiejar.CookieJar()
    cookieproc = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(cookieproc, proxy_handler)
    opener.addheaders = [('Origin', 'https://passport.csdn.net'),
                         ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'),
                         ('Referer', 'https://passport.csdn.net/account/login?from=http%3A%2F%2Fmy.csdn.net%2Fmy%2Fmycsdn')
                         ]  #添加头

    while 1:
        count = 0
        try:
            h = opener.open('https://passport.csdn.net').read().decode("utf8")  # 不传入参数第一次对登陆页面发起请求获取隐藏参数
        except urllib.error.HTTPError as e:
            print("Error Code: ", e.code)
            count += 1
        except urllib.error.URLError as e:
            print("Reason: ", e.reason)
            count += 1
        else:
            print("不传入参数第一次对登陆页面发起请求获取隐藏参数 成功")
            break
        if count == 5:  # 当错误计数达到五个时退出循环
            print("不传入参数第一次对登陆页面发起请求获取隐藏参数 失败")
            exit()

    patten1 = re.compile(r'name="lt" value="(.*?)"')        #利用正则表达式获取隐藏参数lt
    patten2 = re.compile(r'name="execution" value="(.*?)"') ##利用正则表达式获取隐藏参数execution
    b1 = patten1.search(h)      #匹配页面
    b2 = patten2.search(h)      #
    username = input("输入csdn用户名：")
    password = input("输入csdn密码：")
    postData = {
        'username': username,       #csdn用户名
        'password': password,       #csdn密码
        'lt': b1.group(1),        #第一个隐藏参数
        'execution': b2.group(1), #第二个隐藏参数
        '_eventId': 'submit',     #第三个隐藏参数
    }
    postData = urllib.parse.urlencode(postData).encode('UTF8')  #转换post参数
    # response = opener.open('https://passport.csdn.net', postData) #登陆页面传入post参数，成功登陆，保留cookie

    while 1:
        count = 0
        try:
            response = opener.open('https://passport.csdn.net', postData)  # 登陆页面传入post参数，成功登陆，保留cookie
        except urllib.error.HTTPError as e:
            print("Error Code: ", e.code)
            count += 1
        except urllib.error.URLError as e:
            print("Reason: ", e.reason)
            count += 1
        else:
            print("登陆 成功")
            break
        if count == 5:  # 当错误计数达到五个时退出循环
            print("登陆 失败")
            exit()
    #以下爬取需要登录的内容

    #在这里我展示爬取个人信息。我设置了个人信息不可见，仅在本人登陆时可见。

    while 1:
        count = 0
        try:
            response2 = opener.open('http://my.csdn.net/')
        except urllib.error.HTTPError as e:
            print("Error Code: ", e.code)
            count += 1
        except urllib.error.URLError as e:
            print("Reason: ", e.reason)
            count += 1
        else:
            print("访问页面 成功")
            break
        if count == 5:  # 当错误计数达到五个时退出循环
            print("访问页面 失败")
            exit()

    # response2 = opener.open('http://my.csdn.net/')
    text2 = response2.read().decode('utf-8', 'ignore')
    patten3 = re.compile(r'<dd class="person-detail">((?:.|\n)*?)</dd>')    #匹配用户个人信息正则表达式
    person_detail = patten3.search(text2).group(1).strip().split("<span>|</span>")  #格式化输出
    print(person_detail)


login_csdn()