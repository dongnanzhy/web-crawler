# -*- coding: utf-8 -*-
import os
import pickle
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

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

        i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i

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
            browser.find_element_by_css_selector(".form_body .input.input_white").send_keys("username")
            browser.find_element_by_css_selector('.form_body input[type="password"]').send_keys("password")
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
