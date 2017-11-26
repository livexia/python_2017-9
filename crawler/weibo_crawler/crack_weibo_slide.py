import os
import time
import queue
import threading
from PIL import Image
from os import listdir
from multiprocessing import Pool


TEMPLATES_FOLDER = 'templates/'


def is_pixel_equal(image1, image2, x, y):
    """
    判断两个像素是否相同
    :param image1: 图片1
    :param image2: 图片2
    :param x: 位置x
    :param y: 位置y
    :return: 像素是否相同
    """
    # 取两个图片的像素点
    pixel1 = image1.load()[x, y]
    pixel2 = image2.load()[x, y]
    threshold = 20
    if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                    pixel1[2] - pixel2[2]) < threshold:
        return True
    else:
        return False


def same_image(image, template):
    """
    识别相似验证码
    :param image: 待识别验证码
    :param template: 模板
    :return:
    """
    # 相似度阈值
    threshold = 0.999
    count = 0
    for x in range(image.width):
        for y in range(image.height):
            # 判断像素是否相同
            if is_pixel_equal(image, template, x, y):
                count += 1
    result = float(count) / (image.width * image.height)
    if result >= threshold:
        return True
    return False


def detect_image(image):
    """
    匹配图片
    :param image: 图片
    :return: 拖动顺序
    """
    p = Pool(4)
    result = queue.Queue()
    numbers = queue.Queue()

    t1 = threading.Thread(target=start, args=(p, result, image))
    t2 = threading.Thread(target=get_result, args=(p, result, numbers))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    p.join()

    return numbers.get()


def detect_one_image(image, template_name):
    # print('正在匹配', template_name)
    template = Image.open(TEMPLATES_FOLDER + template_name)
    if same_image(image, template):
        # 返回顺序
        numbers = ([int(number) for number in list(template_name.split('.')[0])])
        print('匹配成功，拖动顺序：', numbers)
        return numbers
    else:
        return False


def get_exactly_cut(image):
    """
    精确剪切
    查找完全空白像素点
    """
    imin = -1
    imax = -1
    jmin = -1
    jmax = -1
    row = image.size[0]
    col = image.size[1]
    for i in range(row):
        for j in range(col):
            if image.load()[i, j] != (255, 255, 255, 255):
                imax = i
                break
        if imax == -1:
            imin = i

    for j in range(col):
        for i in range(row):
            if image.load()[i, j] != (255, 255, 255, 255):
                jmax = j
                break
        if jmax == -1:
            jmin = j
    return imin + 1, jmin + 1, imax + 1, jmax + 1


def start(p, result, image):
    for template_name in listdir(TEMPLATES_FOLDER):
        if template_name.split('.')[0] != '':
            try:
                result.put(p.apply_async(detect_one_image, args=(image, template_name)))
            except:
                break


def get_result(p, result, numbers):
    while 1:
        number = result.get().get() # 获取子进程返回值
        if number:
            p.terminate()  # 结束所有子进程
            numbers.put(number)
            return number


# start_time = time.time()
# horses = [1, 2, 3, 4]
# import itertools
# races = itertools.permutations(horses)
# while 1:
#     try:
#         name = list(next(races))
#         image = ''.join(map(str, name)) + '.png'
#         detect_name = detect_image(Image.open(image))
#         if name == detect_name:
#             print("识别{}成功".format(image))
#         else:
#             print(name, detect_name)
#     except StopIteration:
#         # 遇到StopIteration就退出循环
#         break
# end_time = time.time()
#
# print(end_time - start_time)