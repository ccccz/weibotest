
BOT_NAME = 'weibotest'

SPIDER_MODULES = ['weibotest.spiders']
NEWSPIDER_MODULE = 'weibotest.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

COOKIES_ENABLED = True

# MongoDB 相关配置
MONGO_HOST = '94.191.110.118'
# MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB_NAME = 'university_weibo'
COOKIES_COLLECTION_NAME = 'cookies_pool'
SCHOOL_BASE_INFO = 'base_info'
SCHOOL_FOLLOWS_INFO = 'follows_info'

# 启用 pipeline
ITEM_PIPELINES = {
    'weibotest.pipelines.MongoPipeline': 300
}

# 启用 Middleware
DOWNLOADER_MIDDLEWARES = {
    'weibotest.middlewares.WeiboCookiesMiddleware': 500
}

# User-Agent 池
USER_AGENT_POOL = [
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
]

# 模拟登陆相关配置
WB_LOGIN_URL = 'https://passport.weibo.cn/sso/login'
WB_USER_POOL = [
    {
        'username': 'qaswazxs@126.com',
        'password': '19991004'
    }
]
WB_LOGIN_FORM = {
    'username': '',
    'password': '',
    'savestate': '1',
    'r': 'https://weibo.cn/',
    'ec': '0',
    'pagerefer': 'https://weibo.cn/pub/?vt=',
    'entry': 'mweibo',
    'wentry': '',
    'loginfrom': '',
    'client_id': '',
    'code': '',
    'qq': '',
    'mainpageflag': '1',
    'hff': '',
    'hfp': ''
}
WB_LOGIN_HEADERS = {
    'Origin': 'https://passport.weibo.cn',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https%3A%2F%2Fweibo.cn%2F%3Fluicode%3D10000011%26lfid%3D100103type%253D1%2526q%253D%25E5%258D%2597%25E4%25BA%25AC%25E5%25A4%25A7%25E5%25AD%25A6&backTitle=%CE%A2%B2%A9&vt='
}


