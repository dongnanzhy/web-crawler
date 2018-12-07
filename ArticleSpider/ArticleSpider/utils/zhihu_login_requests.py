# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'
# 这个script因为知乎更改了登录方式，所以没法使用

import requests
try:
    import cookielib   # python 2
except:
    import http.cookiejar as cookielib   # python 3

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36"
header = {
    "HOST":"www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    'User-Agent': agent
}


def is_login():
    #通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/inbox"
    # 要设置重定向参数，以防止重定向到登录页面
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    # 状态码应该是 == 302
    if response.status_code != 200:
        return False
    else:
        return True


def get_xsrf():
    #获取xsrf code
    response = session.get("https://www.zhihu.com", headers=header)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        return (match_obj.group(1))
    else:
        return ""


def get_index():
    # 测试利用cookie拿到首页
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")


def zhihu_login(account, password):
    #知乎登录
    post_url, post_data = None, None
    if re.match("^1\d{10}",account):
        print ("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password
        }
    else:
        if "@" in account:
            print("邮箱方式登录")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password
            }

    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()


if __name__ == '__main__':
    zhihu_login("18782902568", "admin123")
    # get_index()
    is_login()