# -*- coding: utf-8 -*-
import redis
from random import choice

from zhilianspider.settings import REDIS_HOST, REDIS_PORT, REDIS_KEY_PROXY,REDIS_KEY_HEADER


def random_proxy():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    except:
        print ('连接redis失败')
        result = r.zrangebyscore(REDIS_KEY_PROXY,100,100)
        if len(result):
            # print(choice(result))
            return choice(result) 
        else:
            result = r.zrevrange(REDIS_KEY_PROXY, 0, 100)
            if len(result):
                # print(choice(result))
                return choice(result) 
            else:
                pass

def random_ua():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    except:
        print ('连接redis失败')
        result = r.zrangebyscore(REDIS_KEY_HEADER,100,100)
        if len(result):
            # print(choice(result))
            return choice(result) 
        else:
            result = r.zrevrange(REDIS_KEY_HEADER, 0, 100)
            if len(result):
                # print(choice(result))
                return choice(result) 
            else:
                pass


