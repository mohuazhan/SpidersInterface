# encoding: utf-8

from collections import namedtuple


response = [
    'OK',
    'BAD_REQUEST',
    'UNAUTHORIZED',
    'NOT_FOUND',
    'METHOD_NOT_ALLOWED',
    'INTERNAL_SERVER_ERROR',
]

# response code
_response_code = namedtuple('RESPONSE_CODE', response)
RESPONSE_CODE = _response_code(200, 400, 401, 404, 405, 500)

# response message
_response_msg = namedtuple('RESPONSE_MSG', response)
RESPONSE_MSG = _response_msg(
    'OK',
    'Bad Request',
    'Unauthorized',
    'Not Found',
    'Method Not Allowed',
    'Internal Server Error',
)

# MongoDB Connection
MONGODB_CONNECTTION = {
    'SERVER': "127.0.0.1",
    'PORT': 27017,
    'USER': 'xiaomo',
    'PASSWORD': '19940809',
    'DB': "bak_tornado"
}

# manage all url
DOUYINPC_UID_AWEMELIST = "https://www.iesdouyin.com/web/api/v2/aweme/post/?user_id=%s&sec_uid=&count=21&max_cursor=0&aid=1128&_signature=%s&dytk=%s"