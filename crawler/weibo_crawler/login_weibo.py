# -*- coding: UTF-8 -*-
import os
import rsa
import binascii
import base64
import re
import time
import json
import random
import requests
import urllib.parse
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crack_weibo_slide import *
from general import *


class LoginWeibo():

    def __init__(self, username, password):
        self.session = requests.Session()
        self.browser = webdriver.PhantomJS()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password
        self.numbers = []

    def __del__(self):
        try:
            self.browser.close()
        except:
            self.browser.quit()

    def process_verify_code(self, pcid):
        url = 'http://login.sina.com.cn/cgi/pin.php?r={randint}&s=0&p={pcid}'.format(
            randint=int(random.random() * 1e8), pcid=pcid)
        filename = '{}.png'.format(pcid)
        if os.path.isfile(filename):
            os.remove(filename)
        resp = self.session.get(url)
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

    def encode_password(self, servertime, nonce, pubkey):
        rsaPubkey = int(pubkey, 16)
        RSAKey = rsa.PublicKey(rsaPubkey, 65537)  # 创建公钥
        codeStr = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)  # 根据js拼接方式构造明文
        pwd = rsa.encrypt(codeStr.encode('utf-8'), RSAKey)  # 使用rsa进行加密
        return binascii.b2a_hex(pwd)  # 将加密信息转换为16进制。

    def encode_username(self):
        su = base64.b64encode(self.username.encode(encoding="utf-8"))
        return su

    def normal_login(self):
        print("电脑端登陆入口")
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

        su = self.encode_username()

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
        prelogin = self.session.get(url_prelogin, params=preData).content.decode('gbk')
        prelogin_info = json.loads(re.findall(r'\((\{.*?\})\)', prelogin)[0])
        sp = self.encode_password(prelogin_info['servertime'], prelogin_info['nonce'], prelogin_info['pubkey'])

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
            postData.update(self.process_verify_code(prelogin_info['pcid']))
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

        resp_login = self.session.post(url_login, data=postData)
        final_url = re.findall(r'(http[^s].*?)\"\)', resp_login.text)[0].replace("%2F", "/").replace("%3F", "?").replace("%3D", "=").replace("%26", "&").replace("%3A",":")
        resp_final = self.session.get(final_url)

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
                url = self.session.get(loginurl).text
                url = re.findall(r"(https.*?)\"\)", url)[0]
                if "登陆" not in self.session.get(url).text:
                    print("登陆阶段完成")
                else:
                    print("登陆阶段失败")
            else:
                print("登录失败！")

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://m.weibo.cn/'
        self.browser.get(url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def get_position(self):
        """
        初步剪裁验证码
        :return: 验证码位置元组
        """
        try:
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-holder-body')))
            time.sleep(2)
            location = img.location
            size = img.size
            top, bottom, left, right = location['y'] + 100, location['y'] + size['height'] + 60, location['x'], \
                                       location['x'] + \
                                       size['width']
            return (left, top, right, bottom)
        except TimeoutException:
            self.open()
            return False

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        first_cut = self.get_position()
        if not first_cut:
            print('未出现验证码')
            return False
        else:
            print("需要滑动验证")
            print('验证码位置', first_cut)
            screenshot = self.get_screenshot()
            captcha = screenshot.crop(first_cut)
            new_cut = get_exactly_cut(captcha)
            captcha = captcha.crop(new_cut)
            captcha.save(name)
            return captcha

    def move(self, numbers):
        """
        根据顺序拖动
        :param numbers:
        :return:
        """
        # 获得四个按点
        circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ')
        dx = dy = 0
        for index in range(4):
            circle = circles[numbers[index] - 1]
            # 如果是第一次循环
            if index == 0:
                # 点击第一个按点
                ActionChains(self.browser) \
                    .move_to_element_with_offset(circle, circle.size['width'] / 2, circle.size['height'] / 2) \
                    .click_and_hold().perform()
            else:
                # 小幅移动次数
                times = 30
                # 拖动
                for i in range(times):
                    ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                    time.sleep(1 / times)
            # 如果是最后一次循环
            if index == 3:
                # 松开鼠标
                ActionChains(self.browser).release().perform()
            else:
                # 计算下一次偏移
                dx = circles[numbers[index + 1] - 1].location['x'] - circle.location['x']
                dy = circles[numbers[index + 1] - 1].location['y'] - circle.location['y']

    def save_cookie(self):
        file_name = "cookies.json"
        json_to_file(file_name, self.browser.get_cookies())
        d = read_json_file(file_name)
        cookie = {}
        for item in d:
            if item.__contains__('name') and item.__contains__('value') and item.__contains__('expiry'):
                expiry_date = int(item['expiry'])
                if expiry_date > (int)(time.time()):
                    cookie[item['name']] = item['value']
                else:
                    print("过期cookie")
                    return False
        if not cookie:
            print("无效cookie")
            return False
        # print(cookie)
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookie)
        return True

    def mobile_login(self):
        """
        破解入口
        :return:
        """
        self.open()
        # 获取验证码图片
        print("手机端登陆入口")
        image = self.get_image('captcha.png')
        if image:
            numbers = detect_image(image)
            self.move(numbers)
        time.sleep(2)
        if self.save_cookie():
            print("传递cookie成功")
            time.sleep(5)
            print('手机端登陆阶段完成')
        else:
            i = input("传递cookie失败，尝试再次获取[y/n]:")
            if i == 'y':
                self.mobile_login()
            else:
                print("获取cookie失败")
                exit(1)
