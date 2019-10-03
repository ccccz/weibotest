import scrapy
from weibotest.items import BaseInfoItem
from weibotest.items import WeiboInfoItem
import re

class WeiboSpider(scrapy.Spider):
    name="weibo"
    #url
    url_1="https://weibo.cn/"
    url_2=[    #此处可改为从文件读取
        "nju1902",
        "PKU",
        "ifudan"
    ]
    url_3="?page="
    url_4=0   #搜索页面
    url_5 = 0  #高校顺序url_2

    weiboNum=0  #正在爬取的高校微博页数
    headers={               #头部
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
    meta={
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }
    cookies = {
        '_T_WM': '43586327469',
        'ALF': '1572274973',
        'SCF': 'Ath3LGFZX0FTfy5B1hPlXwqPBhTi85tlI__-vO50T-QtSkkb77xvvhlLiMFtFUfKo3prCgwPLcGnEu3W6QthKkM.',
        'SUB': '_2A25wiwZ4DeRhGeBO61AR9CzOzz6IHXVQd6owrDV6PUJbktAKLU6lkW1NSkS9qS9zsx7tUcYItrkeBHPTKDFnL6Zi',
        'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WWGEzsPZhUmybVP6rA5ve_.5JpX5K-hUgL.Foq7ehz7ShzEShz2dJLoIEBLxK-L12BL1h2LxK-L12BL1h2LxK-L12BL1h2LxKqL1KMLBK-t',
        'SUHB': '04Wu_GeSI9_qSF',
        'SSOLoginState': '1569682984'
    }
    contTemp=''


    def parse(self, response):
        #具体爬取内容，目前只有粉丝数可和关注数，微博内容未写
        #filename = (response.url.split("/")[-1]).split("?")[0]


        if(self.url_4==1):
            name = self.url_2[self.url_5]
            wb=response.xpath("/html/body/div[3]/div/span/text()").extract()
            wb=wb[0][3:len(wb[0])-1]
            fans = response.xpath('/ html / body / div[3] / div / a[2] / text()').extract()
            fans=fans[0][3:len(fans[0])-1]
            follows = response.xpath('/ html / body / div[3] / div / a[1] / text()').extract()
            follows=follows[0][3:len(follows[0])-1]
            self.weiboNum=int(wb)/10
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
            yield scrapy.Request(url, callback=self.sub_parse, headers=self.headers, cookies=self.cookies)


    def start_requests(self):
        #重写了start_requests方法，可以按照自定义顺序爬取界面
        #TODO:暂时修改回调函数，记得改回来self.getNextUrl()
        return [
            scrapy.Request(self.getNextUrl(), callback=self.parse, headers=self.headers, cookies=self.cookies)
        ]

    def getNextUrl(self):
        if(self.url_5<len(self.url_2)):
            url=self.url_1+self.url_2[self.url_5]+self.url_3
            if(self.url_4<self.weiboNum):
                #self.weiboNum
                url=url+str(self.url_4)
                self.url_4=self.url_4+1
            else:
                self.url_5=self.url_5+1
                if(self.url_5==len(self.url_2)):
                    return ''
                self.url_4=0
                url = self.url_1 + self.url_2[self.url_5] + self.url_3
                url = url + str(self.url_4)
                self.url_4 = self.url_4 + 1
            return url
        else:
            return ""

    def sub_parse(self,response):

        for i in range(1,len(response.xpath('/html/body/div[@ class="c"]'))-1):
            item=WeiboInfoItem()
            repost=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[1]/span[1][@ class="cmt"]/a/text()').extract()
            if(len(repost)==0):    #原创微博
                content=''
                contents=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[last()]').css('*::text').extract()
                contents2=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[1]').css('*::text').extract()
                if contents[1]!='原图':
                    imgs=0
                else:
                    if contents2[-2][0:2]=='组图':
                        imgs=contents2[-2][3]
                    else:
                        imgs=1
                item['id']=self.url_2[self.url_5]
                item['repost']=''
                item['tag']=[]
                item['at']=[]
                item['imgNum']=imgs
                item['likeNum']=contents[-9][2:len(contents[-9]) - 1]
                item['repostNum']=contents[-7][3:len(contents[-7]) - 1]
                item['commentNum']=contents[-5][3:len(contents[-5]) - 1]
                item['time']=contents[-1]
                temp=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[1]/span/a[last()]')
                if (temp.xpath('text()').extract())[0]=='全文':  #如果需要访问全文
                    mRequest=scrapy.Request('https://weibo.cn'+(temp.xpath('@href').extract())[0], callback=self.getContent, headers=self.headers, cookies=self.cookies,priority=1)
                    mRequest.meta['item']=item
                    yield mRequest
                else:   #不需要访问全文
                    if len(contents2)>=3:
                        if contents2[-3]=='收藏':
                            for j in range(0, len(contents2) - 11):
                                content = content + contents2[j]
                        else:
                            if contents2[-1] == ']':
                                for j in range(0, len(contents2) - 3):
                                    content = content + contents2[j]
                            else:
                                for j in range(0, len(contents2)):
                                    content = content + contents2[j]
                    elif contents2[-1]==']':
                        for j in range(0,len(contents2)-3):
                            content=content+contents2[j]
                    else:
                        for j in range(0,len(contents2)):
                            content=content+contents2[j]
                    item['content']=content
                    item['tag'] = self.getTags(item['content'])
                    item['at'] = self.getAts(item['content'])
                    self.printWeiboInfoItem(item)
                    yield item

            else:      #转发的微博

                contents=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[last()]').css('*::text').extract()
                content=''

                for i in range(1,len(contents)-9):
                    content=content+contents[i]
                item['id'] = self.url_2[self.url_5]
                item['repost'] = repost[0]
                item['imgNum'] = 0
                item['likeNum'] = contents[-9][2:len(contents[-9]) - 1]
                item['repostNum'] = contents[-7][3:len(contents[-7]) - 1]
                item['commentNum'] = contents[-5][3:len(contents[-5]) - 1]
                item['time'] = contents[-1]
                item['content']=content
                item['tag'] = self.getTags(item['content'])
                item['at'] = self.getAts(item['content'])
                self.printWeiboInfoItem(item)
                yield item
        url = self.getNextUrl()
        if (len(url) != 0):
            if (self.url_4 < self.weiboNum):
                yield scrapy.Request(url, callback=self.sub_parse, headers=self.headers,
                                     cookies=self.cookies)
            else:
                yield scrapy.Request(url, callback=self.parse, headers=self.headers, cookies=self.cookies)



    # self.weiboNum

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
        self.printWeiboInfoItem(item)
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