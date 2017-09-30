import urllib.request
import urllib.error
import urllib.parse
import time


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

data = urllib.parse.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0}).encode('utf-8')
headers = {'User-Agent': user_agent }

proxy_handler = urllib.request.ProxyHandler({'http': 'http://127.0.0.1:1080/'})     #新建代理
proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()     #设置基础认证
proxy_auth_handler.add_password('realm', 'host', 'username', 'password')    #添加认证密钥
opener = urllib.request.build_opener(proxy_handler)         #设置认证
opener.addheaders = [('User-Agent', user_agent)]        #添加headers

count = 0
while 1:
    try:
        Req = opener.open('http://ident.me', data)
    except urllib.error.HTTPError as e:
        print("Error Code: ",e.code)
        count += 1
    except urllib.error.URLError as e:
        print("Reason: ",e.reason)
        count += 1
    else:
        print(Req)
        break
    if count == 5:      #当错误计数达到五个时退出循环
        break



with open("result.txt",'wt') as f:
    urlinfo = Req.info()
    website = Req.read()
    print(urlinfo)
    print(website)
    print(urlinfo, file=f)
    print(website,file=f)

