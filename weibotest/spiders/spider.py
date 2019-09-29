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


    def parse(self, response):
        #具体爬取内容，目前只有粉丝数可和关注数，微博内容未写
        filename = (response.url.split("/")[-1]).split("?")[0]


        if(self.url_4==2):
            name = filename
            fans = response.xpath('/ html / body / div[3] / div / a[2] / text()').extract()
            fans=fans[0][3:len(fans[0])-1]
            follows = response.xpath('/ html / body / div[3] / div / a[1] / text()').extract()
            follows=follows[0][3:len(follows[0])-1]
            print(name)
            print("粉丝数： "+fans)
            print("关注数： "+follows)


        url=self.getNextUrl()
        if(len(url)!=0):
            yield scrapy.Request(url, callback=self.parse, headers=self.headers, cookies=self.cookies)




    def start_requests(self):
        #重写了start_requests方法，可以按照自定义顺序爬取界面

        return [
            scrapy.Request(self.getNextUrl(), callback=self.parse, headers=self.headers, cookies=self.cookies)
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