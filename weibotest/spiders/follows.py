# -*- coding: utf-8 -*-
import scrapy
import json
from weibotest.items import FollowsInfoItem


class FollowsSpider(scrapy.Spider):

    name = 'follows'
    # allowed_domains = ['weibo.cn']
    url_1 = "https://weibo.cn/"
    # 用户 id: 现从文件读取
    url_2 = [
        # 'nju1902'
    ]
    url_3 = "?page="
    # 起始页面
    url_4 = 2202
    # 当前高校下标(0~107)
    url_5 = 88  # TODO: 起始高校位置
    tid = ''  # 高校编号
    # 当前高校总微博数
    weiboNum = 3058
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
    }
    meta = {
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }

    def start_requests(self):
        # 重写了start_requests方法，可以按照自定义顺序爬取界面
        with open('weibotest/schools.js', 'r', encoding='UTF-8') as f:
            sch_array = json.loads(f.read())
            for sch in sch_array["university_list"]:
                self.url_2.append(sch['id'])
                print(sch['id'])
        return [
            scrapy.Request(self.get_url(), callback=self.parse, headers=self.headers)
        ]

    def get_url(self):
        if self.url_5 < len(self.url_2):
            url = self.url_1 + self.url_2[self.url_5]
            self.url_5 = self.url_5 + 1
            self.url_4 = 1
            return url
        
    def get_page_url(self):
        if self.url_4 <= self.page_num:
            url = self.url_1 + str(self.tid) + self.url_3 + str(self.url_4)
            self.url_4 = self.url_4+1
            # print(url)
            return url

    def parse(self, response):
        tid = response.xpath('/ html / body / div[@ class="u"] / div / a[1] / @href').extract()
        tid = tid[0]
        tid = tid[1:str(tid).index('/', 1)]
        self.tid = tid
        yield scrapy.Request(self.get_page_url(), callback=self.sub_parse, headers=self.headers)

    def sub_parse(self, response):
        # print(response.xpath('/ html / body / table[1] / tr /td[1]/a/@href ').extract())
        # print(response.body)
        # item = FollowsInfoItem()
        follow_list = []
        if self.url_4 == 2:
            wb_page = response.xpath('/html/body/div[@ id="pagelist"]/form/div/text()').extract()
            self.page_num = wb_page[-1][str(wb_page[-1]).index('/') + 1:len(wb_page[-1]) - 1]
            self.page_num = int(self.page_num)
            print(self.page_num)
            # item['id'] = self.url_2[self.url_5-1]
            # item['follow_list'] = []
        else:
            follow_list = response.meta['follow_list']
            # item = response.meta['item']

        # print(response.xpath('/html/body/table/tr/td[1]/a').extract())
        for user in response.xpath('/html/body/table'):
            dict = {"id": "", "name": ""}
            id = user.xpath('tr/td[1]/a/@href').extract()
            # print(id)
            id = str(id[0])
            id = id[id.rfind('/')+1:len(id)]
            dict["id"] = id
            name = user.xpath('tr/td[2]/a[1]/text()').extract()
            name = str(name[0])
            dict["name"] = name
            follow_list.append(dict)
            # print(follow_list)

        if self.url_4 > self.page_num:
            item = FollowsInfoItem()
            item['id'] = self.url_2[self.url_5-1]
            item['follow_list'] = follow_list
            print(len(follow_list))
            self.print_item(item)
            yield item
            yield scrapy.Request(self.get_url(), callback=self.parse, headers=self.headers)
        else:
            mRequest = scrapy.Request(self.get_page_url(), callback=self.sub_parse, headers=self.headers)
            mRequest.meta['follow_list'] = follow_list
            yield mRequest

    def print_item(self, item):
        print('id: '+item["id"])
        print(item["follow_list"])

