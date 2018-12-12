#_*_ coding:utf-8 _*_
import time
import datetime
import os
import json
import sys
import string
import requests
import itchat


type = sys.getfilesystemencoding()


reload(sys)
sys.setdefaultencoding('utf-8')

'''图灵key
## 8edce3ce905a4c1dbb965e6b35c3834d
## eb720a8970964f3f855d863d24406576
## 1107d5601866433dba9599fac1bc0083
## 71f28bf79c820df10d39b4074345ef8c
'''
KEY = '8edce3ce905a4c1dbb965e6b35c3834d'


def itchat_SendMsg(nm, msg, second=None):
    try:
        itchat.auto_login(hotReload=True)
        myfriend = itchat.search_friends(name=nm)
        myfriendUserName = myfriend[0]['UserName']
        print  myfriendUserName
        itchat.send(msg, toUserName=myfriendUserName)
        if second != None:
            t = time(second, itchat_SendMsg(nm, msg, second))
            t.start()
    except:
        message = u'It is wrong!!'
        itchat.send(message, toUserName='filehelper')


def GetTuling_response(msg):
    # 这里我们就像在“3. 实现最简单的与图灵机器人的交互”中做的一样
    # 构造了要发送给服务器的数据
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key': KEY,
        'info': msg,
        'userid': 'wechat-robot',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
        return r.get('text')
    # 为了防止服务器没有正常响应导致程序异常退出，这里用try-except捕获了异常
    # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
    except:
        # 将会返回一个None
        return

if __name__ == '__main__':
    itchat_SendMsg('高向阳', 'abc')
    #autoReplay()
    # pass
