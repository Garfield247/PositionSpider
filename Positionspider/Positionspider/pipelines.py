# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import json
import redis
import socket
import pymongo
from datetime import datetime
from twisted.internet.threads import deferToThread
from Positionspider.settings import REDIS_HOST,REDIS_PORT,REDIS_KEY_DATA,MONGO_CONF

class PositionspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonPipeline(object):

    def open_spider(self, spider):
        filedir = './%sdata'%str(datetime.now().date())
        if os.path.exists(filedir)==False:
            os.makedirs(filedir)
        filename = 'Slave-%s-%s-%s.json'%(str(socket.gethostname()).split('-')[-1],spider.name,str(datetime.now().date()))
        filepath = os.path.join(filedir,filename)
        self.fp = open(filepath, 'a', encoding='utf-8')

    def process_item(self, item, spider):
        obj = dict(item)
        obj['source'] = spider.name
        string = json.dumps(obj, ensure_ascii=False)
        self.fp.write(string + '\n')
        return item

    def close_spider(self, spider):
        self.fp.close()

class SaveRedisPipline(object):
    def open_spider(self,spider):
        self.redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        key = REDIS_KEY_DATA
        obj = dict(item)
        obj['source'] = spider.name
        data = json.dumps(obj, ensure_ascii=False)
        self.redis_cli.rpush(key, data)
        return item

class MongodbPiplines(object):
    def open_spider(self,spider):
        host = MONGO_CONF['MONGODB_HOST']
        port = MONGO_CONF['MONGODB_PORT']
        dbName = MONGO_CONF['MONGODB_DBNAME']
        self.client = pymongo.MongoClient(host=host, port=port)
        tdb = self.client[dbName]
        post_name = spider.name+'_data'
        self.post = tdb[post_name]

    def process_item(self, item, spider):
        data = dict(item)
        data['source'] = spider.name
        self.post.insert(data)
        return item

    def close_spider(self, spider):
        self.client.close()
