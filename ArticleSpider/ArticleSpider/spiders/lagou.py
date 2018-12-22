# -*- coding: utf-8 -*-
import os
import pickle
from datetime import datetime
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import LagouJobItemLoader, LagouJobItem
from utils.common import get_md5


# CrawlSpider源码分析
# 不能重写parse()函数，最重要的函数：_parse_response(),
# 可自定义的函数：parse_start_url， process_results


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def parse_start_url(self, response):
        return []

    def process_results(self, response, results):
        return results

    def parse_job(self, response):
        # 解析拉勾网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        # 以下四个item通过span拿到，用xpath比较好写
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        # 这里把全文html提取
        item_loader.add_css("job_desc", ".job_bt div")
        # 这里有些地址放在<a>下面，不能直接取text。先全拿到，后面再处理
        item_loader.add_css("job_addr", ".work_addr")
        # 注意：job_company是一个id，所以用"#"不用"."
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()

        return job_item

    def start_requests(self):
        """
        使用selenium模拟登陆后拿到cookie交给scrapy的request使用
        通过selenium模拟登录
        :return:
        """
        # 从文件读取cookie
        cookies = []
        if os.path.exists('./ArticleSpider/cookies/lagou/lagou.cookie'):
            cookies = pickle.load(open('./ArticleSpider/cookies/lagou/lagou.cookie', 'rb'))
        if not cookies:
            from selenium import webdriver
            import time
            browser = webdriver.Chrome(executable_path="./chromedriver")
            browser.get("https://passport.lagou.com/login/login.html")
            browser.find_element_by_css_selector(".form_body .input.input_white").send_keys("0012064094331")
            browser.find_element_by_css_selector('.form_body input[type="password"]').send_keys("Zhy198901")
            browser.find_element_by_css_selector('div[data-view="passwordLogin"] input.btn_lg').click()
            time.sleep(10)

            cookies = browser.get_cookies()
            print(cookies)
            pickle.dump(cookies, open('./ArticleSpider/cookies/lagou/lagou.cookie', 'wb'))

            browser.close()

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        # 以下是重写了原函数的代码
        for url in self.start_urls:
            yield scrapy.Request(url=url, dont_filter=True, cookies=cookie_dict)
