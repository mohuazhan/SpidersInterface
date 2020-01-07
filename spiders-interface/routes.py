# -*- coding: utf-8 -*-

from handlers.spider_douyin import DouYinPCUidGetAwemeListHandler


# 访问地址
ROUTE_UID_AWEMELIST_DOUYINPC = r'/v1/spider/douyin/uid/awemelist'


# 映射列表
routes = [
    (ROUTE_UID_AWEMELIST_DOUYINPC, DouYinPCUidGetAwemeListHandler),
]
