import json
import math
import redis
from datetime import datetime
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
from search.models import JobboleArticleType
from elasticsearch import Elasticsearch

client = Elasticsearch(hosts=['192.168.1.3:9200'])
redis_cli = redis.StrictRedis(host='192.168.1.3', port=6379)

# Create your views here.
class IndexView(View):
    # 首页
    def get(self, request):
        # redis中找到搜索频率最高的TOPN(TOP5)
        topn_search = [word.decode('utf8') for word in
                       redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)]
        return render(request, "index.html", {"topn_search": topn_search})


class SearchSuggest(View):
    def get(self, request):
        # 获取当前搜素关键词
        key_words = request.GET.get('s', '')
        # 获取所有es suggestion的title
        re_datas = []
        if key_words:
            s = JobboleArticleType.search()
            # 利用es的suggest搜索:
            # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters-completion.html#querying
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute()
            for match in suggestions.suggest.my_suggest[0].options:
                source = match._source
                re_datas.append("".join(source['title']))
        return HttpResponse(json.dumps(re_datas), content_type='application/json')


class SearchView(View):
    def get(self, request):
        # 获取搜素关键词
        key_words = request.GET.get("q", "")
        # 获取搜索的文章类型（article，zhihuquestion，lagou）
        s_type = request.GET.get("s_type", "article")
        # redis中搜索关键词+1，用来统计热门搜索
        redis_cli.zincrby("search_keywords_set", 1, key_words)
        # redis中找到搜索频率最高的TOPN(TOP5)
        topn_search = [word.decode('utf8') for word in
                       redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)]
        # 获取当前页码，默认为1
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1
        # 从redis获取爬取document总数
        jobbole_count = redis_cli.get("jobbole_count").decode('utf8')
        zhihuquestion_count = redis_cli.get("zhihuquestion_count").decode('utf8')
        lagou_count = redis_cli.get("lagou_count").decode('utf8')

        start_time = datetime.now()
        # es query with highlight
        response = client.search(
            index="jobbole",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["tags", "title", "content"]
                    }
                },
                "from": (page-1)*10,
                "size": 10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {}
                    }
                }
            }
        )
        end_time = datetime.now()
        # 获取返回时间
        last_seconds = (end_time - start_time).total_seconds()
        # 获取搜索document总数
        total_nums = response["hits"]["total"]
        # 获取page number总数
        page_nums = math.ceil(total_nums / 10)
        # 构建所有retrieval结果
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = "".join(hit["_source"]["title"])
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict["content"] = "".join(hit["_source"]["content"])[:500]

            hit_dict["create_date"] = hit["_source"]["create_date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page": page,
                                               "page_nums": page_nums,
                                               "total_nums": total_nums,
                                               "last_seconds": last_seconds,
                                               "all_hits": hit_list,
                                               "key_words": key_words,
                                               "jobbole_count": jobbole_count,
                                               "zhihuquestion_count": zhihuquestion_count,
                                               "lagou_count": lagou_count,
                                               "topn_search": topn_search})