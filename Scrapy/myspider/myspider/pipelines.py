# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem
import logging


class MongoPipeline(object):

    def __init__(self):
        client =pymongo.MongoClient(
            settings['MONGODB_HOST'],
            settings['MONGODB_PORT']
        )
        db = client[settings['MONGODB_DATABASE']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        valid = True
        if item['book_invalid'] >= 11:
            valid = False
            logging.log(logging.DEBUG, "Invalid Book!")
        if valid:
            i = dict(item)
            if self.collection.find_one({'_id': i['_id']}):
                j = {
                    'book_updated': i['book_updated'],
                    'book_star': i['book_star'],
                    'book_subscribe': i['book_subscribe']
                }
                self.collection.update_one({'_id': i['_id']}, {"$set": j}, True)
            else:
                self.collection.insert_one(i)
            logging.log(logging.DEBUG, "Item wrote to MongoDB database {}/{}" .format(settings['MONGODB_DB'], settings['MONGODB_COLLECTION']))
        return item
