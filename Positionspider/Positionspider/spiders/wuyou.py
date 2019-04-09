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
                    url = 'https://search.51job.com/jobsearch/search_result.php?fromJs=1&keyword='+ keyw +'&keywordtype=2&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9'
                    yield scrapy.Request(url,callback=self.parse,meta={'k':k,'kw':kw},dont_filter=True)


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
    def com_scale(self,text):
        try:
            scale = text.split('|')[1].strip()
            return scale
        except:
            return None

    def parse(self,response):
        # with open('response.html','w',encoding='utf-8') as fp:
        #     fp.write(response.text)
        jobs = response.xpath('.//div[@class="el"]')
        for job in jobs:
            item = PositionspiderItem()
            k = response.meta['k']
            kw = response.meta['kw']
            item['tag'] = k
            item['position'] = kw
            item['job_location'] = jobs.xpath('./span[@class="t3"]/text()').extract_first()
            print(item['job_location'])
            info_url = job.xpath('//p[starts-with(@class,"t1")]/span/a/@href').extract_first()
            print(info_url)
            yield scrapy.Request(info_url,callback = self.parse_item,meta={'k':k,'kw':kw,'item':item})
        next_page = response.xpath('.//div[@class="p_in"]/ul/li[@class="bk"][2]/a/@href').extract_first()
        if next_page:
            yield scrapy.Request(url=next_page,callback=self.parse,meta={'k':k,'kw':kw})

    def parse_item(self, response):
        item = response.meta['item']
        item['job_name'] = self.drop_t(response.xpath('.//div[@class="tHeader tHjob"]/div[@class="in"]/div[@class="cn"]/h1/text()').extract_first())

        item['salary'] = response.xpath('.//div[@class="cn"]/strong/text()').extract_first()
        item['crawl_date'] = str(datetime.now().date())
        item['job_category'] = response.xpath('.//div[@class="bmsg job_msg inbox"]/div[@class="mt10"]/p[@class="fp"]/span[@class="el"]/text()').extract_first()
        item['company_scale'] = self.com_scale(response.xpath('.//div[@class="cn"]/p[@class="msg ltype"]/text()').extract_first())
        item['company_addr'] = self.drop_t(response.xpath('.//div[@class="bmsg inbox"]/p[@class="fp"]/text()[2]').extract_first())
        item['edu'] = response.xpath('.//div[@class="jtag inbox"]/div[@class="t1"]/span[@class="sp4"]/em[@class="i2"]/../text()').extract_first()
        item['experience'] = response.xpath('.//div[@class="jtag inbox"]/div[@class="t1"]/span[@class="sp4"]/em[@class="i1"]/../text()').extract_first()
        item['job_info'] = self.dis_job_info(response.xpath('string(.//div[@class="bmsg job_msg inbox"])').extract_first())
        yield item
