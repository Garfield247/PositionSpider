# -*- coding: utf-8 -*-
import re
import json
import scrapy
from datetime import datetime
from urllib import parse as ps
from scrapy_redis.spiders import RedisSpider
from Positionspider.items import PositionspiderItem


class YingcaiSpider(RedisSpider):
    name = 'yingcai'
    # allowed_domains = ['wwww.chinahr.com']
    # start_urls = ['http://wwww.chinahr.com/']

    def start_requests(self):
        with open(r'/project/joblist.json','r',encoding='utf-8') as fp:
            obj = json.load(fp)
            # print(type(obj[0]))
            dd = obj[0]
            job_l = []
            for k,v in dd.items():
                for kw in v:
                    if k in kw:
                        keyw = ps.quote(kw)
                    else:
                        keyw = ps.quote(k+' '+kw)
                    url = 'http://www.chinahr.com/sou/?orderField=relate&keyword='+ keyw +'&page=1'
                    yield scrapy.Request(url,callback = self.parse,meta={'k':k,'kw':kw},dont_filter=True)

    #解析详情页分页URL
    def parse(self,response):
        # with open('response.html','w',encoding='utf-8') as fp:
        #     fp.write(response.text)
        k = response.meta['k']
        kw = response.meta['kw']
        info_urls = response.xpath('.//div[@class="jobList"]/ul/li[@class="l1"]/span[@class="e1"]/a/@href').extract()
        for info_url in info_urls:

            yield scrapy.Request(info_url,callback = self.parse_item,meta={'k':k,'kw':kw})


        next_page = response.xpath('.//div[@class="pageList"]/a[contains(text(), "下一页")]/@href').extract_first()
        if next_page:
            url = 'http://www.chinahr.com/sou/' + next_page
            yield scrapy.Request(url=url, callback=self.parse, meta={'k':k,'kw':kw})
    #定义处理长文本的函数
    def longtextsplit(self,longtext):
        if type(longtext) == str:
            list_obj =[i.strip() for i in re.split(r'[\uFF08|\(]?\d+\s?[\u3001|\.|\uFF09|\)|\uFF0C|\,]+',re.sub(r'[\r|\n|\t|]','',longtext))]
            return list_obj
        else:
            return ""

    #定义清除转义字符的函数
    def drop_ESC(self,obj):
        if type(obj) == str:
            return re.sub(r'[\r|\n|\t|\s]','',obj)

    def parse_item(self, response):
        # print(response.url)
        # with open('response.html','w',encoding='utf-8') as fp:
        #     fp.write(response.text)
        item = PositionspiderItem()
        k = response.meta['k']
        kw = response.meta['kw']
        item['tag'] = k
        item['position'] = kw
        item['company_name'] = response.xpath('.//div[@class="job-company jrpadding"]/h4/a/text()').extract_first()
        item['salary'] = response.xpath('.//div[@class="job_require"]/span[@class="job_price"]/text()').extract_first()
        item['crawl_date'] = str(datetime.now().date())
        item['job_category'] = self.drop_ESC(response.xpath('.//div[@class="job-company jrpadding"]/table/tbody/tr[2]/td[2]/text()').extract_first())
        item['company_scale'] = response.xpath('.//div[@class="job-company jrpadding"]/table/tbody/tr[3]/td[2]/text()').extract_first()
        item['job_name'] = response.xpath('.//span[@class="job_name"]/text()').extract_first()
        item['job_location'] = response.xpath('.//div[@class="base_info"]/div[@class="job_require"]/span[@class="job_loc"]/text()').extract_first()
        item['company_addr'] = response.xpath('.//div[@class="mapwrap mt15"]/@data-addr').extract_first()
        item['edu'] = response.xpath('.//div[@class="job_profile jpadding"]/div[@class="base_info"]/div[@class="job_require"]/span[4]/text()').extract_first()
        item['experience'] = response.xpath('.//div[@class="job_profile jpadding"]/div[@class="base_info"]/div[@class="job_require"]/span[@class="job_exp"]/text()').extract_first()
        item['job_info'] = self.longtextsplit(response.xpath('string(.//div[@class="job_intro_info"])').extract_first())
        yield item
