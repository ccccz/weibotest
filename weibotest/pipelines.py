from weibotest.items import BaseInfoItem
from weibotest.items import WeiboInfoItem
from weibotest.settings import MONGO_HOST
from weibotest.settings import MONGO_PORT
from weibotest.settings import MONGO_DB_NAME
import pymongo

class MongoPipeline(object):

    # 初始化数据库连接信息
    def __init__(self):
        host = MONGO_HOST
        port = MONGO_PORT
        db_name = MONGO_DB_NAME
        client = pymongo.MongoClient(host, port)
        self.db = client[db_name]
        self.base_info = self.db["base_info"]

    # 判断 Item 的类型并存入相应的集合
    def process_item(self, item, spider):
        if isinstance(item, BaseInfoItem):
            self.base_info.insert(dict(item))
        elif isinstance(item, WeiboInfoItem):
            collectionName = str(item['id']) + "_weibo_info"
            self.db[collectionName].insert(dict(item))
        else:
            pass
