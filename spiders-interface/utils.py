# -*- coding: utf-8 -*-

import re
import subprocess
import time
import json
import hashlib
from fontTools.ttLib import TTFont

# POST请求参数加密
def param_md5(str_encode):
    param = hashlib.md5()
    param.update(str_encode.encode('utf-8'))
    return param.hexdigest()


# 使用google-chrome动态获取抖音pc版的根据uid得到视频列表的url
def get_UserAwemeList_url_dynamic(uid):
    p = subprocess.Popen('\
        google-chrome \
        --headless \
        --disable-gpu \
        --dump-dom \
        --no-sandbox \
        "http://127.0.0.1:20201/douyin-pc/uid-get-aweme.html?uid=%s"' % uid,\
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    time.sleep(1)
    content = p.stdout.readlines()[-3]  # 返回网页的文本
    google_shell = content\
        .replace("amp;","")\
        .replace("</script>","")\
        .replace("\n","")\
        .strip()  # 去除前后的空格
    pattern1 = r'dytk=(.*?)"'
    p1 = re.compile(pattern1)
    dytk = p1.findall(content)[0]
    return {"dytk":dytk, "google_shell":google_shell}

'''
get_cmap_dict(),
get_num_cmap(),
map_cmap_num(get_cmap_dict,get_num_cmap),
replace_num_and_cmap(result,response)
以上函数用于破解抖音pc版字体加密
'''
ttfond = TTFont("./others/iconfont_9eb9a50.woff")
def get_cmap_dict():
    """
    :return: 关系映射表
    """
    # 从本地读取关系映射表【从网站下载的woff字体文件】
    best_cmap = ttfond["cmap"].getBestCmap()
    # 循环关系映射表将数字替换成16进制
    best_cmap_dict = {}
    for key,value in best_cmap.items():
        best_cmap_dict[hex(key)] = value
    return best_cmap_dict

def get_num_cmap():
    """
    :return: 返回num和真正的数字映射关系
    """
    num_map = {
        "x":"", "num_":1, "num_1":0,
        "num_2":3, "num_3":2, "num_4":4,
        "num_5":5, "num_6":6, "num_7":9,
        "num_8":7, "num_9":8,
    }
    return num_map

def map_cmap_num(get_cmap_dict,get_num_cmap):
    new_cmap = {}
    for key,value in get_cmap_dict().items():
        key = re.sub("0","&#",key,count=1) + ";"    # 源代码中的格式 &#xe606;
        new_cmap[key] = get_num_cmap()[value]
        # 替换后的格式
        # '&#xe602;': 1, '&#xe603;': 0, '&#xe604;': 3, '&#xe605;': 2,
    return new_cmap

def replace_num_and_cmap(result,response):
    """
    将网页源代码中的&#xe603;替换成数字
    """
    for key,value in result.items():
        if key in response:
            # print(777)
            response = re.sub(key, str(value), response)
    return response

new_cmap = map_cmap_num(get_cmap_dict, get_num_cmap)
# 破解字体加密使用方法(respon为网页请求返回的text文本)
# respon = replace_num_and_cmap(new_cmap,respon)

