# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PositionspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #数据来源，网站地址（需要去除前缀和后缀）
    source = scrapy.Field()
    #标签，采集固定值，joblist第一层
    tag = scrapy.Field()
    #岗位，采集固定值，joblist第二层，与tag关联
    position = scrapy.Field()
    #职位分类，本项目无太大实用意义
    job_category = scrapy.Field()
    #职位名称
    job_name = scrapy.Field()
    #工作地点
    job_location = scrapy.Field()
    #采集日期，固定值，采集的当前日期，格式YYYY-MM-DD
    crawl_date = scrapy.Field()
    #学历要求
    edu = scrapy.Field()
    #薪资
    salary = scrapy.Field()
    #工作经验
    experience = scrapy.Field()
    #职位信息，包括工作职责以及任职要求
    job_info = scrapy.Field()
    #公司名称
    company_name = scrapy.Field()
    #公司地址
    company_addr = scrapy.Field()
    #公司规模
    company_scale = scrapy.Field()

