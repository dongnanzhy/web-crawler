import re

# line = "xxx出生于2001年6月1日"
# line = "xxx出生于2001/6/1"
line = "xxx出生于2001/06/01"
# line = "xxx出生于2001-6-1"
# line = "xxx出生于2001-06-01"
# line = "xxx出生于2001-06"

# 这里注意[年-/]会报错，一般"-"都放在最后因为他有特殊含义
regex_str = ".*出生于(\d{4}[年/-]\d{1,2}([月/-]\d{1,2}|[月/-]$|$))"
match_obj = re.match(regex_str, line)
if match_obj:
    print(match_obj.group(1))