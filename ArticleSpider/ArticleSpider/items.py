# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    create_date = value.strip().replace("·", "").strip()
    try:
        create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def get_nums(value):
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        numbers = int(match_re.group(1))
    else:
        numbers = 0

    return numbers


def remove_comment_tags(value):
    # 去掉tags中提取的评论
    if '评论' in value:
        return ""
    else:
        return value


# 自定义ItemLoader
class ArticleItemLoader(ItemLoader):
    # 注意：TakeFirst的作用是把css读取的list转化成其第一个element输出
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    # MapCompose 可以叠加多个函数
    # 注意：这里title是通过css读取的list，input_processor会对list里每一个元素做操作， function输入时list里的element
    # MapCompose 可以接受任一多的function，一次调取
    title = scrapy.Field(
        input_processor=MapCompose()
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
        # output_processor=TakeFirst()  由于自定义ItemLoader,所以不需要一次定义output_processor
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()       # url md5 编码id
    # 这个item应该是list，所以我们在output_processor写一个function什么都不做（不TakeFirst）
    front_image_url = scrapy.Field(
        output_processor=MapCompose(lambda value: value)
    )
    front_image_path = scrapy.Field()
    vote_numbers = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    bookmark_numbers = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_numbers = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        # Join 是用一个连接符连接list
        output_processor=Join(",")
    )
