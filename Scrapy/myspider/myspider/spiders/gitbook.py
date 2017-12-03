# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from myspider.items import GitbookItem
import itertools

class GitbookSpider(scrapy.Spider):
    name = "gitbook"
    allowed_domains = ["gitbook.com"]
    start_urls = ['https://www.gitbook.com/explore?lang=all']
    base_url = 'https://www.gitbook.com/'
    download_base_url = 'https://www.gitbook.com/download/'
    read_base_url = 'https://www.gitbook.com/read/'

    def parse(self, response):
        #获得页数
        last_page = int(response.xpath('//ul[@class="pagination-pages"]/li[last()]//text()').extract()[0])
        raw_url = self.start_urls[0] + '&page='
        all_page = itertools.chain(range(0, last_page))
        while 1:
            try:
                page = str(next(all_page))
                url = raw_url + page
                # print("爬取第{}页".format(page))
                yield Request(url, callback=self.parse_page)
            except StopIteration:
                print("所有页面爬取完成")
                break

    def parse_page(self, response):
        sel = Selector(response)
        books = []
        all_books = sel.xpath('//div[@class="Book"]')
        for item in all_books:
            # print(item.extract())
            book = GitbookItem()
            book['book_title'] = item.xpath('.//div[@class="book-infos"]/h2[@class="title"]//text()').extract()[0]
            book['book_invalid'] = 0
            if '❤️' in book['book_title']:
                book['book_invalid'] += 10
            if 'dating' in book['book_title']:
                book['book_invalid'] += 10
            if 'Gay' in book['book_title']:
                book['book_invalid'] += 10

            book['book_description'] = item.xpath('.//div[@class="book-infos"]/p[@class="description"]//text()').extract()
            book['book_url'] = item.xpath('.//div[@class="book-infos"]/h2[@class="title"]/a/@href').extract()[0]
            book['book_updated'] = item.xpath('.//div[@class="book-infos"]/p[@class="updated"]/span//text()').extract()[0]
            book['book_contributor'] = book['book_url'].split('/')[4]
            book['book_name'] = book['book_url'].split('/')[5]
            book['_id'] = book['book_contributor'] + '/' + book['book_name']
            book['book_read_url'] = self.read_base_url + 'book'+ book['book_contributor'] + '/' + book['book_name']
            book['book_download_url'] = [
                self.download_base_url + 'pdf' + '/book/'+ book['book_contributor'] + '/' + book['book_name'],
                self.download_base_url + 'mobi' + '/book/'+ book['book_contributor'] + '/' + book['book_name'],
                self.download_base_url + 'epub' + '/book/'+ book['book_contributor'] + '/' + book['book_name']
            ]
            yield Request(book['book_url'] + '/details', meta={'key': book}, callback=self.parse_item)

    def parse_item(self, response):
        book = response.meta['key']
        sel = Selector(response).xpath('.//div[@class="btn-toolbar pull-right head-toolbar"]//a')
        book['book_star'] = int(sel.xpath('./text()').extract()[1])
        book['book_subscribe'] = int(sel.xpath('./text()').extract()[3])

        if book['book_star'] <=1:
            book['book_invalid'] += 1
        if book['book_subscribe'] <= 1:
            book['book_invalid'] += 1

        yield book