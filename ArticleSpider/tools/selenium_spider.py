# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'
import time

from selenium import webdriver
from scrapy.selector import Selector


browser = webdriver.Chrome(executable_path='../chromedriver')
# browser = webdriver.Firefox(executable_path='../geckodriver')

# 自己写的，有点问题
# browser.get('https://www.zhihu.com/signup?next=%2F')
# browser.find_element_by_css_selector(".SignContainer-switch span").click()
# browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input[name='username']").send_keys("dongnanzhy@163.com")
# browser.find_element_by_css_selector(".SignFlow-password input[name='password']").send_keys("1989zz9891")
# browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

# facebook
# browser.get('https://www.facebook.com')
#
# browser.find_element_by_id('email').send_keys('xxx')
# browser.find_element_by_id('pass').send_keys('xxx')
# browser.find_element_by_id('loginbutton').click()

# copied
# browser.get("https://www.zhihu.com/signin")
# browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
#     "xxx")
# time.sleep(3)
# browser.find_element_by_css_selector(".SignFlow-password input").send_keys(
#     "xxx")
# time.sleep(3)
# browser.find_element_by_css_selector(
#     ".Button.SignFlow-submitButton").click()
# time.sleep(5)
# browser.refresh()
# print(browser.page_source)


#打开知乎首页
browser.get('https://www.zhihu.com/')
time.sleep(2)
#进入登陆页面
browser.find_element_by_css_selector(".SignContainer-switch span").click()
time.sleep(1)
#点击社交网络账号登陆
browser.find_element_by_css_selector("span.Login-qrcode button").click()#点击qr_code登陆
time.sleep(10)

browser.refresh()
print(browser.page_source)

# browser.quit()
