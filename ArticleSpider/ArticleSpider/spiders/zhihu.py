# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'

import scrapy
import time
import json
import re


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    #question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        'User-Agent': agent
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        pass

    def parse_question(self, response):
        #处理question页面， 从页面中提取出具体的question item
       pass

    def parse_answer(self, response):
        pass

    def start_requests_deprecated(self):
        # 由于知乎更改登录方式，【deprecated】
        # 通过scrapy异步方法获得xsrf
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def login(self, response):
        # 旧的知乎登录方式，配合start_requests_deprecated()使用
        # 详见utils.zhihu_login_requests.py
        response_text = response.text
        # re.DOTALL 设置后匹配全文，不设置的话只能匹配一行
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = (match_obj.group(1))
        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "xxx",
                "password": "xxx"
            }
            return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.headers,
                callback=self.check_login
            )]

    def check_login(self, response):
        # 验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)

    def start_requests(self):
        from selenium import webdriver
        browser = webdriver.Chrome(executable_path="./chromedriver")

        # username_password login not working
        # browser.get("https://www.zhihu.com/signin")
        # browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
        #     "xxx")
        # browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
        #     "xxx")
        # browser.find_element_by_css_selector(
        #     ".Button.SignFlow-submitButton").click()

        # QR code login
        # 打开知乎首页
        browser.get('https://www.zhihu.com/')
        time.sleep(2)
        # 进入登陆页面
        browser.find_element_by_css_selector(".SignContainer-switch span").click()
        time.sleep(1)
        # 点击社交网络账号登陆
        browser.find_element_by_css_selector("span.Login-qrcode button").click()  # 点击qr_code登陆
        time.sleep(10)

        cookies = browser.get_cookies()
        print(cookies)
        cookie_dict = {}
        import pickle
        for cookie in cookies:
            # 写入文件
            f = open('./ArticleSpider/cookies/zhihu/' + cookie['name'] + '.zhihu', 'wb')
            pickle.dump(cookie, f)
            f.close()
            cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        # 不指明回调函数，默认为self.parse
        return [scrapy.Request(url=self.start_urls[0], headers=self.headers, dont_filter=True, cookies=cookie_dict)]