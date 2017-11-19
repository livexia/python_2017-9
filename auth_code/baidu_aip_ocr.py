from aip import AipOcr
import requests

""" 你的 APPID AK SK """
APP_ID = '10399977'
API_KEY = 'w6iMCncOWX17rkjT9ALxrYrW'
SECRET_KEY = input('Secret Key：')

aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)

# 读取图片
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

url = 'http://login.sina.com.cn/cgi/pin.php?&s=0&p=yf-1557d096497d1ec13141869101daa184ef64'
resp = requests.get(url)
if resp.status_code == 200:
    with open('pincode.png', 'wb') as f:
        f.write(resp.content)
options = {
    'detect_direction': 'true',
    'language_type': 'ENG',
}
# 调用通用文字识别接口
result = aipOcr.basicGeneral(get_file_content('pincode.png'), options)
print(result)
# 如果图片是url 调用示例如下
# result = aipOcr.basicGeneral(url)
