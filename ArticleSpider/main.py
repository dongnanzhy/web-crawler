# -*- coding: utf-8 -*-

# HOW TO START
# 1. 创建project： scrapy startproject <project_name>
# 2. 创建spider script： scrapy genspider <file_name> <start_url>
#    2-a. "scrapy genspider -t crawl <file_name> <start_url>" (-t 指明模板模式，默认为basic)
# 3. 运行spider script: scrapy crawl jobbole
#    3-a. 暂停与重启：scrapy crawl lagou -s JOBDIR=job_info/001
#                  (注意不同spider不用次运行必须用不同的dir，通过ctrl+C终止[kill -f 不是kill -9] )

# SCRAPY SHELL 运用
# 可以在shell里调试html，不用每次运行都访问一次url
# scrapy shell <url>

# 项目流程【爬取博客系统】spiders/jobbole.py
# 1. 使用xPath extract html 或者 使用css extract html
# 2. 通过异步call back 函数爬取网站
# 3. 设计item
# 4. 修改settings的pipeline，加入自定义image pipeline保存图片及路径
# 5. 爬取数据导出JSON文件
# 6. 爬取数据导出MySQL，同步 + 异步两种方式
# 7. 利用ItemLoader整理代码

# 项目流程【爬取知乎】 spiders/zhihu.py
# 1. 知乎登录，以方便从首页DFS
#     1-a. Requests 模拟知乎登录(tools.zhihu_login_requests.py)
#     1-b. Scrapy 模拟知乎登录(w/o 验证码/倒立文字)。由于知乎更改登录设置，deprecated
#     1-c. 通过selenium和qr_code 模拟知乎登录，并保存cookie
# 2. 设计知乎sql表
# 3. Item Loader提取知乎question，利用知乎API提取知乎answer
# 4. 异步保存至SQL

# 项目流程【爬取拉勾网全栈】 spiders/lagou.py
# 1. 设计SQL表
# 2. 生成spider，"scrapy genspider -t crawl <file_name> <start_url>" (-t 指明模板模式，默认为basic)
# 3. 修改settings sys.path.append(source path)
# 4. 通过selenium模拟登录，并保存cookie
# 3. Item Loader提取拉勾网信息
# 4. 异步保存至SQL


# SCRAPY进阶 【反爬虫】  middlewares.py
# 1. Scrapy架构 (core: engine, spider, scheduler, downloader, item, 2 middlewares (spider middleware and downloader middleware))
# 2. http.Request 和 Response
# 3. downloadermiddleware 随机更换user agent
# 4. downloadermiddleware 更换ip代理(proxy) (付费软件crawlera, 或者TOR)
# 5. 验证码识别 (在线打码：云打码)
# 6. 设置custom_settings

# SCRAPY进阶 【selenium 等】  tools/selenium_spider.py
# 1. selenium模拟知乎登录，模拟微博鼠标下拉
# 2. chromedriver不加载图片, phantomJS
# 3. scrapy downloader middleware 集成selenium
# 4. 动态网页(url带有"?")： scrapy-splash, selenium grid, splinter (略)
# 5. scrapy 暂停与重启，url去重(hash.sha1), telnet(scrapy会默认开启telnet，监听端口，可以通过命令行连接)
# 6. spider middleware 可以参考scrapy定义的几个(depth, httperror...)
# 7. spider Stats Collection(数据收集)
# 8. scrapy Signals(信号)。非常重要，关联了各个core
# 9. scrapy Extensions(扩展)
#    spider/downloader middleware实际上都是有extension manager管理的，定义函数与信号量进行了绑定
#    主要入口 from_crawler(), 在里面绑定信号量（见官网例子）


# 添加main函数方便pycharm调试

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath((__file__))))
# execute(["scrapy", "crawl", "jobbole"])
# execute(["scrapy", "crawl", "zhihu"])
execute(["scrapy", "crawl", "lagou"])
