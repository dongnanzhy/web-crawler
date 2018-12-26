# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'

import re

str1 = 'abc python'
print(str1.find('abc'))
print(str1.startswith('abc'))

# A【基础re知识】
# 加"r"代表元字符，
# 例如，普通字符串要定义"\\n",元字符串只需要定义"\n"
pa = re.compile(r'abc')
# pa = re.compile(r'ABC', re.I) # ignore 大小写
match_obj = pa.match(str1)

# 注意： match_obj.group 如果regex有括号返回tuple，否则返回str
print(match_obj.group())
print(match_obj.span())

# B【正则表达式】 补充之前
# 1. 普通： \w \W \s \S \d \D a-z
# 2. 特殊字符：
#   2-a. []代表里面字符的任意一个
#   2-b. {m,n}代表出现m->n次
#   2-c. *， +， ？ 单独出现分别代表匹配前一个字符0次或更多，1次或更多，0次或1次
#   2-d. 注意： *?, +?, ?? 代表匹配模式变成非贪婪匹配（尽可能少匹配字符，所以"*?"最少是0次，"+?"最少是1次，"??"最少是0次）(see example)
# 3. 边界匹配
#   3-a. ^ 开头  $ 结尾
#   3-b. \A, \Z 指定字符串必须出现在开头或者结尾  (see example)
# 4. 分组匹配
#   4-a. | 匹配左右任意一个表达式
#   4-b. (xx) 括号中的表达式作为一个分组 ===> \<number> 引用标号为number的分组匹配
#   4-c. (?P<name>) 给分组起一个名字   ===> (?P=name) 引用别名为name的分组匹配


# 2-d
match_obj = re.match(r'[1-9][a-z]*?', '1bc')
print(match_obj.group())   # result=1 "bc"被非贪婪没有匹配

# 3-b
match_obj = re.match(r'\Adongnan[\w]*', 'adongnanzhy')
print(match_obj is None)   # result=None 必须要以"dongnan"开头才可以

# 4-b
# match_obj = re.match(r'\w{4,16}@(163|126).com', 'dongnanzhy@126.com')
match_obj = re.match(r'<(\w+>)\w+</\1', '<book>python</book>')   # 判断xml格式
print(match_obj.group())   #注意上面将"\w+>"作为分组后，在后面通过"\1" 引用了这个分组

# 4-c
match_obj = re.match(r'<(?P<mark_name>\w+>)\w+</(?P=mark_name)', '<book>python</book>')   # 判断xml格式
print(match_obj.group())   #注意上面将"\w+>"作为分组后，在后面通过"\1" 引用了这个分组

# C【re方法介绍】
# search: 字符串中查找匹配， 返回match_obj
str2 = 'dongnanzhy videonum = 1000'
info = re.search(r'\d+', str2)
print(info.group())

# findall: 查找字符串所有匹配，返回list
str2 = 'python=80, java=90'
info = re.findall(r'\d+', str2)
print(info)

# sub: 将字符串匹配正则表达式的部分替换，返回str
str3 = 'dongnanzhy videonum = 1000'
# info = re.sub(r'\d+', '1001', str3)
# 注意：替换的值也可以是一个函数
info = re.sub(r'\d+', lambda match: str(int(match.group())+1), str3)
print(info)


# split: 根据匹配分割字符串，返回分割字符串组成的list
str4 = 'dongnanzhy:C C++ Python,Java'
info = re.split(r':|\s|,', str4)
print(info)




