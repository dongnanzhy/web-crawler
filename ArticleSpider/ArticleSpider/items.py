# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import redis
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from w3lib.html import remove_tags

from utils.common import extract_num
from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from models.es_types import JobboleArticleType, ZhihuAnswerType, ZhihuQuestionType, LagouJobType

from elasticsearch_dsl.connections import connections
es = connections.create_connection(hosts=['192.168.1.3:9200'])

redis_cli = redis.StrictRedis(host="192.168.1.3", port=6379)


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
    # 去掉jobbole网tags中提取的评论
    if '评论' in value:
        return ""
    else:
        return value


def gen_suggests(index, info_tuple):
    """
    根据字符串生成搜索建议数组，供es suggest调用
    :param index:
    :param info_tuple:
    :return:
    """
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index,
                                       body={"analyzer": "ik_max_word", "text": text})
            analyzed_words = set([r["token"] for r in words['tokens'] if len(r['token']) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            used_words.update(new_words)
            suggests.append({"input": list(new_words), "weight": weight})
    return suggests


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

    def save_to_es(self):
        article = JobboleArticleType()

        article.title = self.get('title', ''),
        article.url = self['url']
        # 注意这里保存到了meta id里
        article.meta.id = self['url_object_id']
        article.create_date = self.get('create_date', datetime.datetime.now().date())
        article.front_image_url = self['front_image_url'][0]
        if "front_image_path" in self:
            article.front_image_path = self['front_image_path']
        article.comment_numbers = self.get('comment_numbers', 0)
        article.vote_numbers = self.get('vote_numbers', 0)
        article.bookmark_numbers = self.get('bookmark_numbers', 0)
        article.tags = self.get('tags', '')
        # 调用w3lib来remove tag
        article.content = remove_tags(self['content'])

        article.suggest = gen_suggests(JobboleArticleType._index._name,
                                       ((article.title, 10), (article.tags, 7), (article.content, 5)))

        article.save()
        # redis中记录爬取document数目
        redis_cli.incr("jobbole_count")
        return


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

    def save_to_es(self):
        question = ZhihuQuestionType()

        question.meta.id = self['zhihu_id'][0]
        question.zhihu_id = self['zhihu_id'][0]
        question.topics = ",".join(self.get('topics', [""]))
        question.url = self['url'][0]
        question.title = "".join(self.get("title", [""]))
        question.content = remove_tags("".join(self.get("content", [""])))

        # 由于知乎在数字中加入了逗号，这里做了一点小改动
        answer_num = extract_num("".join([text.replace(",", "") for text in self.get('answer_num', [""])]))
        comments_num = extract_num("".join([text.replace(",", "") for text in self.get('comments_num', [""])]))
        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = int(self["watch_user_num"][1].replace(",", ""))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = 0

        question.answer_num = answer_num
        question.comments_num = comments_num
        question.watch_user_num = watch_user_num
        question.click_num = click_num
        question.crawl_time = datetime.datetime.now().date()

        question.suggest = gen_suggests(ZhihuQuestionType._index._name,
                                       ((question.title, 10), (question.topics, 7), (question.content, 5)))

        question.save()
        # redis中记录爬取document数目
        redis_cli.incr("zhihuquestion_count")
        return


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

    def save_to_es(self):
        answer = ZhihuAnswerType()

        answer.meta.id = self['zhihu_id']
        answer.zhihu_id = self['zhihu_id']
        answer.url = self['url']
        answer.question_id = self['question_id']
        answer.author_id = self['author_id']
        answer.content = self['content']
        answer.praise_num = self.get('praise_num', 0)
        answer.comments_num = self.get('comments_num', 0)
        if 'create_time' in self:
            answer.create_time = datetime.datetime.fromtimestamp(self['create_time'])
        else:
            answer.create_time = datetime.datetime.now().date()
        if 'update_time' in self:
            answer.update_time = datetime.datetime.fromtimestamp(self['update_time'])
        else:
            answer.update_time = datetime.datetime.now().date()
        answer.crawl_time = self['crawl_time']

        answer.suggest = gen_suggests(ZhihuAnswerType._index._name,
                                      [(answer.content, 5)])

        answer.save()
        # redis中记录爬取document数目
        redis_cli.incr("zhihuanswer_count")
        return


def remove_splash(value):
    #去掉拉勾网工作城市等的斜线
    return value.replace("/","")


def handle_jobaddr(value):
    # 处理拉勾网address问题
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        # 利用w3lib库直接去掉tag
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
        """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["job_addr"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params

    def save_to_es(self):
        job = LagouJobType()

        job.meta.id = self['url_object_id']
        job.title = self['title']
        job.url = self['url']
        job.url_object_id = self['url_object_id']
        job.salary = self.get('salary', '')
        job.job_city = self.get('job_city', '')
        job.work_years = self.get('work_years', '')
        job.degree_need = self.get('degree_need', '')
        job.job_type = self.get('job_type', '')
        job.publish_time = self.get('publish_time', '')
        job.job_advantage = self.get('job_advantage', '')
        job.job_desc = self.get('job_desc', '')
        job.job_addr = self.get('job_addr', '')
        job.company_name = self.get('company_name', '')
        job.company_url = self.get('company_url', '')
        job.tags = self.get('tags', '')
        job.crawl_time = self['crawl_time']

        job.suggest = gen_suggests(LagouJobType._index._name,
                                   ((job.title, 10), (job.tags, 8), (job.job_desc, 5)))

        job.save()
        # redis中记录爬取document数目
        redis_cli.incr("lagou_count")
        return
