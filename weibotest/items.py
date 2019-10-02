# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeibotestItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()  # 大学名称
    wb = scrapy.Field()   #微博数
    fans = scrapy.Field()  # 粉丝数
    follows = scrapy.Field()  # 关注数



    pass
