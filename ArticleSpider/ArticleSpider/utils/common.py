# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'
import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    # 从字符串中提取出数字
    match_re = re.match(r".*?(\d+).*", text)
    if match_re:
        numbers = int(match_re.group(1))
    else:
        numbers = 0

    return numbers


if __name__ == '__main__':
    print(get_md5("http://jobbole.com"))
