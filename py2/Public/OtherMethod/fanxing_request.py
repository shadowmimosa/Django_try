#coding=utf-8

#脚本功能：抓取繁星网，推荐艺人列表，并保存到外部文件中

import sys
import requests
import json
import re
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf-8')



class spider(object):
    def __init__(self):
        print "开始对【---%s---】页面进行爬虫"%(html_title[0])


    def getHtml(self,url):
        html=requests.get(url)
        return html.text

    def getJsonData(self,response):
        #通过此正则表达式提取出所需的json串
        jsonData=re.findall(r'\w+[(]{1}(.*)[)]{1}',response,re.S)[0]
        jdict=json.loads(jsonData,"gbk")
        data=jdict['data']
        return data

    def getInfo(self,data):
        info={}
        info['userId']=data['userId']
        info['nickName']=data['nickName']
        info['roomId']=data['roomId']
        info['viewerNum']=data['viewerNum']
        info['startTime']=data['startTime']
        return info

    def saveinfo(self,classinfo,count):
        f=open('info.txt','w')
        f.writelines("当前获取到的推荐艺人数为:"+str(count)+'\n\n')
        for info in classinfo:
            f.writelines('用户ID: ' + info['userId'] + '\n')
            f.writelines('用户昵称: ' + info['nickName'] + '\n')
            f.writelines('房间ID: ' + info['roomId'] + '\n')
            f.writelines('开播时间: ' + str(info['startTime']) + '\n')

            f.writelines('观众数: ' + str(info['viewerNum']) + '\n\n')




if __name__ == '__main__':
    classinfo=[]
    url='http://visitor.fanxing.kugou.com/VServices/IndexService.IndexService.getHotStarList/'
    url_home='http://fanxing.kugou.com/'

    html=requests.get(url_home)
    selector = etree.HTML(html.text)
    html_title = selector.xpath("//title/text()")

    recommendText=selector.xpath("//*[@id='tab_belove']/li[1]/a/i/text()")



    fxspider = spider()
    print u"获取:【---%s---】艺人 "%recommendText[0]
    print u"开始处理页面: "+url
    content=fxspider.getHtml(url)
    data=fxspider.getJsonData(content)
    data_len=len(data)
    for i in xrange(data_len):
        info=fxspider.getInfo(data[i])
        classinfo.append(info)
    fxspider.saveinfo(classinfo,data_len)

    print "获取【%s】艺人数为:【%s】"%(recommendText[0],data_len)
    print u"爬虫结束!"



