import pymongo
import scrapy
from weibotest.items import BaseInfoItem
from weibotest.items import WeiboInfoItem
import re
import datetime
import json
import traceback

from weibotest.settings import MONGO_HOST, MONGO_PORT, MONGO_DB_NAME, SCHOOL_BASE_INFO


class WeiboSpider(scrapy.Spider):
    name="weibo"
    #url
    url_1="https://weibo.cn/"
    url_2=[
        # 'nju1902'
    ]   #此处已改为从文件读取
    url_3="?page="
    url_4= 1976  #搜索页面
    url_5 = 20  #高校顺序url_2    #TODO:起始高校位置

    weiboNum=2094  #正在爬取的高校微博页数
    headers={               #头部
        'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'
    }
    meta={
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }
    cookies = {
        '_T_WM': '43586327469',
        'ALF': '1572708198',
        'SCF': 'Ath3LGFZX0FTfy5B1hPlXwqPBhTi85tlI__-vO50T-QtwVFOA8qTZQHnYu9WvdPwQ3zfeo07OVpU2CoVH7jE3Lw.',
        'SUB': '_2A25wkmIoDeRhGedI7lER9i_Jzj6IHXVQfQ5grDV6PUJbktAKLWn8kW1NVzqyC3OH20h5draiHZcnyiIbKjKFDlcg',
        'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9Whnyn0O9rOclhlg5fY2Qk5O5JpX5K-hUgL.Fo2cSKe7So2fSKz2dJLoIpH1IgUQU8iyIg4KdNHV9GSFdNiDdJMt',
        'SUHB': '06ZUp17PgQTv88',
        'SSOLoginState': '1570116217'
    }


    def parse(self, response):

        if(self.url_4==1):
            name = self.url_2[self.url_5]
            wb=response.xpath('/html/body/div[@ class="u"]/div/span/text()').extract()
            wb=wb[0][3:len(wb[0])-1]
            fans = response.xpath('/ html / body / div[@ class="u"] / div / a[2] / text()').extract()
            fans=fans[0][3:len(fans[0])-1]
            follows = response.xpath('/ html / body / div[@ class="u"] / div / a[1] / text()').extract()
            follows=follows[0][3:len(follows[0])-1]
            # self.weiboNum=int(wb)/10
            item=BaseInfoItem()
            item['id']=name
            item['wb']=wb
            item['fans']=fans
            item['follows']=follows
            yield item
            print(name)
            print("微博数： "+wb)
            print("粉丝数： "+fans)
            print("关注数： "+follows)


        url=self.getNextUrl()
        if(len(url)!=0):
            yield scrapy.Request(url, callback=self.parse, headers=self.headers, cookies=self.cookies)


    def start_requests(self):
        #重写了start_requests方法，可以按照自定义顺序爬取界面
        with open('weibotest/schools.js','r',encoding='UTF-8') as f:
            schArray=json.loads(f.read())
            for sch in schArray["university_list"]:
                self.url_2.append(sch['id'])
                print(sch['id'])
        return [
            scrapy.Request(self.getNextUrl(), callback=self.sub_parse, headers=self.headers, cookies=self.cookies)
        ]

    def getNextUrl(self):
        if(self.url_5<30):   #TODO:结束高校位置
            url=self.url_1+self.url_2[self.url_5]+self.url_3
            if(self.url_4<self.weiboNum):
                #self.weiboNum
                url=url+str(self.url_4)
                self.url_4=self.url_4+1
            else:
                self.url_5=self.url_5+1
                if(self.url_5==len(self.url_2) or self.url_5==30):  #TODO:这里这里，记得加
                    return ''
                self.url_4=1
                url = self.url_1 + self.url_2[self.url_5] + self.url_3
                url = url + str(self.url_4)
                self.url_4 = self.url_4 + 1
            return url
        else:
            return ""

    def sub_parse(self,response):

        if self.url_4 == 2:
            # print(self.weiboNum)
            wbPage=response.xpath('/html/body/div[@ id="pagelist"]/form/div/text()').extract()
            self.weiboNum=wbPage[-1][str(wbPage[-1]).index('/')+1:len(wbPage[-1])-1]
            # print(wbPage)
            self.weiboNum=int(self.weiboNum)
            print(self.weiboNum)

        for i in range(1,len(response.xpath('/html/body/div[@ class="c"]'))-1):
            try:
                item = WeiboInfoItem()
                repost = response.xpath(
                    '/html/body/div[@ class="c"][' + str(i) + ']/div[1]/span[1][@ class="cmt"]/a/text()').extract()
                if (len(repost) == 0):  # 原创微博
                    content = ''
                    contents = response.xpath('/html/body/div[@ class="c"][' + str(i) + ']/div[last()]').css(
                        '*::text').extract()
                    contents2 = response.xpath('/html/body/div[@ class="c"][' + str(i) + ']/div[1]').css(
                        '*::text').extract()
                    # print(contents)
                    # print(contents[-2][-2:-1])
                    if contents[-2][-2:-1] == '来':
                        contents=contents[0:len(contents)-1]
                    # print(contents)
                    # print(contents2)
                    if contents[1] != '原图':
                        imgs = 0
                        contents2=contents2[0:len(contents2)-10]
                    else:
                        if len(contents2)==1:
                            imgs=1
                        elif contents2[-2][0:2] == '组图':
                            imgs = contents2[-2][3]
                        else:
                            imgs = 1
                    item['id'] = self.url_2[self.url_5]
                    item['repost'] = ''
                    item['tag'] = []
                    item['at'] = []
                    item['imgNum'] = imgs
                    item['likeNum'] = contents[-9][2:len(contents[-9]) - 1]
                    item['repostNum'] = contents[-7][3:len(contents[-7]) - 1]
                    item['commentNum'] = contents[-5][3:len(contents[-5]) - 1]
                    item['time'] = self.getTime(contents[-1])
                    temp = response.xpath('/html/body/div[@ class="c"][' + str(i) + ']/div[1]/span/a[last()]')
                    if len(temp.xpath('text()').extract()) == 0:
                        if len(contents2) >= 3:
                            if contents2[-3] == '收藏':
                                for j in range(0, len(contents2) - 11):
                                    content = content + contents2[j]
                            else:
                                if contents2[-1] == ']':
                                    for j in range(0, len(contents2) - 3):
                                        content = content + contents2[j]
                                else:
                                    for j in range(0, len(contents2)):
                                        content = content + contents2[j]
                        elif contents2[-1] == ']':
                            for j in range(0, len(contents2) - 3):
                                content = content + contents2[j]
                        else:
                            for j in range(0, len(contents2)):
                                content = content + contents2[j]
                        item['content'] = content
                        item['tag'] = self.getTags(item['content'])
                        item['at'] = self.getAts(item['content'])
                        # self.printWeiboInfoItem(item)
                        yield item
                    elif (temp.xpath('text()').extract())[0] == '全文':  # 如果需要访问全文
                        #有备无患，用于在无法访问详情界面时得到大致内容
                        if len(contents2) >= 3:
                            if contents2[-3] == '收藏':
                                for j in range(0, len(contents2) - 11):
                                    content = content + contents2[j]
                            else:
                                if contents2[-1] == ']':
                                    for j in range(0, len(contents2) - 3):
                                        content = content + contents2[j]
                                else:
                                    for j in range(0, len(contents2)):
                                        content = content + contents2[j]
                        elif contents2[-1] == ']':
                            for j in range(0, len(contents2) - 3):
                                content = content + contents2[j]
                        else:
                            for j in range(0, len(contents2)):
                                content = content + contents2[j]
                        item['content'] = content
                        item['tag'] = self.getTags(item['content'])
                        item['at'] = self.getAts(item['content'])
                        #访问具体内容
                        mRequest = scrapy.Request('https://weibo.cn' + (temp.xpath('@href').extract())[0],
                                                  callback=self.getContent, headers=self.headers, cookies=self.cookies,
                                                  priority=1)
                        mRequest.meta['item'] = item
                        yield mRequest
                    else:  # 不需要访问全文
                        if len(contents2) >= 3:
                            if contents2[-3] == '收藏':
                                for j in range(0, len(contents2) - 11):
                                    content = content + contents2[j]
                            else:
                                if contents2[-1] == ']':
                                    for j in range(0, len(contents2) - 3):
                                        content = content + contents2[j]
                                else:
                                    for j in range(0, len(contents2)):
                                        content = content + contents2[j]
                        elif contents2[-1] == ']':
                            for j in range(0, len(contents2) - 3):
                                content = content + contents2[j]
                        else:
                            for j in range(0, len(contents2)):
                                content = content + contents2[j]
                        item['content'] = content
                        item['tag'] = self.getTags(item['content'])
                        item['at'] = self.getAts(item['content'])
                        # self.printWeiboInfoItem(item)
                        yield item

                else:  # 转发的微博

                    contents = response.xpath('/html/body/div[@ class="c"][' + str(i) + ']/div[last()]').css(
                        '*::text').extract()
                    content = ''

                    if contents[-2][-2:-1] == '来':
                        contents=contents[0:len(contents)-1]

                    for i in range(1, len(contents) - 9):
                        content = content + contents[i]
                    item['id'] = self.url_2[self.url_5]
                    item['repost'] = repost[0]
                    item['imgNum'] = 0
                    item['likeNum'] = contents[-9][2:len(contents[-9]) - 1]
                    item['repostNum'] = contents[-7][3:len(contents[-7]) - 1]
                    item['commentNum'] = contents[-5][3:len(contents[-5]) - 1]
                    item['time'] = self.getTime(contents[-1])
                    item['content'] = content
                    item['tag'] = self.getTags(item['content'])
                    item['at'] = self.getAts(item['content'])
                    # self.printWeiboInfoItem(item)
                    yield item
            except Exception as e:
                # print(e)
                print(traceback.format_exc())
                pass
            continue
        url = self.getNextUrl()
        if (len(url) != 0):
            yield scrapy.Request(url, callback=self.sub_parse, headers=self.headers,
                                 cookies=self.cookies)




    def getContent(self,response):
        item=response.meta['item']
        contents=response.xpath('/html/body/div[@ id="M_"]/div').css('*::text').extract()
        content=''
        if contents[-11]=='原图':
            if contents[-14][0:2]=='组图':
                for i in range(4, len(contents) - 15):
                    content = content + contents[i]
            else:
                for i in range(4, len(contents) - 13):
                    content = content + contents[i]
        else:
            for i in range(4, len(contents) - 10):
                content = content + contents[i]
        item['content']=content
        item['tag']=self.getTags(item['content'])
        item['at']=self.getAts(item['content'])
        # self.printWeiboInfoItem(item)
        yield item

    def printWeiboInfoItem(self,item):   #打印类，可解开注释使用
        print("大学id： "+item['id'])
        print("转发： " + item['repost'])
        print("内容： " + item['content'])
        print("点赞数： " + item['likeNum'])
        print("转发数： " + item['repostNum'])
        print("评论数： " + item['commentNum'])
        print("发博时间： " + item['time'])
        print(item['tag'])
        print(item['at'])
        print("图片数： "+str(item['imgNum']))

    def getTags(self,content):
        pattern=re.compile(r'\#[^\#]*\#')
        result=pattern.findall(content)
        return result

    def getAts(self,content):
        pattern=re.compile(r'\@[^ ]*')
        result = pattern.findall(content)
        return result

    def getTime(self,mTime):
        # print(mTime)
        result=''
        mTime=mTime.split()
        if mTime[0][-1]=='前':

            m=int(mTime[0][0:len(mTime[0])-3])
            result=(datetime.datetime.now()-datetime.timedelta(minutes=m)).strftime('%Y-%m-%d %H:%M')
            return result

        if mTime[0]=='今天' :
            result=datetime.datetime.now().strftime('%Y-%m-%d')
        elif mTime[0][2:3]=='月':
            result = datetime.datetime.now().strftime('%Y')+'-'+mTime[0][0:2]+'-'+mTime[0][3:5]
        else:
            result=mTime[0]

        result=result+' '+mTime[1][0:5]
        return result

