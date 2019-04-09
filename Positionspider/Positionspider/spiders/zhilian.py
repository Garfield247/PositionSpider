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

    def start_requests(self):
        with open('/project/joblist.json','r',encoding='utf-8') as fp:
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
                    url = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw='+keyw+'&kt=3&lastUrlQuery=%7B%22pageSize%22:%2260%22,%22jl%22:%22489%22,%22kw%22:%22'+keyw+'%22,%22kt%22:%223%22%7D'
                    yield scrapy.Request(url,callback = self.parse,meta={'k':k,'kw':kw,'keyw':keyw,'pn':1},dont_filter=True)


    def parse(self, response):
        result = json.loads(response.text)
        k = response.meta['k']
        kw = response.meta['kw']
        keyw = response.meta['keyw']
        pn = response.meta['pn']
        for data in result['data'].get('results'):
            item = PositionspiderItem()
            item['tag'] = k
            item['position'] = kw
            item['crawl_date'] = str(datetime.now().date())
            item['job_name'] = data['jobName']
            item['job_category'] = data['jobType'].get('display')
            item['company_name'] = data['company'].get('name')
            item['company_scale'] = data['company'].get('size').get('name')
            item['experience'] = data['workingExp'].get('name')
            item['edu'] = data['eduLevel'].get('name')
            item['salary'] = data['salary']
            item['job_location'] = data['city'].get('display')
            info_url = data['positionURL']
            yield scrapy.Request(info_url,callback=self.parse_item,meta={'k':k,'kw':kw,'item':item})
        count = int(result['data'].get('numFound'))
        pn +=1
        keyword = ps.unquote(keyw)
        if pn*60 < count:
            next_page = 'https://fe-api.zhaopin.com/c/i/sou?start={start}&pageSize=60&cityId=489&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={k_w}&kt=3&lastUrlQuery='.format(start=(pn-1)*60,k_w=keyw)+ps.quote({"p":pn,"pageSize":"60","jl":"489","kw":keyword,"kt":"3"})
            print('!!!!!',next_page)
            yield scrapy.Request(url=next_page,callback=self.parse,meta={'k':k,'kw':kw,'keyw':keyw,'item':item},dont_filter=True )
    #定义处理长文本的函数
    def longtextsplit(self,longtext):
        if type(longtext) == str:
            list_obj =[re.sub(r'\s{3,}','',i.strip()) for i in re.split(r'[\uFF08|\(]?\d+\s?[\u3001|\.|\uFF09|\)|\uFF0C|\,]+',re.sub(r'[\r|\n|\t]','',longtext))]
            return list_obj
        else:
            return ""

    #定义清除转义字符的函数
    def drop_ESC(self,obj):
        if type(obj) == str:
            return re.sub(r'[\r|\n|\t|\s]','',obj)

    def parse_item(self, response):
        # with open('file.html','w',encoding='utf-8') as fp:
        #     fp.write(response.text)
        item = response.meta['item']
        item['company_addr'] = response.xpath('//p[@class="add-txt"]/text()').extract_first()
        item['job_info'] = self.longtextsplit(response.xpath('string(.//div[@class="pos-ul"])').extract_first())
        yield item


