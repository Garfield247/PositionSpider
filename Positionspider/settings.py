# -*- coding: utf-8 -*-

# Scrapy settings for Positionspider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Positionspider'

SPIDER_MODULES = ['Positionspider.spiders']
NEWSPIDER_MODULE = 'Positionspider.spiders'


#item Pipeline同时处理item的最大值为100
CONCURRENT_ITEMS=100
#scrapy downloader并发请求最大值为16
CONCURRENT_REQUESTS=80
#对单个网站进行并发请求的最大值为8
CONCURRENT_REQUESTS_PER_DOMAIN=8
#抓取网站的最大允许的抓取深度值
# DEPTH_LIMIT=0
# Obey robots.txt rules
# ROBOTSTXT_OBEY = False
DOWNLOAD_TIMEOUT=10
DNSCACHE_ENABLED=True
#避免爬虫被禁的策略1，禁用cookie
# Disable cookies (enabled by default)
# COOKIES_ENABLED = False
# CONCURRENT_REQUESTS=4
#CONCURRENT_REQUESTS_PER_IP=2
#CONCURRENT_REQUESTS_PER_DOMAIN=2
#设置下载延时，防止爬虫被禁
DOWNLOAD_DELAY = 1

DOWNLOADER_MIDDLEWARES = {
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware':123,
    'Positionspider.middlewares.ProxyMiddleware' : 100,
}

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en,zh',
}

ITEM_PIPELINES = {
    # 'Positionspider.pipelines.JsonPipeline':300,
    # 'Positionspider.pipelines.SaveRedisPipline':310,
    'Positionspider.pipelines.MongodbPiplines':290,
}

#使用scrapy_redis的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
#确保所有蜘蛛通过redis共享相同的重复过滤器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 是否允许暂停
SCHEDULER_PERSIST = False
# 爬虫使用的队列类
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
# 爬虫等待时间
SCHEDULER_IDLE_BEFORE_CLOSE = 60

# 默认请求序列化器是pickle
SCHEDULER_SERIALIZER = "scrapy_redis.picklecompat"

MONGO_CONF = {
    'MONGODB_HOST' : '192.168.3.99',
    'MONGODB_PORT' : 27017,
    'MONGODB_DBNAME' : 'case01',
}

REDIS_URL = None
REDIS_HOST = '192.168.3.130'
REDIS_PORT = '6379'
# 配置日志
LOG_LEVEL = 'INFO'

REDIS_KEY_PROXY = 'proxies'
REDIS_KEY_HEADER = 'headers'
REDIS_KEY_DATA = 'crawl_data'

#设置停止时间
CLOSESPIDER_TIMEOUT = 86000

FLUME_HOST = '192.168.3.101'
FLUME_PORT = 55555
RETRY_NUM = 1
