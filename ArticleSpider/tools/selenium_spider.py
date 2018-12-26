# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'
# selenium测试代码

import time

from selenium import webdriver
from scrapy.selector import Selector


browser = webdriver.Chrome(executable_path='../chromedriver')

'''
# 自己写的知乎登录，有点问题
# browser.get('https://www.zhihu.com/signup?next=%2F')
# browser.find_element_by_css_selector(".SignContainer-switch span").click()
# browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input[name='username']").send_keys("xxx@163.com")
# browser.find_element_by_css_selector(".SignFlow-password input[name='password']").send_keys("xxx")
# browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

# copied 知乎登录
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
# 留一点时间来加载页面
time.sleep(2)
#进入登陆页面
browser.find_element_by_css_selector(".SignContainer-switch span").click()
time.sleep(1)
#点击社交网络账号登陆
browser.find_element_by_css_selector("span.Login-qrcode button").click()#点击qr_code登陆
time.sleep(10)

browser.refresh()
print(browser.page_source)
time.sleep(5)
browser.quit()
'''

'''
# facebook 登录
browser.get('https://www.facebook.com')
browser.find_element_by_id('email').send_keys('xxx')
browser.find_element_by_id('pass').send_keys('xxx')
browser.find_element_by_id('loginbutton').click()
'''

'''
# 完成微博模拟登录
browser.get("https://www.oschina.net/blog")
time.sleep(5)
browser.find_element_by_css_selector("#loginname").send_keys("liyao198705@sina.com")
browser.find_element_by_css_selector(".info_list.password input[node-type='password']").send_keys("da_ge_da")
browser.find_element_by_css_selector(".info_list.login_btn a[node-type='submitBtn']").click()
# 完成微博模拟鼠标下拉刷新（browser可以执行js）
for i in range(3):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
    time.sleep(3)
t_selector = Selector(text=browser.page_source)
print (t_selector.css(".tm-promo-price .tm-price::text").extract())
'''

'''
#设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
# 设置为不加载图片
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path='../chromedriver', chrome_options=chrome_opt)
browser.get("https://www.taobao.com")
time.sleep(8)
browser.quit()
'''

'''
#phantomjs, 无界面的浏览器(适用于在server上操作)，多进程情况下phantomjs性能会下降很严重
browser = webdriver.PhantomJS(executable_path="../phantomjs")
browser.get("https://detail.tmall.com/item.htm?spm=a230r.1.14.3.yYBVG6&id=538286972599&cm_id=140105335569ed55e27b&abbucket=15&sku_properties=10004:709990523;5919063:6536025")

print(browser.page_source)
browser.quit()
'''
