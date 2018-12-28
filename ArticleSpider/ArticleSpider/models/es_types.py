# -*- coding: utf-8 -*-
__author__ = 'dongnanzhy'

from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer

from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['192.168.1.3:9200'])


class ArticleType(Document):
    # 伯乐在线文章类型
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()       # url md5 编码id
    # 这个item应该是list，所以我们在output_processor写一个function什么都不做（不TakeFirst）
    front_image_url = Keyword()
    front_image_path = Keyword
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


if __name__ == "__main__":
    ArticleType.init()
