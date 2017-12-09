# -*- coding: utf-8 -*-
import sys
from scrapy import cmdline

if __name__ == '__main__':
    try:
        spider_name = sys.argv[1]
        print("Spider name:{}".format(spider_name))
    except Exception:
        spider_name = input("Spider name:")
    cmdline.execute("scrapy crawl {}".format(spider_name).split())
