
import requests
import json
import pymongo
import logging
from weibotest.settings import MONGO_HOST
from weibotest.settings import MONGO_PORT
from weibotest.settings import MONGO_DB_NAME
from weibotest.settings import COOKIES_COLLECTION_NAME
from weibotest.settings import WB_LOGIN_URL
from weibotest.settings import WB_LOGIN_FORM
from weibotest.settings import WB_LOGIN_HEADERS
from weibotest.settings import WB_USER_POOL


logger = logging.getLogger("----COOKIES POOL----")
client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB_NAME]
col = db[COOKIES_COLLECTION_NAME]


def get_cookies(username, password):
    payload = WB_LOGIN_FORM
    payload['username'] = username
    payload['password'] = password
    response = requests.post(WB_LOGIN_URL, data=payload, headers=WB_LOGIN_HEADERS)
    cookies = response.cookies.get_dict()
    logger.warning("获取 " + username + " Cookies 成功!")
    logger.warning(json.dumps(cookies))
    return json.dumps(cookies)


def init_cookies():
    for user in WB_USER_POOL:
        cookies = get_cookies(user['username'], user['password'])
        col.insert({
            'username': user['username'],
            'cookies': cookies
        })
