# -*- coding: utf-8 -*-

# HOW TO START
# 1. 创建project： scrapy startproject <project_name>
# 2. 创建spider script： scrapy genspider <file_name> <start_url>
# 3. 运行spider script: scrapy crawl jobbole

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


# 添加main函数方便pycharm调试

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath((__file__))))
# execute(["scrapy", "crawl", "jobbole"])
# execute(["scrapy", "crawl", "zhihu"])
execute(["scrapy", "crawl", "lagou"])
