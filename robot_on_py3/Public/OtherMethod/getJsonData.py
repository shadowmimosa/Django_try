#coding=utf-8

#脚本功能：从返回的内容中提取json串。
#例如:结果返回为 callback({"songerid":123})，提取里面的json串

import re
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')



def getJsonData(response):
        #通过此正则表达式提取出所需的json串
        jsonData=re.findall(r'\w+[(]{1}(.*)[)]{1}',response,re.S)[0]
        jdict=json.loads(jsonData,"gbk")
        return jdict

