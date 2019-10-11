# -*- coding: utf-8 -*-
import scrapy
import json
from weibotest.items import FollowsInfoItem


class FollowsSpider(scrapy.Spider):
    name = 'follows'
    # allowed_domains = ['weibo.cn']
    # url
    url_1 = "https://weibo.cn/"
    url_2 = [
        # 'nju1902'
    ]  # 此处已改为从文件读取
    url_3 = "/follow?page="
    url_4 = 1  # 搜索页面
    url_5 = 37  # 高校顺序    #TODO:起始高校位置
    tid = '' #高校编号

    pageNum = 100  # 正在爬取的高校关注页数
    headers = {  # 头部
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
    }
    meta = {
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }

    def start_requests(self):
        # 重写了start_requests方法，可以按照自定义顺序爬取界面
        with open('weibotest/schools.js', 'r', encoding='UTF-8') as f:
            schArray = json.loads(f.read())
            for sch in schArray["university_list"]:
                self.url_2.append(sch['id'])
                print(sch['id'])
        return [
            scrapy.Request(self.getUrl(), callback=self.parse, headers=self.headers)
        ]

    def getUrl(self):
        if(self.url_5<len(self.url_2)):
            url=self.url_1+self.url_2[self.url_5]
            self.url_5 = self.url_5 + 1
            self.url_4 = 1
            return url
    def getPageUrl(self):
        if(self.url_4<=self.pageNum):
            url=self.url_1+str(self.tid)+self.url_3+str(self.url_4)
            self.url_4=self.url_4+1
            # print(url)
            return url

    def parse(self, response):
        tid=response.xpath('/ html / body / div[@ class="u"] / div / a[1] / @href').extract()
        tid=tid[0]
        tid=tid[1:str(tid).index('/', 1)]
        self.tid=tid
        yield scrapy.Request(self.getPageUrl(), callback=self.sub_parse, headers=self.headers)


    def sub_parse(self, response):
        # print(response.xpath('/ html / body / table[1] / tr /td[1]/a/@href ').extract())
        # print(response.body)
        # item=FollowsInfoItem()
        followsList=[]
        if(self.url_4==2):
            wbPage=response.xpath('/html/body/div[@ id="pagelist"]/form/div/text()').extract()
            self.pageNum = wbPage[-1][str(wbPage[-1]).index('/') + 1:len(wbPage[-1]) - 1]
            self.pageNum=int(self.pageNum)
            print(self.pageNum)
            # item['id']=self.url_2[self.url_5-1]
            # item['followsList']=[]
        else:
            followsList=response.meta['followsList']
            # item=response.meta['item']

        # print(response.xpath('/html/body/table/tr/td[1]/a').extract())
        for user in response.xpath('/html/body/table'):
            dict={"id":"","name":""}
            id=user.xpath('tr/td[1]/a/@href').extract()
            # print(id)
            id=str(id[0])
            id=id[id.rfind('/')+1:len(id)]
            dict["id"]=id
            name=user.xpath('tr/td[2]/a[1]/text()').extract()
            name=str(name[0])
            dict["name"]=name
            followsList.append(dict)
            # print(followsList)

        if self.url_4>self.pageNum:
            item=FollowsInfoItem()
            item['id']=self.url_2[self.url_5-1]
            item['followsList']=followsList
            print(len(followsList))
            self.printItem(item)
            yield item
            yield scrapy.Request(self.getUrl(), callback=self.parse, headers=self.headers)
        else:
            mRequest=scrapy.Request(self.getPageUrl(),callback=self.sub_parse,headers=self.headers)
            mRequest.meta['followsList']=followsList
            yield mRequest



    def printItem(self,item):
        print('id: '+item["id"])
        print(item["followsList"])

