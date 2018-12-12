#coding=utf-8
#脚本功能:统计RF接口数

import os
import sys,time
import datetime

#获取系统默认编码
type = sys.getfilesystemencoding()


reload(sys)
sys.setdefaultencoding('utf-8')


d = datetime.datetime.now()


#返回一个月前的日期时间和时间戳
def month_get(d):
    dayscount = datetime.timedelta(days=d.day)
    dayto = d - dayscount
    #格式化前一个月时间
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, int(d.strftime("%H")),int(d.strftime("%M")),int(d.strftime("%S")))
    #将前一个月时间转换成时间戳
    date_to_format=time.strptime(str(date_to),"%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(date_to_format))
    return date_to


#统计接口总数
def InterFace_Count(path):
    count=0
    for dirpath,dirname,filenames in os.walk(path):
        for file in filenames:
            try :
                sfile=file.split(".")
                if sfile[0]!='__init__' and sfile[1]=='txt':
                    if 'get' in sfile[0].lower() or 'post' in sfile[0].lower():
                        print file
                        count=count+1
            except Exception:
                pass
    return count


#判断文件是否包括指定标签
def CheckTag(path,tag):
    fopen=open(path)
    if tag in fopen.read():
        return True
    return False

#统计最近一个月新增接口数
def InterFace_Count_NearOneMonth(path):
    now=time.strftime("%Y-%m-%d %H:%M:%S")
    # print u"当前日期时间:",now
    near_month_time=month_get(d)
    # print u"一个月前日期时间:",near_month_time
    count=0
    count_a=0
    count_b=0
    count_c=0
    for dirpath,dirname,filenames in os.walk(path):
        for file in filenames:
            path=os.path.join(dirpath,file)
            statinfo=os.stat(path)
            create_time=time.localtime(statinfo.st_ctime)   #创建时间
            create_time=time.strftime("%Y-%m-%d %H:%M:%S",create_time)   #格式化创建时间

            modifty_time=time.localtime(statinfo.st_mtime  )   #修改时间
            modifty_time=time.strftime("%Y-%m-%d %H:%M:%S",modifty_time)   #格式化修改时间

            create_time_l=time.strptime(create_time,"%Y-%m-%d %H:%M:%S")   #格式化至时间戳对象
            modifty_time_l=time.strptime(modifty_time,"%Y-%m-%d %H:%M:%S")   

            #获取一个月前时间的时间戳
            date_to_format=time.strptime(str(near_month_time),"%Y-%m-%d %H:%M:%S")
            timeStamp = float(time.mktime(date_to_format))

            #统计接口总数
            try:
                sfile=file.split(".")
                if sfile[0]!='__init__' and sfile[1]=='txt':
                    if 'get' in sfile[0].lower() or 'post' in sfile[0].lower():
                            print file
                            count=count+1
            except Exception:
                pass

            #过滤出一个月所有新创建的文件，比较创建时间大于一个月内
            try:
                sfile=file.split(".")
                if sfile[0]!='__init__' and sfile[1]=='txt':
                    if 'get' in sfile[0].lower() or 'post' in sfile[0].lower():
                        if float(time.mktime(create_time_l))>= float(time.mktime(date_to_format)):
                            # print file
                            count_a=count_a+1
            except Exception:
                pass

            #过滤出一个月所有新创建且修改过的文件，比较创建时间大于一个月内
            
            try :
                sfile=file.split(".")
                if sfile[0]!='__init__' and sfile[1]=='txt':
                    if 'get' in sfile[0].lower() or 'post' in sfile[0].lower():
                        if float(time.mktime(create_time_l))>= float(time.mktime(date_to_format)) and float(time.mktime(modifty_time_l))>= float(time.mktime(date_to_format)):
                            # print file
                            count_b=count_b+1
            except Exception:
                pass


             #过滤出一个月所有新创建、修改过的文件且包含Online标签的文件，比较创建时间大于一个月内
         
            try :
                sfile=file.split(".")
                if sfile[0]!='__init__' and sfile[1]=='txt':
                    if 'get' in sfile[0].lower() or 'post' in sfile[0].lower():
                           if float(time.mktime(create_time_l))>= float(time.mktime(date_to_format)) and float(time.mktime(modifty_time_l))>= float(time.mktime(date_to_format)) and CheckTag(path,"Online")==bool(True):
                                # print file
                                count_c=count_c+1
            except Exception:
                pass
    return count,count_a,count_b,count_c


if __name__ == '__main__':
    try:
        print u"开始统计...".decode('utf-8').encode(type)
        path=''.join(sys.argv[1:])
        if len(sys.argv[1:])>1:
            path=' '.join(sys.argv[1:])
        # count=InterFace_Count(path)
        count,count_a,count_b,count_c=InterFace_Count_NearOneMonth(path)


        print u"当前目录下，统计RF总的接口数量为: %s 个".decode('utf-8').encode(type)%count
        print u"当前目录下，统计RF一个月内新增接口数量为: %s 个".decode('utf-8').encode(type)%count_a
        print u"当前目录下，统计RF一个月内新增及修改的接口数量为: %s 个".decode('utf-8').encode(type)%count_b
        print u"当前目录下，统计RF一个月内新增修改且包含Online标签接口数量为: %s 个".decode('utf-8').encode(type)%count_c
    except Exception:
        pass
