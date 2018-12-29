# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'

from django.db import models
from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections

# Create your models here.

connections.create_connection(hosts=['192.168.1.3:9200'])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class JobboleArticleType(Document):
    """
    伯乐在线文章类型
    """
    # Completion是es自带的自动补全提示工具
    # 由于报错，所以自定义了analyzer，但实际上什么都没做
    suggest = Completion(analyzer=ik_analyzer)
    # 以下是scrapy的item
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()       # url md5 编码id
    front_image_url = Keyword()
    front_image_path = Keyword()
    vote_numbers = Integer()
    bookmark_numbers = Integer()
    comment_numbers = Integer()
    content = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")

    class Index:
        name = 'jobbole'
        doc_type = "article"

    class Meta:
        # name = "jobbole"
        doc_type = "article"


class ZhihuQuestionType(Document):
    """
    知乎question类型
    """
    # Completion是es自带的自动补全提示工具
    # 由于报错，所以自定义了analyzer，但实际上什么都没做
    suggest = Completion(analyzer=ik_analyzer)
    # 以下是scrapy的item
    zhihu_id = Keyword()
    topics = Text(analyzer="ik_max_word")
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    answer_num = Integer()
    comments_num = Integer()
    watch_user_num = Integer()
    click_num = Integer()
    crawl_time = Date()

    class Index:
        name = 'zhihu_question'
        doc_type = "question"

    class Meta:
        doc_type = "question"


class ZhihuAnswerType(Document):
    """
    知乎answer类型
    """
    # Completion是es自带的自动补全提示工具
    # 由于报错，所以自定义了analyzer，但实际上什么都没做
    suggest = Completion(analyzer=ik_analyzer)
    # 以下是scrapy的item
    zhihu_id = Keyword()
    url = Keyword()
    question_id = Keyword()
    author_id = Keyword()
    content = Text(analyzer="ik_max_word")
    praise_num = Integer()
    comments_num = Integer()
    create_time = Date()
    update_time = Date()
    crawl_time = Date()

    class Index:
        name = 'zhihu_answer'
        doc_type = "answer"

    class Meta:
        doc_type = "answer"


class LagouJobType(Document):
    """
    知乎answer类型
    """
    # Completion是es自带的自动补全提示工具
    # 由于报错，所以自定义了analyzer，但实际上什么都没做
    suggest = Completion(analyzer=ik_analyzer)
    # 以下是scrapy的item
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    salary = Text(analyzer="ik_max_word")
    job_city = Text(analyzer="ik_max_word")
    work_years = Text(analyzer="ik_max_word")
    degree_need = Text(analyzer="ik_max_word")
    job_type = Text(analyzer="ik_max_word")
    # 这里没有做处理，暂时保留text
    publish_time = Text(analyzer="ik_max_word")
    job_advantage = Text(analyzer="ik_max_word")
    job_desc = Text(analyzer="ik_max_word")
    job_addr = Text(analyzer="ik_max_word")
    company_name = Keyword()
    company_url = Keyword()
    tags = Text(analyzer="ik_max_word")
    crawl_time = Date()

    class Index:
        name = 'lagou'
        doc_type = "job"

    class Meta:
        doc_type = "job"


if __name__ == "__main__":
    JobboleArticleType.init()
    ZhihuQuestionType.init()
    ZhihuAnswerType.init()
    LagouJobType.init()
