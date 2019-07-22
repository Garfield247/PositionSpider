# -*- coding: utf-8 -*-
import re
import json
import scrapy
from urllib import parse as ps
from datetime import datetime
from scrapy_redis.spiders import RedisSpider
from Positionspider.items import PositionspiderItem


class WuyouSpider(RedisSpider):
    name = 'wuyou'
    # allowed_domains = ['wwww.51job.com']
    # start_urls = ['http://wwww.51job.com/']
    search_url = "https://search.51job.com/jobsearch/search_result.php?fromJs=1&keyword={keyword}&keywordtype=2&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9"



    def start_requests(self):
        joblist = json.load(open(r'/project/joblist.json','r',encoding='utf-8'))[0]
        keywords = [[tag,postion] for tag in joblist.keys() for postion in joblist.get(tag,[]) ]
        for tag,position in keywords:
            keyword = ps.quote(position if tag in position else "%s %s"%(tag,position))
            yield scrapy.Request(self.search_url.format(keyword=keyword),callback=self.parse,meta={'tag':tag,'position':position})


    def dis_job_info(self,longtext):
        info_list = re.split(r'[\uFF08|\(]?\d+\s?[\u3001|\.|\uFF09|\)|\uFF0C|\,]+',longtext)
        result_list = []
        for info in info_list:
            new_info = re.sub(r'[\r|\n|\t]','',info).replace('|','-')
            if new_info:
                if ('微信'or'分享'or'邮件') not in new_info:
                    result_list.append(new_info)
        return result_list
    def drop_t(self,text):
        if text:
            return text.replace('\t','').replace('\n','').replace('\r','')
        else:
            return None

    def parse(self,response):
        jobs = response.xpath('.//div[@class="el"]')
        for job in jobs:
            item = PositionspiderItem()
            tag = response.meta['tag']
            position = response.meta['position']
            item['tag'] = tag
            item['position'] = position
            item['job_location'] = jobs.xpath('./span[@class="t3"]/text()').extract_first()
            info_url = job.xpath('//p[starts-with(@class,"t1")]/span/a/@href').extract_first()
            if info_url:
                yield scrapy.Request(info_url,callback = self.parse_item,meta={'tag':tag,'position':position,'item':item})
        next_page = response.xpath('.//div[@class="p_in"]/ul/li[@class="bk"][2]/a/@href').extract_first()
        if next_page:
            yield scrapy.Request(url=next_page,callback=self.parse,meta={'tag':tag,'position':position})

    def parse_item(self, response):
        item = response.meta['item']
        item['job_name'] = self.drop_t(response.xpath('.//div[@class="tHeader tHjob"]/div[@class="in"]/div[@class="cn"]/h1/text()').extract_first())

        item['salary'] = response.xpath('.//div[@class="cn"]/strong/text()').extract_first()
        item['crawl_date'] = str(datetime.now().date())
        item['job_category'] = response.xpath('.//div[@class="com_tag"]/p[@class="at"][3]/span[@class="i_trade"]/../a/text()').extract_first()
        item['company_scale'] = response.xpath('.//p[@class="at"][2]/text()').extract_first()
        item['company_addr'] = self.drop_t(response.xpath('.//div[@class="bmsg inbox"]/p[@class="fp"]/text()[2]').extract_first())
        try:
            item['edu'] = response.xpath('.//div[@class="cn"]/p[2]/text()').extract()[2]
        except:
            item['edu'] = None
        try:
            item['experience'] = response.xpath('.//div[@class="cn"]/p[2]/text()').extract()[1]
        except:
            item['experience'] = None
        item['job_info'] = self.dis_job_info(response.xpath('string(.//div[@class="bmsg job_msg inbox"])').extract_first())
        yield item
