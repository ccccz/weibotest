
import scrapy


class BaseInfoItem(scrapy.Item):
    id = scrapy.Field()         # 大学Id
    wb = scrapy.Field()         # 微博数
    fans = scrapy.Field()       # 粉丝数
    follows = scrapy.Field()    # 关注数
    pass


class WeiboInfoItem(scrapy.Item):
    id = scrapy.Field()         # 大学Id
    repost = scrapy.Field()     # 转发者
    content = scrapy.Field()    # 微博内容
    tag = scrapy.Field()        # 微博标签
    at = scrapy.Field()         # @ 的人
    imgNum = scrapy.Field()     # 配图数量
    likeNum = scrapy.Field()    # 点赞数
    repostNum = scrapy.Field()  # 转发数
    commentNum = scrapy.Field() # 评论数
    time = scrapy.Field()       # 发微时间4
    pass


class FollowsInfoItem(scrapy.Item):
    id = scrapy.Field()         # 大学Id
    followsList = scrapy.Field()# 关注列表
    pass