# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'
# 参考：https://github.com/muchrooms/zheye

import sys
sys.path.insert(0, "../")
from zheye import zheye


z = zheye()
positions = z.Recognize('captcha_cn.gif')
print(positions)
