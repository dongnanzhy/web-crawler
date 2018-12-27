# -*- coding: utf-8 -*-

# 添加main函数方便pycharm调试

from scrapy.cmdline import execute

import sys
import os

# Implementation: 修改了settings和jobbole，启动后spider会不断访问redis
#                 执行： "redis-cli lpush jobbole:start_urls http://blog.jobbole.com/all-posts/"，
#                 可以发现spider立刻pop出来进行parse

# 源码分析：
# 1. connection.py, defaults.py
# 2. dupefilter.py(scrapy和scrapy-redis原理相同，都会在里面记录requests_seen)
# 3. pipelines.py，定义了RedisPipeline
# 4. queue.py, 定义了三种queue
# 5. scheduler.py
# 6. spiders.py 继承了一个RedisMixin； scrapy-redis还是先了crawl_spider做全栈爬取

# bloomfilter集成
# 1. bloomfilter是url去重技术，是对hashset去重的进步一升级
# 2. 自定义bloomfilter放在/utils里
# 3. 更改scrapy_redis的dupefilter.py去重函数。加入bloomfilter


sys.path.append(os.path.dirname(os.path.abspath((__file__))))
execute(["scrapy", "crawl", "jobbole"])
