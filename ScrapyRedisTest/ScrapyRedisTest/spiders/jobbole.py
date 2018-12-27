# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'

import scrapy
from scrapy.http import Request
from urllib import parse

from scrapy_redis.spiders import RedisSpider


class JobboleSpider(RedisSpider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    # start_urls = ['http://blog.jobbole.com/all-posts/']
    # 这个记录的redis中保存所有request的zset(sorted set)
    redis_key = 'jobbole:start_urls'


    # 以下函数可以照搬以前scrapyde
    def parse(self, response):
        """
        1. 获取文章列表页中的url并交给scrapy下载后并进行解析
        获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        :param response:
        :return:
        """
        # 设置Stats Collection计数404页面的url和个数
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        # 解析列表页所有文章url并交给scrapy下载后并进行解析
        # ::attr(href) 代表去属性名为href的值
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            # 继续parse下一页url和image_url
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            # 根据是否有域名自动做url拼接，parse.urljoin(response.url, post_url)
            # 将url交给scrapy继续parse, 异步协程
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": parse.urljoin(response.url, image_url)},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy下载
        # 通过两个class name 来提取css
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        提取文章的具体字段， 回调函数
        :param response:
        :return:
        """
        pass