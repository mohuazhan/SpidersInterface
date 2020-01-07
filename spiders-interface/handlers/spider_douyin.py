# -*- coding: utf-8 -*-

import re
import subprocess
import time
import json
from lxml import etree
import logging
import pymongo
import tornado.gen
from tornado.concurrent import run_on_executor

from utils import param_md5,get_UserAwemeList_url_dynamic
from consts import RESPONSE_CODE, MONGODB_CONNECTTION
from handlers.common import CommonHandler

logger = logging.getLogger(__name__)

# 连接MongoDB
mongo_client = pymongo.MongoClient(
    MONGODB_CONNECTTION['SERVER'],
    MONGODB_CONNECTTION['PORT']
)
mongo_database = mongo_client.admin  # 连接用户库
mongo_database.authenticate(
    MONGODB_CONNECTTION['USER'],
    MONGODB_CONNECTTION['PASSWORD']
)  # 用户认证
mongo_database = mongo_client[MONGODB_CONNECTTION['DB']]  # 连接数据库


class DouYinPCUidGetAwemeListHandler(CommonHandler):
    '''
    处理抖音用户ID请求视频列表(/v1/spider/douyin/uid/awemelist)的Handler
    handle_args：校验传入参数
    '''

    def __init__(self, *args, **kwargs):
        super(DouYinPCUidGetAwemeListHandler, self).__init__(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        super(DouYinPCUidGetAwemeListHandler, self).initialize(*args, **kwargs)

    def handle_args(self):
        request_data = json.loads(self.request.body)
        method = request_data['method']
        uid = request_data['uid']
        token = request_data['token']
        re_token = param_md5(method + uid + 'boookekj')
        if re_token == token:
            return uid
        else:
            raise ValueError(u'不正常访问token')

    @run_on_executor
    def spider_douyin_awemelist(self, uid):
        mongo_collection = mongo_database['original_uid_awemelist']  # 连接数据表
        try:
            retry_count = 0
            while True:
                google_json = get_UserAwemeList_url_dynamic(uid)
                if google_json['dytk'] != '':
                    break
                retry_count += 1
                if retry_count > 3:
                    result = {
                        "url":None,
                        "respon":None,
                        "success_times":0,
                        "msg":"Too many failures!Please try it again!",
                        "status":500,  # 服务器遇到错误，无法完成请求
                        "now":time.time()
                    }
                    mongo_collection.insert(dict(result))
                    return result
                time.sleep(1)
            original_url = re.findall(
                '--no-sandbox "(.*?)"',
                google_json['google_shell']
            )[0]
            res_list = []
            while True:
                respon = subprocess.Popen(
                    google_json['google_shell'],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                res = str(respon.stdout.read()).decode('utf-8')
                html = etree.HTML(res)
                res_text = html.xpath('//body/pre/text()')
                res_json = json.loads(res_text[0])
                res_list.append(res_json)
                if res_json['aweme_list'] == []:
                    result = {
                        "url":url,
                        "respon":res_list,
                        "success_times":len(res_list),
                        "msg":"An empty aweme list appears here!Please try it again!",
                        "status":206,  # 服务器成功处理了部分 GET 请求
                        "now":time.time()
                    }
                    mongo_collection.insert(dict(result))
                    return result
                if res_json['has_more'] == True:
                    max_cursor = res_json['max_cursor']
                    google_json['google_shell'] = re.sub(
                        'max_cursor=(.*?)&aid',
                        'max_cursor=%s&aid' % str(max_cursor),
                        google_json['google_shell']
                    )  # 正则替换max_cursor
                if res_json['has_more'] == False:
                    break
                time.sleep(1)
            result = {
                "url":original_url,
                "respon":res_list,
                "success_times":len(res_list),
                "msg":"success",
                "status":200,
                "now":time.time()
            }
            mongo_collection.insert(dict(result))
            return result
        except:
            return []

    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        try:
            uid = self.handle_args()
        except ValueError as e:
            logger.exception(e)
            self.set_status(RESPONSE_CODE.BAD_REQUEST)
            response = e.message
            self.write(response)
            self.finish()
            return

        try:
            result = yield self.spider_douyin_awemelist(uid)
        except ValueError as e:
            logger.exception(e)
            self.set_status(RESPONSE_CODE.INTERNAL_SERVER_ERROR)
            response = e.message
            self.write(json.dumps(response))
            self.finish()
            return

        self.set_status(RESPONSE_CODE.OK)
        response = result
        self.write(json.dumps(response))
        self.finish()