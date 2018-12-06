import re

'''
1)   ^ $ * ? + {2} {2, } {2,5}  |  
2)   [] [^] [a-z] .
3)   \s \S \w \W 
4)   [\u4E00-\u9FA5] () \d 
'''

# ^$.* 使用
line = "bobby123"
# 以b开头，后面跟任何字符重复任何多次, 最后以3结尾
regex_str = "^b.*3$"

match_obj = re.match(regex_str, line)
if match_obj:
    print("yes")

# ?() 使用
line = "boooooobby123"
# ()用来group并提取子串
# ?用来采用非贪婪匹配（从左向右匹配,遇到第一个完成）。 贪婪匹配是从右向左看，把最后一个匹配
regex_str1 = ".*?(b.*b).*"
regex_str2 = ".*?(b.*?b).*"
match_obj1 = re.match(regex_str1, line)
match_obj2 = re.match(regex_str2, line)
if match_obj1:
    print(match_obj1.group(1))
if match_obj2:
    print(match_obj2.group(1))

# + {} 使用
line = "boooobaaaooobbbaaby123"
# + 出现1次或多次
# {3, } 出现3词或以上; {2,5} 出现最少2次最多5次
regex_str = ".*?(b.{1}b).*"
match_obj = re.match(regex_str, line)
if match_obj:
    print(match_obj.group(1))

# | 使用
line = "boobby123"
# | 就是or的意思
regex_str = "((bobby|boobby)123)"
match_obj = re.match(regex_str, line)
if match_obj:
    print(match_obj.group(0))
    print(match_obj.group(1))
    print(match_obj.group(2))

# [] 使用
line = "18782902222"
# [] 就是任何一个,匹配电话号码。
regex_str = "(1[48357][0-9]{9})"
match_obj = re.match(regex_str, line)
if match_obj:
    print(match_obj.group(1))

# \s空格； \S不是空格
# \w 就是[A-Za-z0-9_]; \W与\w相反

# unicode编码 [\u4E00-\u9FA5]代表汉字
line = "study in 南京大学"
# 注意这里不加？会导致结果为"京大学"
regex_str = ".*?([\u4E00-\u9FA5]+大学)"
match_obj = re.match(regex_str, line)
if match_obj:
    print(match_obj.group(1))