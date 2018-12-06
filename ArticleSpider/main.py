# -*- coding: utf-8 -*-

# HOW TO START
# 1. 创建project： scrapy startproject <project_name>
# 2. 创建spider script： scrapy genspider <file_name> <start_url>
# 3. 运行spider script: scrapy crawl jobbole

# SCRAPY SHELL 运用
# 可以在shell里调试html，不用每次运行都访问一次url
# scrapy shell <url>

# 项目流程
# 1. 使用xPath extract html 或者 使用css extract html
# 2. 通过异步call back 函数爬取网站
# 3. 设计item
# 4. 修改settings的pipeline，加入自定义image pipeline保存图片及路径
# 5. 爬取数据导出JSON文件
# 6. 爬取数据导出MySQL，同步 + 异步两种方式
# 7. 利用ItemLoader整理代码

# 添加main函数方便pycharm调试

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath((__file__))))
execute(["scrapy", "crawl", "jobbole"])