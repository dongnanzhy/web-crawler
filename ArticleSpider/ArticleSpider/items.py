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

from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT


# default class, just pass
class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    # Used in JobBoleArticleItem input processor
    create_date = value.strip().replace("·", "").strip()
    try:
        create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def remove_comment_tags(value):
    # 去掉tags中提取的评论
    if '评论' in value:
        return ""
    else:
        return value


# 自定义ItemLoader,设置默认output_processor
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
        input_processor=MapCompose(extract_num)
    )
    bookmark_numbers = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    comment_numbers = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        # Join 是用一个连接符连接list
        output_processor=Join(",")
    )

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, create_date, 
                                        front_image_url, front_image_path, comment_nums, vote_nums, 
                                        bookmark_nums, tags, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE comment_nums=VALUES(comment_nums), vote_nums=VALUES(vote_nums), bookmark_nums=VALUES(bookmark_nums)
        """
        params = (self['title'],
                  self['url'],
                  self['url_object_id'],
                  self['create_date'],
                  # TODO: 这里front_image_url应该是个list，所以取第一个元素。但不这么做也不会报错？
                  self['front_image_url'][0],
                  self['front_image_path'],
                  self['comment_numbers'],
                  self['vote_numbers'],
                  self['bookmark_numbers'],
                  self['tags'],
                  self['content'])
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题 item
    # 这里也可以像JobBoleArticleItem一样处理，但我们用另一种方法实验一下
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, 
                                        content, answer_num, comments_num, watch_user_num, 
                                        click_num, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """
        # 虽然zhihu_id用的是add_value()，但传进来后还是list。url同理
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        # 由于知乎在数字中加入了逗号，这里做了一点小改动
        answer_num = extract_num("".join([text.replace(",", "") for text in self["answer_num"]]))
        comments_num = extract_num("".join([text.replace(",", "") for text in self["comments_num"]]))
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = int(self["watch_user_num"][1].replace(",", ""))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答 item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎answer表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, 
                                        content, praise_num, comments_num, 
                                        create_time, update_time, crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
              update_time=VALUES(update_time)
        """
        # zhihu answer 是通过知乎api获得的，不是list直接就是值
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)

        params = (self['zhihu_id'], self['url'],
                  self['question_id'], self['author_id'], self['content'],
                  self['praise_num'], self['comments_num'], create_time, update_time,
                  self['crawl_time'].strftime(SQL_DATETIME_FORMAT))

        return insert_sql, params
