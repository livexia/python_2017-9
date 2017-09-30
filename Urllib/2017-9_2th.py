import urllib.request
import urllib.error
import urllib.parse
import re
import socket
import socks

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

url = "https://steamspy.com"
data = b''
headers = { 'User-Agent' : user_agent }

proxy_handler = urllib.request.ProxyHandler({'http': 'http://127.0.0.1:1080/'})
# proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()
# proxy_auth_handler.add_password('realm', 'host', 'username', 'password')
opener = urllib.request.build_opener(proxy_handler)
opener.add_handler = [('User-Agent', user_agent)]

count = 0
while 1:
    #url = input("input the website url:")
    try:
        Req = opener.open('https://www.google.com')
    except urllib.error.HTTPError as e:
        print("Error Code: ",e.code)
        count += 1
    except urllib.error.URLError as e:
        print("Reason: ",e.reason)
        count += 1
    else:
        print(Req)
        break
    if count == 5:
        break



with open("result.txt",'wt') as f:
    urlinfo = Req.info()
    website = Req.read()
    print(urlinfo,file=f)
    print(website.decode('utf-8'),file=f)

