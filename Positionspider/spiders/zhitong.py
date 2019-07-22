# -*- coding: utf-8 -*-
import re
import json
import scrapy
from datetime import datetime
from urllib import parse as ps
from scrapy_redis.spiders import RedisSpider
from Positionspider.items import PositionspiderItem

class ZhitongSpider(scrapy.Spider):
    name = 'zhitong'
    # allowed_domains = ['www.job5156.com']
    # start_urls = ['http://www.job5156.com/']

    search_url = "http://www.job5156.com/s/result/ajax.json?keyword={keyword}&keywordType=0&sortBy=0&pageNo={pagenum}"


    def start_requests(self):
        joblist = json.load(open(r'/project/joblist.json','r',encoding='utf-8'))[0]
        keywords = [[tag,postion] for tag in joblist.keys() for postion in joblist.get(tag,[]) ]
        for tag,position in keywords:
            keyword = ps.quote(position if tag in position else "%s %s"%(tag,position))
            yield scrapy.Request(self.search_url.format(keyword=keyword,pagenum=1),callback=self.parse,meta={'tag':tag,'position':position,'keyword':keyword,'pagenum':1})

    #定义处理长文本的函数
    def longtextsplit(self,longtext):
        if type(longtext) == str:
            list_obj =[re.sub(r'\s{3,}','',i.strip()) for i in re.split(r'[\uFF08|\(]?\d+\s?[\u3001|\.|\uFF09|\)|\uFF0C|\,]+',re.sub(r'[\r|\n|\t]','',longtext))]
            return list_obj
        else:
            return ""

    def parse(self, response):
        result = json.loads(response.text)
        # print(result)
        tag = response.meta['tag']
        position = response.meta['position']
        keyword = response.meta['keyword']
        pagenum = response.meta['pagenum']
        for data in result.get('page',{}).get('items',[]):
            item = PositionspiderItem()
            item['tag'] = tag
            item['position'] = position
            item['crawl_date'] = str(datetime.now().date())
            item['job_name'] = data['posName']
            item['job_category'] = data['industryStr']
            item['company_name'] = data['comName']
            item['company_scale'] = data['comInfo'].get('employeeNumStr')
            item['experience'] = data['reqWorkYearStr']
            item['edu'] = data['educationDegreeStr']
            item['salary'] = data['salaryStr']
            item['job_location'] = data['workLocationsStr']
            # info_url = data['positionURL']
            item['company_addr'] = data['comInfo'].get('locationStr')
            item['job_info'] = self.longtextsplit(data['posDesc'])
            yield item
        if result['page'].get('hasNext'):
            pagenum +=1
            yield scrapy.Request(url=self.search_url.format(keyword=keyword,pagenum=pagenum),callback=self.parse,meta={'tag':tag,'position':position,'keyword':keyword,'pagenum':pagenum} )






