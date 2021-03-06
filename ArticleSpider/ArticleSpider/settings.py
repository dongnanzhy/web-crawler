# -*- coding: utf-8 -*-
import os
import sys
# 注意：通过这种方法可以把ArticleSpider/ArticleSpider 作为source path, 供所有scrapy使用
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Scrapy settings for ArticleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ArticleSpider'

SPIDER_MODULES = ['ArticleSpider.spiders']
NEWSPIDER_MODULE = 'ArticleSpider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"
RANDOM_UA_TYPE = "random"

# Obey robots.txt rules
# 遵循robots协议，要设置为false
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# 延迟下载，以防止被反爬虫
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# 注意：对于不需要登录的网站，最好设置为False，以防止server追踪
#      因为在zhihu和lagou设置了custom_settings,所以这里设为False
# 首次加入cookie后，后面的request都会自动加上cookie
COOKIES_ENABLED = False
# COOKIES_DEBUG = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ArticleSpider.middlewares.ArticlespiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'ArticleSpider.middlewares.ArticlespiderDownloaderMiddleware': 543,
    # 自己定义的随机更换agent的middleware,自定义的middleware要大于系统自带的，才能保证后执行覆盖
    'ArticleSpider.middlewares.RandomUserAgentMiddleware': 543,
    # 在所有request中加上settings里设置的USER_AGENT
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 2,
    # 设置通过selenium下载页面
    # 'ArticleSpider.middlewares.JSPageMiddleware': 3,
}

# Enable or disable extensions  自定义extension
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# 这个就是item在pipeline中的流动（处理）顺序，数字越小代表越先进入pipeline
ITEM_PIPELINES = {
   # 默认pipeline
   # 'ArticleSpider.pipelines.ArticlespiderPipeline': 300,
   # 默认image pipeline
   # 'scrapy.pipelines.images.ImagesPipeline': 1,
   # 自定义JSON pipeline
   # 'ArticleSpider.pipelines.JsonExporterPipeline': 2,
   # 自定义image pipeline
   # 'ArticleSpider.pipelines.ArticleImagePipeline': 1,
   # 自定义mysql pipeline
   # 'ArticleSpider.pipelines.MysqlPipeline': 2,
   # 自定义 异步 mysql pipeline
   # 'ArticleSpider.pipelines.MysqlTwistedPipeline': 2,
   # 自定义 elasticsearch pipeline
   'ArticleSpider.pipelines.ElasticsearchPipeline': 2,
}
# 定义image的url路径item字段 和 下载存储地址
IMAGES_URLS_FIELD = "front_image_url"
project_dir = os.path.abspath(os.path.dirname(__file__))
IMAGES_STORE = os.path.join(project_dir, "images")

# 设置下载图片的最小dimension
IMAGES_MIN_HEIGHT = 100
IMAGES_MIN_WIDTH = 100


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# MYSQL 配置
MYSQL_HOST = '192.168.1.3'
MYSQL_DBNAME = 'article_spider'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '1989zz9891'

SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"
