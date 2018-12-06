# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的url并交给scrapy下载后并进行解析
        获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        :param response:
        :return:
        """

        # 解析列表页所有文章url并交给scrapy下载后并进行解析
        # ::attr(href) 代表去属性名为href的值
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            # 继续parse下一页url和image_url
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            # 根据是否有域名自动做url拼接，parse.urljoin(response.url, post_url)
            # 将url交给scrapy继续parse, 异步协程
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": parse.urljoin(response.url, image_url)},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy下载
        # 通过两个class name 来提取css
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def parse_detail(self, response):
        """
        提取文章的具体字段， 回调函数
        :param response:
        :return:
        """
        article_item = JobBoleArticleItem()
        # 文章封面图
        front_image_url = response.meta.get("front_image_url", "")

        """
        '''
        # 方法一：【通过XPath提取字段】
        # 可以在浏览器inspect html里copy Xpath
        # chrome return 和 firefox return 可能不一样。 有时直接copy的值无法获得数据, 因为获取的是动态html而不是原始html
        
        # 标题
        # extract_first() 就是 extract()[0]，还可以传一个default值
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        # 创建时间
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first("").strip().replace("·", "").strip()
        # 点赞数
        vote_numbers = int(response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first(""))
        # 收藏数
        bookmark_numbers = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first("")
        match_re = re.match(r".*?(\d+).*", bookmark_numbers)
        if match_re:
            bookmark_numbers = match_re.group(1)
        # 评论数
        comment_numbers = response.xpath("//a[@href='#article-comment']/span/text()").extract_first("")
        match_re = re.match(r".*?(\d+).*", comment_numbers)
        if match_re:
            comment_numbers = match_re.group(1)
        # 正文 (不提取text而是提取整个html结构)
        content = response.xpath("//div[@class='entry']").extract_first("")
        # 标签
        tags = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tags = ','.join([item for item in tags if not item.strip().endswith('评论')])
        '''
        # 方法二：【通过CSS选择器提取字段】
        # 标题
        # ::text 代表去text
        title = response.css(".entry-header h1::text").extract_first("")
        # 创建时间
        create_date = response.css('p.entry-meta-hide-on-mobile::text').extract_first("").strip().replace("·","").strip()
        # 点赞数
        vote_numbers = int(response.css(".vote-post-up h10::text").extract_first(""))
        # 收藏数
        bookmark_numbers = response.css(".bookmark-btn::text").extract_first("")
        match_re = re.match(r".*?(\d+).*", bookmark_numbers)
        if match_re:
            bookmark_numbers = int(match_re.group(1))
        else:
            bookmark_numbers = 0
        # 评论数
        comment_numbers = response.css("a[href='#article-comment'] span::text").extract_first("")
        match_re = re.match(r".*?(\d+).*", comment_numbers)
        if match_re:
            comment_numbers = int(match_re.group(1))
        else:
            comment_numbers = 0
        # 正文 (不提取text而是提取整个html结构)
        content = response.css("div.entry").extract_first("")
        # 标签
        tags = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        tags = ','.join([item for item in tags if not item.strip().endswith('评论')])

        # 赋值生成item
        article_item['url_object_id'] = get_md5(response.url)
        article_item['title'] = title
        article_item['url'] = response.url
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item['create_date'] = create_date
        # scrapy 的image下载接受的是数组
        article_item['front_image_url'] = [front_image_url]
        article_item['vote_numbers'] = vote_numbers
        article_item['bookmark_numbers'] = bookmark_numbers
        article_item['comment_numbers'] = comment_numbers
        article_item['tags'] = tags
        article_item['content'] = content
        """

        # 通过item loader 加载 item
        # 更加简洁可配置
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("vote_numbers", ".vote-post-up h10::text")
        item_loader.add_css("bookmark_numbers", ".bookmark-btn::text")
        item_loader.add_css("comment_numbers", "a[href='#article-comment'] span::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()

        yield article_item
