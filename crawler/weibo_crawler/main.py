import sys
from general import read_json_file
from login_weibo import LoginWeibo
from weibo_spider import WeiboSpider

#入口
def main():
    if input("是否从根目录breakpoint.json中读取断点[y/n]：") == 'y':
        stopinfo = read_json_file('breakpoint.json')
        print('断点为：uid为{}的{}页。'.format(stopinfo['uid'], stopinfo['page']))
    else:
        stopinfo = {'page': '-1', 'uid': '-1', '_id': '-1', 'total_page': '-1'}

    print('请登录微博！')
    try:
        username = sys.argv[1]
        password = sys.argv[2]
    except IndexError:
        username = input('输入账号：')
        password = input('输入密码：')

    crawler = WeiboSpider(stopinfo)
    login = LoginWeibo(username, password)
    count = 0
    login_method = input("登陆入口，默认手机端登陆[p(PC)/m(Mobile)]：")

    while count < 3:
        try:
            if login_method == 'p':
                login.normal_login()    #PC端登陆，手动输入图像验证码
            else:
                login.mobile_login()    #手机端登陆，自动识别滑动验证码
            break
        except Exception:
            count += 1
    crawler.session = login.session

    url = [
        r'https://weibo.cn/2761139954',
        r'https://weibo.cn/1765335300'
    ]
    for u in url:
        crawler.get_html(u, True)
    stopinfo = crawler.stopinfo
    print(stopinfo)


main()