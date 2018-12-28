# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

import MySQLdb
import MySQLdb.cursors

from models.es_types import ArticleType
from w3lib.html import remove_tags


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


# 自定义json文件导出
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        # 注意ensure_ascii=False不然中文显示会有错误
        lines = json.dumps(dict(item), ensure_ascii=False)
        self.file.write(lines)
        # 注意要return item 因为pipeline下一项可能会使用它
        return item

    # spider close 会调用
    def spider_closed(self, spider):
        self.file.close()


# 调用scrapy提供的json exporter导出json文件
class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('article_exporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


# 采用同步机制写入mysql -- 仅供学习用，后面都用异步方法
class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('192.168.1.3',
                                    'root',
                                    '1989zz9891',
                                    'article_spider',
                                    charset='utf8',
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, create_date, 
                                        front_image_url, front_image_path, comment_nums, vote_nums, 
                                        bookmark_nums, tags, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item['title'],
                                         item['url'],
                                         item['url_object_id'],
                                         item['create_date'],
                                         item['front_image_url'],
                                         item['front_image_path'],
                                         item['comment_numbers'],
                                         item['vote_numbers'],
                                         item['bookmark_numbers'],
                                         item['tags'],
                                         item['content']
                                         ))
        self.conn.commit()
        return item


# 异步机制写入mysql
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 注意：scrapy会自动调用这个类方法并把setting传进来
    @classmethod
    def from_settings(cls, settings):
        # 这里dbparams里的key值要与MySQLdb参数值相同
        dbparams = dict(
            host = settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        # 建立连接池 args=mysqldb package name,
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item构建不同的sql语句并插入到mysql中
        # 可以根据不同的classname做判断，if item.__class__.__name__ == "xxxx"，但这样不好

        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


# 自定义图像保存pipeline， 继承scrapy的ImagesPipeline
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        # 只对有front image的网页生效
        if "front_image_url" in item:
            image_file_path = ''
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item


class ElasticsearchPipeline(object):
    # 将数据写入到es中

    def process_item(self, item, spider):
        # 将item转为es
        item.save_to_es()

        return item
