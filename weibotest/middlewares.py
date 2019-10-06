
import random
import pymongo
import json
import logging
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from weibotest.settings import USER_AGENT_POOL
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from weibotest.settings import MONGO_HOST
from weibotest.settings import MONGO_PORT
from weibotest.settings import MONGO_DB_NAME
from weibotest.settings import COOKIES_COLLECTION_NAME
from weibotest.cookies import init_cookies
import time


class WeibotestSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WeibotestDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# User-Agent池中间件
class WeibotestUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(USER_AGENT_POOL)


# Cookie池中间件
class WeiboCookiesMiddleware(RetryMiddleware):

    def __init__(self, settings, crawler):
        self.logger = logging.getLogger("---Cookies池---")
        RetryMiddleware.__init__(self, settings)
        # 模拟登陆初始化 cookies，若注释掉需要手动向数据库中写入 cookies
        # 写入格式为: username(string) cookies(json string)
        # | username | cookies |
        # | "qaswazxs@126.com" | "{"SSOLoginState": "1570157316", "SUB": "_2A25wksNUDeRhGedI7lER9i_Jzj6IHXVQfO0crDV6PUJbktANLW7HkW1NVzqyC0ntAqR8szHeQCefNRM41xZZJ3YI"}" |
        # init_cookies()
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB_NAME]
        col = db[COOKIES_COLLECTION_NAME]
        self.cookies_pool = []
        for item in col.find():
            self.cookies_pool.append(json.loads(item['cookies']))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        time.sleep(random.randint(0,3))
        random_cookies = random.choice(self.cookies_pool)
        self.logger.warning("本次请求使用 cookies:")
        self.logger.warning(random_cookies)
        request.cookies = random_cookies


