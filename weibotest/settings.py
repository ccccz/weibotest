
BOT_NAME = 'weibotest'

SPIDER_MODULES = ['weibotest.spiders']
NEWSPIDER_MODULE = 'weibotest.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

COOKIES_ENABLED = True

# MongoDB 相关配置
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB_NAME = 'university_weibo'

# 启用 pipeline
ITEM_PIPELINES = {
   'weibotest.pipelines.MongoPipeline': 300
}
