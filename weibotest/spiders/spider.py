import scrapy

class WeiboSpider(scrapy.Spider):
    name="weibo"
    #url
    url_1="https://weibo.cn/"
    url_2=[    #此处可改为从文件读取
        "nju1902",
        "PKU",
        "ifudan"
    ]
    url_3="?f=search_"
    url_4=1
    url_5 = 0

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


        if(self.url_4==2):
            name = (response.url.split("/")[-1]).split("?")[0]
            wb=response.xpath("/html/body/div[3]/div/span/text()").extract()
            wb=wb[0][3:len(wb[0])-1]
            fans = response.xpath('/ html / body / div[3] / div / a[2] / text()').extract()
            fans=fans[0][3:len(fans[0])-1]
            follows = response.xpath('/ html / body / div[3] / div / a[1] / text()').extract()
            follows=follows[0][3:len(follows[0])-1]
            print(name)
            print("微博数： "+wb)
            print("粉丝数： "+fans)
            print("关注数： "+follows)


        url=self.getNextUrl()
        if(len(url)!=0):
            yield scrapy.Request(url, callback=self.sub_parse(), headers=self.headers, cookies=self.cookies)




    def start_requests(self):
        #重写了start_requests方法，可以按照自定义顺序爬取界面
        #TODO:暂时修改回调函数，记得改回来self.getNextUrl()
        return [
            scrapy.Request("https://weibo.cn/nju1902?page=2", callback=self.sub_parse, headers=self.headers, cookies=self.cookies)
        ]

    def getNextUrl(self):
        #目前是按照顺序爬取前1000条微博页面
        if(self.url_5<=1):
            url=self.url_1+self.url_2[self.url_5]+self.url_3
            if(self.url_4<=1):
                url=url+str(self.url_4)
                self.url_4=self.url_4+1
            else:
                self.url_5=self.url_5+1
                self.url_4=1
                url = self.url_1 + self.url_2[self.url_5] + self.url_3
                url = url + str(self.url_4)
                self.url_4 = self.url_4 + 1
            return url
        else:
            return ""

    def sub_parse(self,response):
        #// *[ @ id = "M_I8AULotHE"]  /html/body/div[8]/div[1]/span[1]
        #字段：repost-转发者，content-内容，tag-标签，at-at的人，imgs-配图数，
        # likeNum-点赞数，repostNum-转发数，commentNum-评论数，time-发博时间
        for i in range(1,len(response.xpath('/html/body/div[@ class="c"]'))-1):

            repost=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[1]/span[1][@ class="cmt"]/a/text()').extract()
            if(len(repost)==0):    #原创微博
                repost=''
                content=''
                contents=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[last()]').css('*::text').extract()
                contents2=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[1]').css('*::text').extract()
                if contents2[-3]=='收藏':
                    imgs=0
                else:
                    if contents2[-2][0:2]=='组图':
                        imgs=contents2[-2][3]
                    else:
                        imgs=1

                temp=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[1]/span/a[last()]')
                #print((temp.xpath('@href').extract())[0])
                if (temp.xpath('text()').extract())[0]=='全文':
                    yield scrapy.Request('https://weibo.cn'+(temp.xpath('@href').extract())[0], callback=self.getContent, headers=self.headers, cookies=self.cookies)

                #print(response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[1]/span/a[last()]/text()').extract())

                    #yield scrapy.Request(, callback=self.getContent, headers=self.headers, cookies=self.cookies)
                    #imgs=contents2[-1]
                   # content = ''
                #else:
                 #   content = ''
                  #  for s in contents2:
                   #     content = content + s
                #print(contents)
                #print(contents2)
                imgs=0
            else:      #转发的微博
                repost=repost[0]
                contents=response.xpath('/html/body/div[@ class="c"]['+str(i)+']/div[last()]').css('*::text').extract()
                content=''
                imgs=0
                for i in range(1,len(contents)-9):
                    content=content+contents[i]
            likeNum=contents[-9][2:len(contents[-9])-1]
            repostNum=contents[-7][3:len(contents[-7])-1]
            commentNum=contents[-5][3:len(contents[-5])-1]
            time=contents[-1]
            print("转发： " + repost)
            print("内容： " + content)
            print("点赞数： "+likeNum)
            print("转发数： "+repostNum)
            print("评论数： "+commentNum)
            print("发博时间： "+time)

            #content=
    def getContent(self,response):
        #print(response.body)
        contents=response.xpath('/html/body/div[@ class="c"][2]/div').css('*::text').extract()
        #for i in range(4,len(contents)-)
        print(contents)