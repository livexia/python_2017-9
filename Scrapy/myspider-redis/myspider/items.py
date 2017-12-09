# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GitbookItem(scrapy.Item):
    _id = scrapy.Field()    #由book_contributor/book_name 构成，同时充当mongdb的_id
    book_title = scrapy.Field() #书籍的显示名称
    book_description = scrapy.Field()   #书籍的简单描述
    book_contributor = scrapy.Field()   #书籍的建立者
    book_name = scrapy.Field()  #书籍的名字（仓库名），与显示名称不同
    book_url = scrapy.Field()   #书籍链接
    book_read_url = scrapy.Field()  #书籍阅读链接
    book_download_url = scrapy.Field()  #书籍下载链接，未验证可靠性
    book_star = scrapy.Field()  #书籍的start数量
    book_subscribe = scrapy.Field() #书籍的订阅数量
    book_updated = scrapy.Field()   #书籍的更新日期
    book_invalid = scrapy.Field()   #书籍的有效性