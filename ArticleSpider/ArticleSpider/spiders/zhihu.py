# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'

import os
import scrapy
import time
import json
import re
import datetime
import pickle

try:
    import urlparse as parse
except:
    from urllib import parse

from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
from zheye import zheye


# 1. spider 入口：start_requests()，完成登录
#    1-a. 旧版本知乎登录，POST用户名，密码和xsrf code (start_requests_deprecated())
#    1-b. 旧版本知乎登录，POST用户名，密码，xsrf code 以及验证码图片/倒立文字验证码(注意这里由于要保证同一个session，利用了callback，比较tricky)
#    1-c. selenium模拟，qr code登录 (start_requests())
# 2. 异步到parse(), 从start_urls开始DFS爬取
# 3. 如果不是question类型url，继续DFS；如果是question类型url，异步到parse_question()解析
# 4. 解析question，yield item，scrapy自动检测是item后路由到pipeline
# 4. 解析question，通过知乎提供的json接口，yield request, 异步到parse_answer()
# 5. 通过json格式解析answer，yield item 并且 如果没有结束，继续异步parse_answer()

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    # question的第一页answer的请求url
    # 知乎是随着滚动自动刷新，如果点开F12-Network，会发现实际上是send了如下request
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"

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
        all_urls = response.css("a::attr(href)").extract()
        # url 加上域名
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        # 注意filter函数的使用,过滤掉非https的url
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            # 通过regex找到question类型的url
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)

                # 注意scrapy是用过yield传递request的
                yield scrapy.Request(request_url, headers=self.headers,
                                     meta={"question_id": question_id},
                                     callback=self.parse_question)
                # break   # debug
            else:
                # pass  # debug
                # 如果不是question页面则直接进行下一步跟踪
                yield scrapy.Request(url, headers=self.headers,
                                     callback=self.parse)

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item
        # 注意：这里也可以继续抓取url进行下一步跟踪，参考self.parse()，此处省略
        question_id = int(response.meta.get("question_id", ""))
        if "QuestionHeader-title" in response.text:
            # 处理新版本
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            # 取html，不取text
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            # 回答数，提取text
            item_loader.add_css("answer_num", ".List-headerText span::text")
            # 评论数，提取text，略微改动
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            # 关注数和浏览数一起提取，略微改动
            item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
            # 主题。 css格式里空格代表后代（子代用">"）小心Popover后面还有个后代div
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

            question_item = item_loader.load_item()
        else:
            # 处理旧版本，略
            raise NotImplementedError
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                             callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        # totals_answer = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]

        #提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            # 由于匿名评论，可能不存在用户id
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            # 没有结束，继续通过next_url拿后面的answer
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

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

            # 如果没有知乎验证码需求，可以直接调用这一步返回，不需要yield
            # return [scrapy.FormRequest(
            #     url=post_url,
            #     formdata=post_data,
            #     headers=self.headers,
            #     callback=self.check_login
            # )]

            # 注意：这里之所以要这样操作，是因为所有的验证码，xsrf code request操作必须要在同一个session下（见utils.zhihu_login_requests.py）
            #      我们无法在scrapy框架下直接使用session，所以我们yield出去，利用scrapy的callback
            #      callback会保证scrapy在同一个session下用相同的cookie
            import time
            t = str(int(time.time() * 1000))
            # 知乎验证码
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
            yield scrapy.Request(captcha_url, headers=self.headers, meta={"post_data": post_data},
                                 callback=self.login_after_captcha)
            # 知乎倒立文字验证
            # captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn".format(t)
            # yield scrapy.Request(captcha_url, headers=self.headers, meta={"post_data": post_data},
            #                      callback=self.login_after_captcha_cn)

    def login_after_captcha_cn(self, response):
        """
        知乎倒立文字验证码识别登录
        :param response:
        :return:
        """
        with open("captcha_cn.jpg", "wb") as f:
            # 注意这里图片是response.body
            f.write(response.body)
            f.close()

        z = zheye()
        positions = z.Recognize('captcha_cn.jpg')

        pos_array = []
        # 有可能有1个或者2个倒立文字
        if len(positions) == 2:
            # zheye识别时可能不是按照x轴先后顺序输出,因此在这里作判断
            if positions[0][1] > positions[1][1]:
                # 先放左边点的x轴，y轴坐标，再放右边点的x轴，y轴坐标
                pos_array.append([positions[1][1], positions[1][0]])
                pos_array.append([positions[0][1], positions[0][0]])
            else:
                pos_array.append([positions[0][1], positions[0][0]])
                pos_array.append([positions[1][1], positions[1][0]])
        else:
            pos_array.append([positions[0][1], positions[0][0]])

        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/phone_num"
        if len(positions) == 2:
            post_data["captcha"] = '{"img_size": [200, 44], "input_points": [[%.2f, %f], [%.2f, %f]]}' % (
                pos_array[0][0] / 2, pos_array[0][1] / 2, pos_array[1][0] / 2, pos_array[1][1] / 2)
        else:
            post_data["captcha"] = '{"img_size": [200, 44], "input_points": [[%.2f, %f]]}' % (
                pos_array[0][0] / 2, pos_array[0][1] / 2)
        post_data['captcha_type'] = "cn"
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def login_after_captcha(self, response):
        """
        知乎验证码识别登录
        :param response:
        :return:
        """
        with open("captcha.jpg", "wb") as f:
            # 注意这里图片是response.body
            f.write(response.body)
            f.close()

        from PIL import Image
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        captcha = input("输入验证码\n>")

        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data["captcha"] = captcha
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
        """
        现在知乎使用的登录方法
        :return:
        """
        # TODO： 不知道为什么这样读了cookie不能使用，而却selenium不能放在else下面
        # cookie_files = os.listdir('./ArticleSpider/cookies/zhihu/')
        # if cookie_files:
        #     # 直接使用cookie
        #     cookie_dict = {}
        #     for cookie_file in cookie_files:
        #         cookie_name = cookie_file.split(".")[0]
        #         with open(os.path.join('./ArticleSpider/cookies/zhihu/', cookie_file), 'rb') as fh:
        #             cookie_value = pickle.load(fh)
        #         cookie_dict[cookie_name] = cookie_value
        # else:
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
        for cookie in cookies:
            # 写入文件
            f = open('./ArticleSpider/cookies/zhihu/' + cookie['name'] + '.zhihu', 'wb')
            pickle.dump(cookie, f)
            f.close()
            cookie_dict[cookie['name']] = cookie['value']
        browser.close()
        # 不指明回调函数，默认为self.parse
        return [scrapy.Request(url=self.start_urls[0], headers=self.headers, dont_filter=True, cookies=cookie_dict)]
