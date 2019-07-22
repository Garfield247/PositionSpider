# -*- coding: utf-8 -*-
import re
import json
import scrapy
from datetime import datetime
from urllib import parse as ps
from scrapy_redis.spiders import RedisSpider
from Positionspider.items import PositionspiderItem

class ZhilianSpider(RedisSpider):
    name = 'zhilian'
    # allowed_domains = ['sou.zhilain.com']
    # start_urls = ['http://sou.zhilain.com/']
    search_url = "https://fe-api.zhaopin.com/c/i/sou?pageSize=90&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={keyword}&kt=3"
    next_url = "https://fe-api.zhaopin.com/c/i/sou?start={start}&pageSize=90&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={keyword}&kt=3"

    def start_requests(self):
        joblist = json.load(open(r'/project/joblist.json','r',encoding='utf-8'))[0]
        keywords = [[tag,postion] for tag in joblist.keys() for postion in joblist.get(tag,[]) ]
        for tag,position in keywords:
            keyword = ps.quote(position if tag in position else "%s %s"%(tag,position))
            yield scrapy.Request(self.search_url.format(keyword=keyword),callback=self.parse,meta={'tag':tag,'position':position,'keyword':keyword,'pagenum':1})


    def parse(self, response):
        result = json.loads(response.text)
        tag = response.meta['tag']
        position = response.meta['position']
        keyword = response.meta['keyword']
        pagenum = response.meta['pagenum']
        for data in result['data'].get('results'):
            item = PositionspiderItem()
            item['tag'] = tag
            item['position'] = position
            item['crawl_date'] = str(datetime.now().date())
            item['job_name'] = data.get('jobName')
            item['job_category'] = data.get('jobType',{}).get('display')
            item['company_name'] = data.get('company',{}).get('name')
            item['company_scale'] = data.get('company',{}).get('size').get('name')
            item['experience'] = data.get('workingExp',{}).get('name')
            item['edu'] = data.get('eduLevel',{}).get('name')
            item['salary'] = data.get('salary')
            item['job_location'] = data.get('city',{}).get('display')
            info_url = data.get('positionURL')
            yield scrapy.Request(info_url,callback=self.parse_item,meta={'item':item})
        count = int(result['data'].get('numFound'))
        pagenum +=1
        yield scrapy.Request(url=self.next_url.format(start=(pagenum-1)*90,keyword=keyword),callback=self.parse,meta={'tag':tag,'position':position,'keyword':keyword,'pagenum':pagenum} )
    #定义处理长文本的函数
    def longtextsplit(self,longtext):
        if type(longtext) == str:
            list_obj =[re.sub(r'\s{3,}','',i.strip()) for i in re.split(r'[\uFF08|\(]?\d+\s?[\u3001|\.|\uFF09|\)|\uFF0C|\,]+',re.sub(r'[\r|\n|\t]','',longtext))]
            return list_obj
        else:
            return ""

    def parse_item(self, response):
        # with open('file.html','w',encoding='utf-8') as fp:
        #     fp.write(response.text)
        item = response.meta['item']
        item['company_addr'] = response.xpath("//span[@class='job-address__content-text']/text()").extract_first()
        item['job_info'] = self.longtextsplit(response.xpath('string(//div[@class="describtion"])').extract_first())
        yield item


