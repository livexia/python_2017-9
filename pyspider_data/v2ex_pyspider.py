#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-12-31 10:33:42
# Project: v2ex_spider

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.v2ex.com/planes', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/go"]').items():
            self.crawl(each.attr.href, callback=self.node_page)

    @config(age=10 * 24 * 60 * 60)
    def node_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/t"]').items():
            url = each.attr.href
            if url.find('#reply') > 0:
                url = url[0:url.find('#')]
            self.crawl(url, callback=self.post_page)
        for each in response.doc('a.page_normal').items():
            self.crawl(each.attr.href, callback=self.node_page, validate_cert=False)
       
    @config(age=10 * 24 * 60 * 60)
    def post_page(self, response):
        post = {}
        title = response.doc('h1').text()
        topic_content = response.doc('.topic_content').text()
        post['node'] = response.doc('.header > a').text().split('V2EX ')[1]
        post['title'] = title
        post['author'] = response.doc('.header > .gray > a').text()
        post['content'] = topic_content
        post['reply'] = []
        
        try:
            post['reply_count'], post['update_time'] = response.doc('.cell > .gray').text().split('回复 | 直到 ')
        except Exception:
            return post
        for each in response.doc('.cell td').items():
            #reply = {}
            num = each('* .fr > span').text()
            if num:
                username = each('strong').text()
                reply_content = each('.reply_content').text()
                #reply[num]={username:reply_content}
                post['reply'].append({username:reply_content})
        if response.doc('.page_normal').text():
            for each in response.doc('.page_normal').items():
                self.crawl(each.attr.href, callback=self.turn_page, validate_cert=False, save = post)
        else:
            return post

    
    @config(age=10 * 24 * 60 * 60)
    def turn_page(self, response):
        post = response.save
        reply = post['reply']
        post['reply'] = []
        for each in response.doc('.cell td').items():
            num = each('* .fr > span').text()
            if num:
                username = each('strong').text()
                reply_content = each('.reply_content').text()
                #reply[num]={username:reply_content}
                post['reply'].append({username:reply_content}) 
        post['reply'] += reply
        return post
                
                
                