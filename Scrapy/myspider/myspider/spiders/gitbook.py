# -*- coding: utf-8 -*-
import scrapy


class GitbookSpider(scrapy.Spider):
    name = "gitbook"
    allowed_domains = ["gitbook.com"]
    start_urls = ['https://www.gitbook.com/explore/']

    def parse(self, response):
        pass
