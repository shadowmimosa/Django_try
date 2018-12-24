#coding=utf-8
'''
基于monkey开发的Android随机测试工具
'''
import re
import sys
import os
#import java
import time,traceback
import platform
import subprocess
import random
from collections import Counter
import threading
import shutil
import hashlib
import commands

import logging
import signal

reload(sys)
sys.setdefaultencoding('UTF-8')

print 'monkey_lib.py   start  -->'
#导入异常,则在线安装

try:
    import xlsxwriter
except ImportError:
    os.popen('start pip install -i http://pypi.douban.com/simple/ XlsxWriter==0.9.3')
try:
    import yaml
except ImportError:
    print "start install yaml"
    os.popen('start pip install -i https://pypi.douban.com/simple/ yaml')


# 配置日志信息
logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(funcName)s [line:%(lineno)d] %(levelname)s %(process)d  %(threadName)s [%(message)s]",
                        filename=os.path.join(os.path.dirname(__file__),"monkey_lib.log"),
                        datefmt="%a,%d %b %Y %H:%M:%S",
                        filemode='w+')
# # 定义一个Handler打印INFO及以上级别的日志到sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# # 设置日志打印格式
formatter = logging.Formatter('%(asctime)s %(funcName)s [line:%(lineno)d] %(levelname)s %(process)d  %(threadName)s [%(message)s]')
console.setFormatter(formatter)
# # 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)


#判断系统类型，windows使用findstr，linux使用grep
system = platform.system()
if system is "Windows":
    find_util = "findstr"
    awk_util='gawk'
    str_encode='GB2312'  #gbk   GB2312

else:
    find_util = "grep"
    awk_util='awk'
    str_encode='utf-8'
WhiteUrllist = list()  #存放不存在text类型黑名单的activity
logging.info('find_util=={},awk_util=={},str_encode=={}'.format(find_util,awk_util,str_encode))
logging.info('WhiteUrllist={}'.format(str(WhiteUrllist)))

def  getdevices(ord=None):
    deviceidlist = list()
    if system is  "Windows":
        getdevicescmd= "adb devices |findstr  device$"
    else:
        getdevicescmd= "adb devices |grep  device$"
    logging.info("getdevicecmd=={}".format(getdevicescmd))
    try:
        f=os.popen(getdevicescmd)
        fs=f.read()
        fslist=fs.split()
        fslen=len(fslist)
        logging.info("fslen=={}".format(fslen))
        if ord is None:
            index=0
        elif ord>0 and 2 * ord>=fslen:
            index=fslen-2
        elif ord>0 and 2 * ord<fslen:
            index=2 * ord-2
        elif ord<0 and 2 * ord+fslen>=0:
            index=2 * ord
        else:
            index=0
        if ord!=0:
            deviceid=fslist[index]
            logging.info('return deviceid; ord is[{}],deviceid is {}'.format(index,deviceid))
            return deviceid
        else:
            for  k in range(0,fslen,2):
                deviceid=fslist[k]
                deviceidlist.append(deviceid)
                logging.info('return List; list[{}],deviceid is {}'.format(k/2,deviceid))
            return  deviceidlist
        #(cmdstatus,cmdout)= commands.getoutput(getdevicescmd)
        #logging.info('cmdstatus=={},cmdout=={}'.format(cmdstatus,cmdout))
    except Exception as e:
        logging.info(e)



#返回一个随机整数，用作-s随机数生成器
def get_digit():
    num=random.randint(1,10000)
    return num

#调用monkeyrunner指定开始启动activity
def startAppActivity(device_name,componentName=None):
    '''
    #os.popen("monkeyrunner")
    monkeyrunnercmd= 'D:\\AndroidSDK\\tools\\monkeyrunner.bat'
    #monkeyrunnercmd = 'e:\\111.bat'
    stdinlist=list()
    d = subprocess.Popen(monkeyrunnercmd, shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #stdinlist.append(monkeyrunnercmd)
    stdinlist.append('from com.android.monkeyrunner import MonkeyRunner as mr ')
    stdinlist.append('from com.android.monkeyrunner import MonkeyDevice as md ')
    stdinlist.append('from com.android.monkeyrunner import MonkeyImage as mi ')
    stdinlist.append('from com.android.monkeyrunner.easy import EasyMonkeyDevice ')
    stdinlist.append('from com.android.monkeyrunner.easy import By ')
    stdinlist.append('print  1234')
    stdinlist.append('device = mr.waitForConnection(5,device_name)')
    stdinlist.append("componentName='co.runner.app/co.runner.app.home_v4.activity.HomeActivityV4'")
    stdinlist.append('device.startActivity(component=componentName)')
    logging.info('stdinlist={}'.format(str(stdinlist)))
    try:
        #logging.info(cmd)
        logging.info("11111")
        #d = subprocess.Popen(stdinlist, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 #stderr=subprocess.PIPE)
        logging.info("11222")
        #d.stdin.write(cmd)
        #logging.info('input={}->{},out={},err={}'.format(cmd,d.stdin.read(),d.stdout.read(),d.stderr.read()))
        out,err = d.communicate()
        logging.info("22222")
        logging.info(out)
        logging.info('err={}'.format(str(err)))
        logging.info("33333")
    except Exception as e:
        logging.info(e)
    '''
    try:
        for p in os.environ['PYTHONPATH'].split(';'):
            logging.info(p)
            if not p in sys.path:
                sys.path.append(p)
                logging.info(p)
    except Exception as e1:
        logging.info(e1)
    try:
        sys.path.append(os.path.join(os.environ['ANDROID'].split(';')))
        logging.info(str(sys.path))
    except Exception as e2:
        logging.info(e2)
    try:
        from com.android.monkeyrunner import MonkeyRunner as mr
        from com.android.monkeyrunner import MonkeyDevice as md
        from com.android.monkeyrunner import MonkeyImage as mi
        from com.android.monkeyrunner.easy import EasyMonkeyDevice  #提供了根据ID进行访问
        from com.android.monkeyrunner.easy import By    #根据ID返回PyObject的方法
    except Exception as e:
        logging.info(e)
    #connect device 连接设备
    #第一个参数为等待连接设备时间
    #第二个参数为具体连接的设备
    print "waitting devices connecting..."
    device = mr.waitForConnection(5,device_name)    #指定设备连接，超时时间为5秒

    print "devices connecting success..."

    if not device:
        print >> sys.stderr,"fail"
        sys.exit(1)

    #定义要启动的Activity
	if componentName is None:
		componentName="co.runner.app/co.runner.app.home_v4.activity.HomeActivityV4"
	else:
		componentName=componentName

    #启动特定的Activity
    device.startActivity(component=componentName)
    time.sleep(3)
    print "delay 3 sec"


#启用应用程序
def startAppActivity_ADB(device_name,StartActivity):
    app=StartActivity.split('/')[0]
    cmd='adb -s {} shell am start -n {}'.format(device_name,StartActivity)
    logging.info('Start Activity cmd is 【{}】;App is {}'.format(cmd,app).encode(str_encode))
    try:
        logging.info('用adb命令:{}启动:{}...'.format(cmd,app).encode(str_encode))
        startApp=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = startApp.communicate()
        activity_top_current=get_device_currentActivity(device_name,app)
        logging.info('activityTopCurrent is [{}]'.format(activity_top_current))
        app=activity_top_current.split('/')[0]
        appativity=activity_top_current.split('/')[-1]
        logging.info('app is {},activity is {}'.format(app,appativity))
        if app==packapgename:
            logging.info('StartActivity Success!!! ==> {}'.format(StartActivity))
            return
        else:
            logging.info('StartActivity error!')
            logging.info('应用程序:{}不存在，请检查安装!'.format(StartActivity).encode(str_encode))
            if system is 'Windows':
                os.popen('taskkill /f /pid {}'.format(os.getpid()))
                sys.exit()
            else:
                os.popen('kill -9 {}'.format(os.getpid()))
                sys.exit()
    except Exception as e:
        logging.info(e)


#启动APP后，通过引导的方式，在执行monkey随机测试前，自动进入指定菜单下
def startAppSelectList(device_name,selectList):
    selectList_list=[]
    if isinstance(selectList,list):
        logging.info('selectList 引导列表符合要求!'.encode(str_encode))
    else:
        logging.info('selectList 引导列表不符合入参要求!'.encode(str_encode))
        selectList=list(selectList)

    selectList_len=len(selectList)
    if selectList_len==0:
        logging.info('未指定引导selectList列表，默认从主Actvitiy执行遍历!'.encode(str_encode))
    elif selectList_len>0:
        logging.info('先进入指定的selectList引导菜单下，再执行monkey随机测试!'.encode(str_encode))
        if "'" in str(selectList):
            selectList=str(selectList).replace("'","")
        if isinstance(selectList,str):
            selectList=eval(selectList)

        for point in selectList:
            if not isinstance(point,tuple):
                point=eval(point)
            selectList_list.append(point)

    for index in xrange(len(selectList_list)):
        os.popen("adb -s {device_name} shell input tap {x} {y}".format(device_name=device_name,x=selectList_list[index][0],y=selectList_list[index][-1]))
        logging.info('进入第{}级引导菜单，对应坐标位置为:{} {}'.format(index+1,selectList_list[index][0],selectList_list[index][-1]).encode(str_encode))
        time.sleep(2)

    logging.info('引导完成'.encode(str_encode))
    time.sleep(3)


#开启jsonrpc服务，用于uiautomator命令通讯
def start_uiautomator_jsonrpc_server(device_name):
    if system is 'Windows':
        if os.path.exists(os.path.join(os.path.join(os.path.dirname(__file__),'jar'),'bundle.jar')) and os.path.exists(os.path.join(os.path.join(os.path.dirname(__file__),'jar'),'uiautomator-stub.jar')):
            logging.info(os.path.join(os.path.join(os.path.dirname(__file__),'jar'),'bundle.jar'))
            logging.info(os.path.join(os.path.join(os.path.dirname(__file__),'jar'),'uiautomator-stub.jar'))
            cmd='adb -s {0} push {1} /data/local/tmp/'.format(device_name,os.path.join(os.path.join(os.path.dirname(__file__),'jar'),'bundle.jar'))
            cmd1='adb -s {0} push {1} /data/local/tmp/'.format(device_name,os.path.join(os.path.join(os.path.dirname(__file__),'jar'),'uiautomator-stub.jar'))
            p = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.communicate()
            if p.returncode==0:
                logging.info(' push bundle.jar==>success')

            p1 = subprocess.Popen(cmd1, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p1.communicate()
            if p1.returncode==0:
                logging.info(' push uiautomator-stub.jar==>success')

            logging.info('Start jsonrpc server via command')
            cmd_server='adb -s {} shell uiautomator runtest bundle.jar uiautomator-stub.jar -c com.github.uiautomatorstub.Stub'.format(device_name)
            jsread=os.popen(cmd_server).read()
            logging.info('start info is {}'.format(jsread))
            if 'carrierweekinfo-conf' in jsread:
                resx=1
                logging.info('######restart uiautomator server!!!######')
                if  resx>5:
                    jsread = os.popen(cmd_server).read()
                    logging.info('######restart ##{}## uiautomator server!!!######'.format(resx))


#新开线程，用于后台启动jsonrpc服务
def thread_start_jsonrpc_server(device_name):
    t=threading.Thread(target=start_uiautomator_jsonrpc_server,args=(device_name,))
    t.setDaemon(True)
    t.start()
    logging.info('启动jsonrpc服务线程，线程名:【{}】'.format(t.getName()).encode(str_encode))
    t.join(3)
    logging.info('jsonrpc服务线程等待3秒，继续向下执行...'.encode(str_encode))

def uiautomator_Guide(d,device_name,selectElements):
    logging.info('打印当前手机界面基本信息:{}'.format(d.info).encode(str_encode))
    if isinstance(selectElements,list):
        logging.info('selectElements 指定引导控制列表集合符合列表类型!'.encode(str_encode))
    else:
        logging.info('selectElements 指定引导控制列表不符合入参要求!'.encode(str_encode))
    elements_len=len(selectElements)
    if elements_len==0:
        logging.info('未指定selectElements引导列表，默认从主Actvitiy执行遍历!'.encode(str_encode))
    elif elements_len>0:
        logging.info('先进入指定的selectElements引导列表，再执行monkey随机测试!'.encode(str_encode))

        for index in xrange(elements_len):
            try:
                type=selectElements[index].split("=")[0]
                logging.info('第{}个elements的type为：{}'.format(index+1,type).encode(str_encode))
                element=selectElements[index].split("=")[-1]
                logging.info('第{}个elements的values为：{}'.format(index+1,element).encode(str_encode))
                rid=d(resourceId="{}".format(element)).wait.exists(timeout=5)
                tid=d(text="{}".format(element)).wait.exists(timeout=5)
                logging.info('第{}个resourceId的values为：{}'.format(index+1,rid).encode(str_encode))
                logging.info('第{}个tid的values为：{}'.format(index+1,tid).encode(str_encode))
                if type=='text':
                    if d(text="{}".format(element)).wait.exists(timeout=5):
                        d(text="{}".format(element)).click()
                        logging.info("进入第{}级引导菜单，对应元素控件为==>:{}".format(index+1,selectElements[index]).encode(str_encode))
                        time.sleep(1)
                    else:
                        time.sleep(1)
                        logging.info("{} ==>当前页面，未检查到该元素".format(selectElements[index]).encode(str_encode))
                        #break
                elif type=='resourceId':
                    if d(resourceId="{}".format(element)).wait.exists(timeout=3):
                        d(resourceId="{}".format(element)).click()
                        logging.info("进入第{}级引导菜单，对应元素控件为==>:{}".format(index+1,selectElements[index]).encode(str_encode))
                        time.sleep(1)
                    else:
                        time.sleep(1)
                        logging.info("{} ==>当前页面，未检查到该元素".format(selectElements[index]).encode(str_encode))
                        #break
            except Exception as e:
                logging.info('执行引导元素时，捕获到异常==>{}'.encode(str_encode).format(e))

#基于uiautomator框架控件识别引导方法
def start_uiautomator(device_name,selectElements):
    try:
        from uiautomator import Device
        logging.info('当前环境已安装uiautomator!'.encode(str_encode))

    except ImportError:
        logging.info('当前环境未安装uiautomator,开始自动安装...'.encode(str_encode))
        os.popen('start pip install -i http://pypi.douban.com/simple/ uiautomator')

    thread_start_jsonrpc_server(device_name)

    try:
        d = Device(device_name)
    except Exception as e:
        logging.info('uiautomator框架初始化失败，错误信息为:{}'.format(e).encode(str_encode))
    else:
        logging.info('打印当前手机界面基本信息:{}'.format(d.info).encode(str_encode))
    if isinstance(selectElements,list):
        logging.info('selectElements 指定引导控制列表集合符合列表类型!'.encode(str_encode))
    else:
        logging.info('selectElements 指定引导控制列表不符合入参要求!'.encode(str_encode))
    elements_len=len(selectElements)
    if elements_len==0:
        logging.info('未指定selectElements引导列表，默认从主Actvitiy执行遍历!'.encode(str_encode))
    elif elements_len>0:
        logging.info('先进入指定的selectElements引导列表，再执行monkey随机测试!'.encode(str_encode))

        for index in xrange(elements_len):
            try:
                type=selectElements[index].split("=")[0]
                logging.info('第{}个elements的type为：{}'.format(index+1,type).encode(str_encode))
                element=selectElements[index].split("=")[-1]
                logging.info('第{}个elements的values为：{}'.format(index+1,element).encode(str_encode))
                rid=d(resourceId="{}".format(element)).wait.exists(timeout=5)
                tid=d(text="{}".format(element)).wait.exists(timeout=5)
                logging.info('第{}个resourceId的values为：{}'.format(index+1,rid).encode(str_encode))
                logging.info('第{}个tid的values为：{}'.format(index+1,tid).encode(str_encode))
                if type=='text':
                    if d(text="{}".format(element)).wait.exists(timeout=5):
                        d(text="{}".format(element)).click()
                        logging.info("进入第{}级引导菜单，对应元素控件为==>:{}".format(index+1,selectElements[index]).encode(str_encode))
                        time.sleep(2)
                    else:
                        time.sleep(2)
                        logging.info("{} ==>当前页面，未检查到该元素".format(selectElements[index]).encode(str_encode))
                elif type=='resourceId':
                    if d(resourceId="{}".format(element)).wait.exists(timeout=3):
                        d(resourceId="{}".format(element)).click()
                        logging.info("进入第{}级引导菜单，对应元素控件为==>:{}".format(index+1,selectElements[index]).encode(str_encode))
                        time.sleep(2)
                    else:
                        time.sleep(2)
                        logging.info("{} ==>当前页面，未检查到该元素".format(selectElements[index]).encode(str_encode))
            except Exception as e:
                logging.info('执行引导元素时，捕获到异常==>{}'.encode(str_encode).format(e))

    # d(text="发现").click()
    # d(text="音乐现场").click()
    # d(text="账号登录").click()    #text完全匹配
    # d(textContains="账号").click()  #textContains文本包含
    # d(textMatches='.*号.*').click()   #正则匹配
    # d.press("back")   #返回
    # d.open.quick_settings()   #打开设置界面
    # d(resourceId="com.kugou.fanxing:id/input_edt").clear_text() #清空用户名
    # d(resourceId="com.kugou.fanxing:id/input_edt").set_text("testfx01")  #输入用户名
    # d(resourceId="com.kugou.fanxing:id/input_edt")[1].set_text("67889911")  #输入密码，由于密码资源id与用户名资源id是一样，但为第二个
    # d(textMatches='登录').click()


#黑名单功能
def backListActivity(device_name,packapgname,blackUrlList,blackList,homeActivity=None,selectElements=None):
    try:
        from uiautomator import Device
        logging.info('当前环境已安装uiautomator!'.encode(str_encode))

    except ImportError:
        logging.info('当前环境未安装uiautomator,开始自动安装...'.encode(str_encode))
        os.popen('start pip install -i http://pypi.douban.com/simple/ uiautomator')

    thread_start_jsonrpc_server(device_name)   #启动jsonrpc服务

    try:
        d = Device(device_name)
    except Exception as e:
        logging.info('uiautomator框架初始化失败，错误信息为:{}'.format(e).encode(str_encode))

    blackUrlList_len = len(blackUrlList)
    blackList_len = len(blackList)
    while blackUrlList_len+blackList_len>0:
        #time.sleep(2)
        current_activity=get_device_currentActivity(device_name,packapgname)
        #if blackList_len>0:
        if blackUrlList_len<=0:
            logging.info('未指定blackUrlList，不过滤activity!'.encode(str_encode))
            pass
        else:
            #处理URL黑名单
            if current_activity in blackUrlList:
                logging.info('当前界面{}==>存在黑名单blackList列表中'.encode(str_encode).format(current_activity))
                logging.info('按back按健返回'.encode(str_encode))
                d.press.back()
                logging.info('点击【"back"】'.encode(str_encode))
                d.press("back")
                logging.info('返回上一页面完成'.encode(str_encode))
                current_activity=get_device_currentActivity(device_name,packapgname)
                logging.info('获取当前页面为###{}###'.format(current_activity).encode(str_encode))
                if current_activity not in blackUrlList:
                    logging.info('当前界面不在黑名单中，返回成功!'.encode(str_encode))
                elif homeActivity in current_activity:
                    logging.info('current_activity=homeActivity={}'.format(homeActivity))
                    uiautomator_Guide(d, device_name, selectElements)
                else:
                    logging.info('返回失败，重新进行入口测试!'.encode(str_encode))
                    #startAppActivity(device_name)
                    rescmd = 'adb -s {} shell am start -R 1 {} '.format(device_name, homeActivity)
                    #monkeypid = get_findstr_pid(device_name)
                    #logging.info('关闭monkey进程'.encode(str_encode))
                    #adb_logcat_stop(device_name, monkeypid)
                    logging.info('使用命令:[{}]重新开始'.format(rescmd).encode(str_encode))
                    os.popen(rescmd)
                    uiautomator_Guide(d, device_name, selectElements)
            else:
                logging.info('当前界面{}不在黑名单blackUrlList列表中'.format(current_activity).encode(str_encode))
                if blackList_len<=0:
                    logging.info('未指定blackList，不过滤text文本!'.encode(str_encode))
                    pass
                elif  current_activity in WhiteUrllist:
                    logging.info(('当前界面{}在WhiteUrllist中!'.format(current_activity).encode(str_encode)))
                else:
                    k = 0
                    for els in blackList:
                        if d(text="{}".format(els)).exists:
                            logging.info('当前界面含有文本元素:{}==>存在黑名单列表中'.encode(str_encode).format(els))
                            blackUrlList.append(current_activity)
                            logging.info('将当前界面{}加入blackUrlList列表中'.format(current_activity).encode(str_encode))
                            logging.info('按back按健返回'.encode(str_encode))
                            d.press.back()
                            logging.info('点击【"back"】'.encode(str_encode))
                            d.press("back")
                            logging.info('返回上一页面完成'.encode(str_encode))
                            if not d(text="{}".format(els)).exists:
                                logging.info('检查到黑名单文本，返回成功!'.encode(str_encode))
                                break
                            else:
                                logging.info('返回失败，重新进行入口测试!'.encode(str_encode))
                                #startAppActivity(device_name)
                                rescmd = 'adb -s {} shell am start -R 1 {}'.format(device_name,homeActivity)
                                #monkeypid = get_findstr_pid(device_name)
                                #logging.info('关闭monkey进程'.encode(str_encode))
                                #adb_logcat_stop(device_name, monkeypid)
                                logging.info('使用命令:[{}]重新开始'.format(rescmd).encode(str_encode))
                                os.popen(rescmd)
                                uiautomator_Guide(d, device_name, selectElements)
                        else:
                            k = k + 1
                            #logging.info('当前界面{},不存黑名单中在##text={}#k={}#的控件对象'.format(current_activity,els,k).encode(str_encode))
                            if k>=blackList_len:
                                WhiteUrllist.append(current_activity)
                                logging.info('当前界面{},不存黑名单中在##text={}#k={}#的控件对象'.format(current_activity, els, k).encode(str_encode))
                                logging.info('WhiteUrllist=={}'.format(WhiteUrllist))
                            pass


#新开线程，用于后台监控黑名单列表
def thread_blackListActivity(device_name,packapgname,blackUrlList,blackList,homeActivity=None,selectElements=None):
    t=threading.Thread(target=backListActivity,args=(device_name,packapgname,blackUrlList,blackList,homeActivity,selectElements))
    t.setDaemon(True)
    t.start()
    t.join(3)
    logging.info('线程名：【{}】 开始进行黑名单activity监控...'.format(t.getName()).encode(str_encode))


#获取手机分辨率
def get_device_pix(device_name):
    result = os.popen("adb -s {} shell wm size".format(device_name), "r")
    return result.readline().split("Physical size:")[1].split()[0]


#获取设备分辨率：
def get_device_display(device_name):
    display=os.popen("adb -s {0} shell dumpsys display | {1} DisplayDeviceInfo".format(device_name,find_util)).read()
    mode=re.compile(r'\d+ x \d+')   #提取屏幕分辨率
    try:
        display= mode.findall(display.strip('\n'))[0]
    except IndexError:
        logging.info('display获取索引异常{}'.encode(str_encode).format(display))
    # print "屏幕分辨率大小为:",display
    return display


#获取设备平台版本号
def get_platformVersion(device_name):
    command1='adb -s {} shell getprop'.format(device_name)    #方法二，通过getprop获取android系统属性
    platform_version_cmd='%s ro.build.version.release'%command1
    platform_version = subprocess.Popen(platform_version_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return platform_version.stdout.read().strip()


#获取设备型号
def get_deviceModel(device_name):
    command1='adb -s {} shell getprop'.format(device_name)    #通过getprop获取android系统属性
    deviceModelCMD='%s ro.product.model'%command1
    deviceModel = subprocess.Popen(deviceModelCMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return deviceModel.stdout.read().strip()

#自动亮屏，解锁屏幕
def autoLockscreen(device_name):
        cmd_poweroff_status='adb -s %s shell dumpsys window policy|%s mScreenOnFully'%(device_name,find_util)
        cmd_lock_status='adb -s %s shell dumpsys window policy|%s mShowingLockscreen'%(device_name,find_util)
        lockScreen=subprocess.Popen(cmd_lock_status, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #处理锁屏命令
        powerOff=subprocess.Popen(cmd_poweroff_status, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #处理黑屏命令
        mAwake=powerOff.stdout.read().split()[0].split('=')[-1]   #获取当前手机屏幕是否黑屏，电源休眠状态,false为黑屏
        if mAwake=='false':  #判断手机是否黑屏
            logging.info("current devices mAwake is false.")
            logging.info('当前手机状态为==>黑屏'.encode(str_encode))
            cmd='adb -s {} shell input keyevent 26'.format(device_name)
            os.popen(cmd)  #点击power，亮屏
            logging.info('执行点击power，亮屏'.encode(str_encode))
            mShowingLockscreen=lockScreen.stdout.read().split()[0].split('=')[-1]    #获取当前手机是否为锁屏状态，true为锁屏
            if mShowingLockscreen=='true':   #判断手机是否锁屏
                logging.info('current devices status is lock screen!!!')
                logging.info('当前手机界面处于==>锁屏'.encode(str_encode))
                screen_size=get_device_pix(device_name)
                logging.info('获取当前手机分辨率为:{}'.format(screen_size).encode(str_encode))
                width=screen_size.split('x')[0]
                height=screen_size.split('x')[-1]
                for i in xrange(3):         #如果解锁命令失败，则重试三次
                    cmd_open_up_lock='adb -s {0} shell input swipe {1} {2} {3} {4}'.format(device_name,int(width)/2,int(height)-50,int(width)/2,int(height)/5)
                    # print cmd_open_up_lock
                    cmd_open_left_lock='adb -s {0} shell input swipe {1} {2} {3} {4}'.format(device_name,int(width)/6,int(height)/2,int(width)/2+100,int(height)/2)
                    # print cmd_open_left_lock
                    os.popen(cmd_open_up_lock)   #向上滑动解锁
                    lockScreen=os.popen(cmd_lock_status).read()
                    if lockScreen.split()[0].split('=')[-1]=='false':   #判断是否解锁成功
                        logging.info('屏幕已成功解锁'.encode(str_encode))
                        break
                    else:
                        logging.info('未解锁成功，重试执行!'.encode(str_encode))
                        os.popen(cmd_open_left_lock)   #从左向右滑动解锁
                        lockScreen=os.popen(cmd_lock_status).read()
                        if lockScreen.split()[0].split('=')[-1]=='false':   #判断是否解锁成功
                            logging.info('屏幕已成功解锁'.encode(str_encode))
                            break
                        continue
            else:
                logging.info('当前手机界面处理==>解锁'.encode(str_encode))
        else:
            logging.info('当前手机状态为==>亮屏'.encode(str_encode))
            mShowingLockscreen=lockScreen.stdout.read().split()[0].split('=')[-1]    #获取当前手机是否为锁屏状态，true为锁屏
            if mShowingLockscreen=='true':   #判断手机是否锁屏
                logging.info('current devices status is lock screen!!!')
                logging.info('当前手机界面处于==>锁屏'.encode(str_encode))
                screen_size=get_device_pix(device_name)
                logging.info('获取当前手机分辨率为:{}'.format(screen_size).encode(str_encode))
                width=screen_size.split('x')[0]
                height=screen_size.split('x')[-1]
                for i in xrange(3):         #如果解锁命令失败，则重试三次
                    cmd_open_up_lock='adb -s {0} shell input swipe {1} {2} {3} {4}'.format(device_name,int(width)/2,int(height)-50,int(width)/2,int(height)/5)
                    # print cmd_open_up_lock
                    cmd_open_left_lock='adb -s {0} shell input swipe {1} {2} {3} {4}'.format(device_name,int(width)/6,int(height)/2,int(width)/2+100,int(height)/2)
                    # print cmd_open_left_lock
                    os.popen(cmd_open_up_lock)   #向上滑动解锁
                    lockScreen=os.popen(cmd_lock_status).read()
                    if lockScreen.split()[0].split('=')[-1]=='false':   #判断是否解锁成功
                        logging.info('屏幕已成功解锁'.encode(str_encode))
                        break
                    else:
                        logging.info('未解锁成功，重试执行!'.encode(str_encode))
                        os.popen(cmd_open_left_lock)   #从左向右滑动解锁
                        lockScreen=os.popen(cmd_lock_status).read()
                        if lockScreen.split()[0].split('=')[-1]=='false':   #判断是否解锁成功
                            logging.info('屏幕已成功解锁'.encode(str_encode))
                            break
                        continue
            else:
                logging.info('当前手机界面处理==>解锁'.encode(str_encode))




#android原生截图功能
def screenshot(device_name,screenshot_name):
    if not os.path.exists(os.path.join(os.path.dirname(__file__),'screenshot_result')):
        os.mkdir(os.path.join(os.path.dirname(__file__),'screenshot_result'))
    os.popen('adb -s {} shell /system/bin/screencap -p /sdcard/{}.jpg'.format(device_name,screenshot_name))
    os.popen('adb pull /sdcard/{}.jpg {}\{}.jpg'.format(screenshot_name,os.path.join(os.path.dirname(__file__),'screenshot_result'),screenshot_name))


#获取当前activity
def get_device_currentActivity(device_name,app):
    geterr = 0
    try:
        activity_top_current=os.popen("adb -s %s shell dumpsys activity top | %s  ACTIVITY.*%s"%(device_name,find_util,app)).read()
        logging.info('adb -s {} shell dumpsys activity top | {}  ACTIVITY.*{}'.format(device_name,find_util,app))

        activity_top_current=activity_top_current.split()[1]
        activity_app = activity_top_current.split()[0]
        #logging.info('当前运行程序平台为 :{}'.format(system).encode(str_encode))
        logging.info("Current Activity:==>{}".encode(str_encode).format(activity_top_current))

    except Exception as e:
            logging.info(e)
            geterr=e
    if geterr==0:
        return activity_top_current
    else:
        logging.info('未检测到app的activity，进行重试!'.format(geterr).encode(str_encode))
        get_device_currentActivity(device_name, app)
            #sys.exit()


#获取当前界面activity，循环监控，如当前界面activity发生变化， 则开启自动截图，图片格式jpg
def get_device_currentActivity_and_screenshot(device_name,packapgname):
    while 1:
        #activity_top_current=os.popen("adb -s %s shell dumpsys activity top | %s  ACTIVITY.*%s"%(device_name,find_util,packapgname)).read()
        time.sleep(3)
        try:
            activity_top_current = get_device_currentActivity(device_name, packapgname)
            #activity_top_current=activity_top_current.split()[1]
            activity_current = activity_top_current.split('/')[-1]
        except Exception as ae:
            logging.info("error==>{}".format(ae))
            activity_current=time.strftime("%Y_%m_%d_%H_%M_%S")
            logging.info('activity获取异常，改成赋值当前时间:{}'.encode(str_encode).format(activity_current))


        #如果不存在，创建目录，执行截图
        if not os.path.exists(os.path.join(os.path.dirname(__file__),'screenshot_result')):
            os.mkdir(os.path.join(os.path.dirname(__file__),'screenshot_result'))
            screenshot(device_name,activity_current)
        else:
            if '{}.jpg'.format(activity_current) in os.listdir(os.path.join(os.path.dirname(__file__),'screenshot_result')):
                # print '{}.png exist!'.format(activity_top_current.split('/')[-1])
                pass
            else:
                # print '{}.png not exist!'.format(activity_top_current)
                screenshot(device_name,activity_current)
    print "exit loop screenshot..."


#获取当前界面activity，循环监控，如当前界面activity发生变化， 则开启minicap自动截图，图片格式jpg
def get_device_currentActivity_and_minicap_screenshot(device_name,packapgname):
    minicap=MiniCapScreen(device_name)
    minicap.push_minicap()   #push minicap文件
    minicap.push_minicap_so()  #push minicap.so文件
    flag=minicap.chmod_minicap_permission()   #检查minicap、minicap.so文件是否存在，并修改权限
    # minicap.minicap_server()  #开启minicap server服务

    t=threading.Thread(target=minicap.minicap_server,args=())
    t.start()
    logging.info('minicap server threading running....')

    if flag==True:
        logging.info('use minicap sreenshot!!!')
        while 1:
            activity_top_current=os.popen("adb -s %s shell dumpsys activity top | %s ACTIVITY.*%s"%(device_name,find_util,packapgname)).read()
            activity_top_current=activity_top_current.split()[1]
            pic_name=activity_top_current.split('/')[-1]   #截取activity名作为图片名称

            #如果不存在，创建目录，执行截图
            if not os.path.exists(os.path.join(os.path.dirname(__file__),'screenshot_result')):
                os.mkdir(os.path.join(os.path.dirname(__file__),'screenshot_result'))
                logging.info('screenshot_result dir create sucuess!')
                minicap.minicap_screenshot(pic_name) #截图
                minicap.pull_screenshot(pic_name)   #拉取图片到本地
            else:
                if '{}.jpg'.format(pic_name) in os.listdir(os.path.join(os.path.dirname(__file__),'screenshot_result')):
                    # print '{}.jpg exist!'.format(pic_name)
                    pass
                else:
                    # '{}.jpg not exist!'.format(pic_name)
                    minicap.minicap_screenshot(pic_name) #截图
                    minicap.pull_screenshot(pic_name)   #拉取图片到本地
    else:
        logging.info('use android screenshot!!!')
        get_device_currentActivity_and_screenshot(device_name,packapgname)
    logging.info("exit loop screenshot...")

#根据名称来结束进程
def kill_process_by_name(name):
    if system is "Windows":
        os.popen('taskkill /f /im %s'%name)
        logging.info('taskkill /f /im %s'%name)
    else:
        pid_list=os.popen("ps -ef | awk '{print $2}'|grep %s"%name)
        for pid in pid_list:
            os.popen('kill -9 %s'%int(pid))
            logging.info('kill -9 %s'%int(pid))

#生成hash字符串
def gen_hash_id(device_name,packapgename):
    md5=hashlib.md5()
    md5.update("{}_{}".format(device_name,packapgename))
    return md5.hexdigest()

#获取查找的fsting的进程号,默认查找  monkey
def get_findstr_pid(device_name,fstring=None):
    pid_list = list()
    if fstring is None:
        fout=os.popen('adb -s %s shell ps | %s monkey'%(device_name,find_util))
    else:
        fout = os.popen('adb -s %s shell ps | %s %s' % (device_name,find_util,fstring))
    try:
        fs = fout.read().strip()
        foutlist = fs.split()
        listlen = len(foutlist)
        for  k  in range(1,listlen,9):
            pid = foutlist[k]
            pid_list.append(pid)
            logging.info("pid_list[{}] is {}".format(k,pid))
    except Exception as e:
        logging.info("#Error: {}".format(e))

    return pid_list

#获取logcat进程列表
def get_logcat_pid(device_name):
    pid_list = list()
    if system is "Windows":
        fout=os.popen('adb -s %s shell ps | findstr logcat'%(device_name))
    else:
        fout=os.popen("adb -s %s shell ps | grep logcat"%(device_name))
    try:
        fs = fout.read().strip()
        foutlist = fs.split()
        listlen = len(foutlist)
        for  k  in range(1,listlen,9):
            pid = foutlist[k]
            pid_list.append(pid)
            logging.info("pid_list[{}] is {}".format(k,pid))
    except Exception as e:
        logging.info("#Error: {}".format(e))

    return pid_list

#停止pid号
def adb_logcat_stop(device_name,pid):
    logging.info("PID Type is {}".format(type(pid)))
    if type(pid)==list:
        for p  in  pid:
            cmd = 'adb -s {device_name} shell kill -9 {pid}'.format(device_name=device_name, pid=p)
            logging.info(cmd)
            os.popen(cmd).read()
    else:
        logging.info('停止logcat日志功能'.encode(str_encode))
        cmd='adb -s {device_name} shell kill -9 {pid}'.format(device_name=device_name,pid=pid)
        logging.info(cmd)
        os.popen(cmd).read()

#清除logcat缓存
def adb_logcat_clear(device_name):
    logging.info('开始清空logcat之前缓存的日志'.encode(str_encode))
    os.popen('adb -s {} logcat -c'.format(device_name)).read()

#获取指定包名进程PID号
def get_process_pid(device_name,packapgename):
    if system is "Windows":
        pidcmd=   'adb -s  '+ device_name + '  shell ps | findstr ^' + packapgename + '$'
        logging.info('pidcmd={}'.format(pidcmd))
        a=os.popen(pidcmd)
        pidcmdouts=a.read()
        logging.info("cmdout=={}".format(pidcmdouts))
        pidlist=pidcmdouts.split()
        pidoutlistlen=len(pidlist)
        logging.info('len=={}'.format(pidoutlistlen))
        pid=pidlist[1]
        logging.info('pid={}'.format(pid))
    else:
        pid=os.popen("adb -s %s shell ps | grep ^%s$'"%(device_name,packapgename)).read().strip()[1]

    logging.info("包名为{0}==>对应的PID为:{1}".format(packapgename,pid).encode(str_encode))
    return pid


#用于Logcat捕获app操作日志（自定义logLevel级别）
def adb_logcat(device_name,packapgename):
    if system is 'Windows':
        logging.info('开始抓取logcat日志...'.encode(str_encode))
    else:
        logging.info('开始抓取logcat日志...'.encode(str_encode))

    pid=get_process_pid(device_name,packapgename)
    adb_logcat_cmd='adb -s {device_name} logcat -v time *:{logLevel} |{find_util} {pid}|{find_util} {packapgename} >{logdir}'.format(device_name=device_name,
    logLevel=logLevel,find_util=find_util,pid=pid,packapgename=packapgename,logdir=os.path.join(os.path.join(os.path.dirname(__file__),'log'),'app.log'))
    logging.info(adb_logcat_cmd)
    os.popen(adb_logcat_cmd).read()


#用于Logcat捕获app异常操作日志
def adb_logcat_error(device_name,packapgename):
    if system is 'Windows':
        logging.info('抓取logcat异常日志...'.encode(str_encode))
    else:
        logging.info('抓取logcat异常日志...'.encode(str_encode))

    pid=get_process_pid(device_name,packapgename)
    adb_logcat_cmd_error='adb -s {device_name} logcat -v time *:W |{find_util} {pid}|{find_util} {packapgename} >{logdir}'.format(device_name=device_name,find_util=find_util,pid=pid,packapgename=packapgename,logdir=os.path.join(os.path.join(os.path.dirname(__file__),'log'),'app_error.log'))
    logging.info(adb_logcat_cmd_error)
    os.popen(adb_logcat_cmd_error).read()


#执行monkey命令
def runMonkeyCMD(device_name,app,count,throttle):
    packapgname=app
    try:
        activity_top_current=get_device_currentActivity(device_name,packapgname)
        packapgename=activity_top_current.split('/')[0]

        #新开线程，用于实时监控屏幕activiy，进行截图操作
        screenshot_pro=threading.Thread(target=get_device_currentActivity_and_screenshot,args=(device_name,packapgname))
        screenshot_pro.setDaemon(True)
        screenshot_pro.start()
        logging.info("start new threading :[{}] use screenshot".format(screenshot_pro.getName()))

        #清除logcat日志
        adb_logcat_clear(device_name)
        #新开线程，用于抓取自定义logcat日志
        adb_logcat_pro=threading.Thread(target=adb_logcat,args=(device_name,packapgename))
        adb_logcat_pro.setDaemon(True)
        adb_logcat_pro.start()
        adb_logcat_pro.join(0.5)
        logging.info("start new threading :[{}] use logcat logLeval log".format(adb_logcat_pro.getName()))

        #新开线程，用于抓取Warning级别以上的日志
        adb_logcat_pro_error=threading.Thread(target=adb_logcat_error,args=(device_name,packapgename))
        adb_logcat_pro_error.setDaemon(True)
        adb_logcat_pro_error.start()
        adb_logcat_pro_error.join(1)
        logging.info("start new threading :[{}] use logcat Warning log".format(adb_logcat_pro_error.getName()))
        logcat_pid_list=get_logcat_pid(device_name)
        logging.info('执行后，获取logcat PID列表:{}'.format(logcat_pid_list).encode(str_encode))


        s=get_digit()   #生成随机序列号

        if packapgename==app:
            logging.info("app is activity_top_current!!!")
        cmd="adb -s {} shell monkey".format(device_name)
        p=os.popen(cmd)
        if 'usage:' in p.read() or '' in p.read():
            logging.info("hi,monkey already installed!")
            logging.info("准备执行monkey测试".encode(str_encode))
            path=os.path.join(os.path.join(os.path.dirname(__file__),'log'),'monkey.log')
            cmd_exc='%s -p %s -s %s --ignore-crashes --ignore-timeouts --monitor-native-crashes --throttle %s --pct-touch %s --pct-motion %s ' \
                 '--pct-nav %s --pct-majornav %s -v -v -v %s 2>&1 >%s'%(cmd,app,s,throttle,pct_touch,pct_motion,pct_nav,pct_majornav,count,path)
            logging.info('Monkey 的命令为'.encode(str_encode))
            logging.info(cmd_exc)
            for x in xrange(3):
                    logging.info('执行monkey命令倒计时{}sec'.format(3-x).encode(str_encode))
                    time.sleep(1)
            device=subprocess.Popen(cmd_exc, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            device_info=device.stdout.read()
            return device_info,logcat_pid_list
        else:
            logging.info("monkey not fonud!")
            return None
    except Exception:
        traceback.print_exc()

#数据完整分析
def anlayzeData(device_name,packagename,count,throttle):
    activitys_list=[]   #用于存储所有activity列表
    events_dict={}   #用于存储所有事件类型，以事件类型为key，activiy为value
    events_dict_bak={}   #用于统计具有相同value的key，保存到新的字典中存储
    events_count_dict={}    #用于存储各个activity对应的事件类型个数
    events_data_dict={}    #用于存储各个activity对应的事件类型详细
    try:
        device_info,logcat_pid_list=runMonkeyCMD(device_name,packagename,count,throttle)
        #停止logcat命令
        logging.info('收集到的logcat命令产生的pid进程号为:{}'.format(logcat_pid_list).encode(str_encode))
        if logcat_pid_list is not None and len(logcat_pid_list)>0:
            for pid in logcat_pid_list:
                adb_logcat_stop(device_name,int(pid))
        logcat_pid_list=get_logcat_pid(device_name)
        if len(logcat_pid_list)==0:
            logging.info('logcat命令停止成功!'.encode(str_encode))
        else:
            logging.info('重新获取logcat PID:{}'.format(logcat_pid_list).encode(str_encode))
            for pid in logcat_pid_list:
                adb_logcat_stop(device_name,int(pid))
            logging.info('logcat命令停止成功!'.encode(str_encode))
    except:
        pass
    if os.path.exists(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'monkey.log')):
        logging.info('Monkey File Exist!')
    else:
        logging.info('Monkey File not Exist and exit process!!!')
        if system is "Windows":
            os.popen('taskkill /f /pid {}'.format(os.getpid()))
        else:
            os.popen('kill -9 {}'.format(os.getpid()))

    f_r=open(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'monkey.log'),'rb')
    f_w_event=open(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'event.log'),'wb')

    #提取遍历过的所有activity
    activity_re_mode=re.compile(r'.*cmp=(.*)in package')
    #event事件类型正则匹配模式
    event_re_mode=re.compile(r'Sending(.*): ')

    print '##'*50+'提取事件类型记录及activity记录'.encode(str_encode)+'##'*50+'\n'
    for line_no,line_content in enumerate(f_r):

        #提取事件类型记录
        if ':Sending' in line_content and '(' in line_content and ')' in line_content:
            event=event_re_mode.findall(line_content)
            f_w_event.write('%s==>%s\n'%(line_no+1,event))
            events_dict[str(event)+str(line_no+1)]=str(value)
        #提取activity记录
        if 'Allowing start of Intent' in line_content and 'in package %s'%packagename in line_content:
            activity = activity_re_mode.findall(line_content)[0].split('}')[0]
            f_w_event.write('%s==>%s\n'%(line_no+1,activity))
            activitys_list.append(activity)
            value=activity+str(line_no+1)
            continue

    # print '##'*50+'遍历过所有的activity列表及统计事件个数'.encode(str_encode)+'##'*50+'\n'
    # print activitys_list   #遍历过的所有activity列表
    # print len(activitys_list)    #遍历activity个数
    # print "activitys:",list(set(activitys_list))    #activity去重后的列表
    # print "activitys count:",len(list(set(activitys_list)))   #activity去重后的个数
    # print 'event count:',len(events_dict)   #统计事件个数
    # print '##'*50+'查询出来的事件类型,提取出所有相同的value值对应的key'.encode(str_encode)+'##'*50+"\n"
    #根据查询出来的事件类型，提取出所有相同的value值对应的key，组成新的字典
    for k,v in events_dict.items():
        if events_dict_bak.has_key(v):
            events_dict_bak[v].append(k)
        else:
            events_dict_bak[v]=[k]
    # print activity_dict_bak

    #根据上述生成的新的字典，重新提取key中activity值（key去重），组成新的字典,统计覆盖事件类型数量
    for k,v in events_dict_bak.items():
        #匹配activty值
        activity_key_mode=re.compile(r'(\D+)\d+')
        g=activity_key_mode.findall(k)[0]
        if events_count_dict.has_key(g):
            events_count_dict[g].append(len(v))
        else:
            events_count_dict[g]=[len(v)]


    #根据上述生成的新的字典，重新提取key中activity值（key去重），组成新的字典,统计覆盖的各个事件类型详细
    for k,v in events_dict_bak.items():
        # print k,'==>',v
        #匹配activty值
        activity_key_mode=re.compile(r'(\D+)\d+')
        g=activity_key_mode.findall(k)[0]
        if events_data_dict.has_key(g):
            events_data_dict[g].append(v)
        else:
            events_data_dict[g]=[v]

    #计算各个activity对应的事件总数
    # print 'event count:',len(events_dict)   #统计事件总数
    for k,v in events_count_dict.items():
        print k,'==>',sum(v)

    f_r.close()
    f_w_event.close()

    abnormal_dict_monkey=check_errorMessage(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'monkey.log'),exception_list)
    abnormal_dict_logcat=check_errorMessage(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'app.log'),exception_list)
    logging.info('monkey.log文件检查到异常情况:{}'.format(str(abnormal_dict_monkey)).encode(str_encode))
    logging.info('app.log文件检查到异常情况:{}'.format(str(abnormal_dict_logcat)).encode(str_encode))
    return count,events_dict,events_data_dict,events_count_dict,abnormal_dict_monkey,abnormal_dict_logcat   #返回入参随机事件总数、提取的所有事件类型含遍历的activity集合、各个activtiy对应的事件集合


#当设备异常中断，对已获取到的数据进行分析
def anlayzeDataException(device_name,packagename,count,throttle):
    activitys_list=[]   #用于存储所有activity列表
    events_dict={}   #用于存储所有事件类型，以事件类型为key，activiy为value
    events_dict_bak={}   #用于统计具有相同value的key，保存到新的字典中存储
    events_count_dict={}    #用于存储各个activity对应的事件类型个数
    events_data_dict={}    #用于存储各个activity对应的事件类型详细
    if os.path.exists(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'monkey.log')):
        logging.info('Monkey File Exist!')
    else:
        logging.info('Monkey File not Exist and exit process!!!')
        if system is "Windows":
            os.popen('taskkill /f /pid {}'.format(os.getpid()))
        else:
            os.popen('kill -9 {}'.format(os.getpid()))

    f_r=open(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'monkey.log'),'rb')

    f_w_event=open(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'event.log'),'wb')

    #提取遍历过的所有activity
    activity_re_mode=re.compile(r'.*cmp=(.*)in package')

    #event事件类型正则匹配模式
    event_re_mode=re.compile(r'Sending(.*): ')

    print '##'*50+'提取事件类型记录及activity记录'.encode(str_encode)+'##'*50+'\n'

    for line_no,line_content in enumerate(f_r):

         #print line_no+1,'===========>',line_content
        #提取事件类型记录
        if ':Sending' in line_content and '(' in line_content and ')' in line_content:
            event=event_re_mode.findall(line_content)
            print line_no+1,'==>',event
            f_w_event.write('%s==>%s\n'%(line_no+1,event))
            events_dict[str(event)+str(line_no+1)]=str(value)
        #提取activity记录
        #print  "提取activity记录"
        if 'Allowing start of Intent' in line_content and 'in package %s'%packagename in line_content:
            #print line_no,line_content
            activity = activity_re_mode.findall(line_content)[0].split('}')[0]
            print line_no+1,'==>',activity
            f_w_event.write('%s==>%s\n'%(line_no+1,activity))
            activitys_list.append(activity)
            value=activity+str(line_no+1)
            continue

    # print '##'*50+'遍历过所有的activity列表及统计事件个数'.encode(str_encode)+'##'*50+'\n'
    # print activitys_list   #遍历过的所有activity列表
    # print len(activitys_list)    #遍历activity个数
    # print "activitys:",list(set(activitys_list))    #activity去重后的列表
    # print "activitys count:",len(list(set(activitys_list)))   #activity去重后的个数
    # print 'event count:',len(events_dict)   #统计事件个数
    # print '##'*50+'查询出来的事件类型,提取出所有相同的value值对应的key'.encode(str_encode)+'##'*50+"\n"
    #根据查询出来的事件类型，提取出所有相同的value值对应的key，组成新的字典
    for k,v in events_dict.items():
        if events_dict_bak.has_key(v):
            events_dict_bak[v].append(k)
        else:
            events_dict_bak[v]=[k]

    #根据上述生成的新的字典，重新提取key中activity值（key去重），组成新的字典,统计覆盖事件类型数量
    for k,v in events_dict_bak.items():
        # print k,'==>',len(v)
        #匹配activty值
        activity_key_mode=re.compile(r'(\D+)\d+')
        g=activity_key_mode.findall(k)[0]
        if events_count_dict.has_key(g):
            events_count_dict[g].append(len(v))
        else:
            events_count_dict[g]=[len(v)]

    #根据上述生成的新的字典，重新提取key中activity值（key去重），组成新的字典,统计覆盖的各个事件类型详细
    for k,v in events_dict_bak.items():
        # print k,'==>',v
        #匹配activty值
        activity_key_mode=re.compile(r'(\D+)\d+')
        g=activity_key_mode.findall(k)[0]
        if events_data_dict.has_key(g):
            events_data_dict[g].append(v)
        else:
            events_data_dict[g]=[v]

    print '\n'+'#'*40
    #计算各个activity对应的事件总数
    print 'event count:',len(events_dict)   #统计事件总数
    for k,v in events_count_dict.items():
        print k,'==>',sum(v)

    f_r.close()
    f_w_event.close()

    abnormal_dict_monkey=check_errorMessage(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'monkey.log'),exception_list)
    abnormal_dict_logcat=check_errorMessage(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'app.log'),exception_list)
    logging.info('monkey.log文件检查到异常情况:{}'.format(str(abnormal_dict_monkey)).encode(str_encode))
    logging.info('app.log文件检查到异常情况:{}'.format(str(abnormal_dict_logcat)).encode(str_encode))
    return count,events_dict,events_data_dict,events_count_dict,abnormal_dict_monkey,abnormal_dict_logcat   #返回入参随机事件总数、提取的所有事件类型含遍历的activity集合、各个activtiy对应的事件集合


#检查指定文件中是否包含指定异常字段，如存在，则统计出现次数及行号
def check_errorMessage(path,exception_list):
    '''
    返回内容：字典类型，key为异常字段，value为，异常字段出现的次数及第一次出现在文件中的行号
    eg:{'IllegalArgument': (['IllegalArgument', 2], 77), 'ArrayIndexOutOfBounds': (['ArrayIndexOutOfBounds', 1], 60)}
    '''
    abnormal_dict={}
    abnormal_list=[]
    if isinstance(exception_list,list):
        if os.path.exists(os.path.join(path)):
            with open(os.path.join(path),'rb') as fopen:
                for line_no,line_content in enumerate(fopen):
                    #logging.info('abnormal_dict1={}'.format(abnormal_dict))
                    for e in exception_list:
                        #logging.info('abnorma2_dict={}'.format(abnormal_dict))
                        if e in line_content:
                            if e in  abnormal_dict.keys():
                                abnormal_dict[e][1] = abnormal_dict[e][1]+1
                                abnormal_dict[e][-1].append(2*line_no+1)
                            else:
                                abnormal_dict[e]=[e,1,[line_content.strip(),2*line_no+1]]
                            #logging.info('abnorma3_dict={}'.format(abnormal_dict))
                        else:
                            continue
                            #logging.info('abnorma4_dict={}'.format(abnormal_dict))
                fopen.seek(0)
                '''
                for e in exception_list:
                    logging.info('abnorma5_dict={}'.format(abnormal_dict))
                    if e in str(fopen.read()):
                        logging.info('abnorma6_dict={}'.format(abnormal_dict))
                        fopen.seek(0)
                        t= [e,str(fopen.read()).count(e)]
                        abnormal_list.append(t)
                        logging.info('abnorma7_dict={}'.format(abnormal_dict))
                        fopen.seek(0)
                abnormal_list=filter(lambda x:x[1]>0,abnormal_list)
                logging.info('abnorma8_dict={}'.format(abnormal_dict))
                for i in abnormal_list:
                    if isinstance(i,(list,tuple)) and len(i)==2:
                        abnormal_dict[i[0]] = i[0],i[1]
                        #abnormal_dict[i[0]]=i,abnormal_dict[i[0]]
                        logging.info('abnorma9_dict={}'.format(abnormal_dict))
'''
        else:
            logging.info("{} not found!".format(path).encode(str_encode))

        print '#'*25+'abnormal list:'+'#'*25
        logging.info("#####abnormal_dict1#####")
        logging.info(abnormal_dict)
        logging.info("#####abnormal_dict2#####")
        return abnormal_dict



#分析logcat error日志
def anlayzeLogcatLog(path):
    re_tag=re.compile(r'.*\d (?P<tag>.*)\( ?\d+\):(?P<lineContent>.*)')
    total_content=[]
    logging.info('开始分析logcat异常日志...'.encode(str_encode))
    with open(path) as f:
        for line,content in enumerate(f):
            m=re_tag.match(content)
            try:
                lineContent=(m.group('tag').strip(),m.group('lineContent').strip())
            except Exception as e:
                logging.info(e)
            total_content.append(lineContent)
    exception_list_dict=Counter(total_content)

    for key,value in exception_list_dict.iteritems():
        print key,value
        logging.info('KEY   {}; VALUE   {}'.format(str(key),str(value)).encode(str_encode))
    if len(exception_list_dict)>0:
        logging.info('logcat error存在异常个数为:{}'.format(len(exception_list_dict)).encode(str_encode))
        logging.info('分析logcat异常日志完成!'.encode(str_encode))
    else:
        logging.info('logcat error未捕获到任何异常!'.encode(str_encode))
    return exception_list_dict




#minicap截图类
class MiniCapScreen(object):
    def __init__(self,device_name):
        self.device_name=device_name

    #获取cpu版本
    def get_cpu_version(self):
        cmd='adb -s {} shell getprop ro.product.cpu.abi'.format(self.device_name)
        cpu_version=os.popen(cmd).read().strip()
        return cpu_version

    #获取cpu版本
    def get_sdk_version(self):
        cmd='adb -s {} shell getprop ro.build.version.sdk'.format(self.device_name)
        sdk_version=os.popen(cmd).read().strip()
        return sdk_version

    #将minicap_so文件push到手机指定目录下
    def push_minicap_so(self):
        path=os.path.join(os.path.join(os.path.dirname(__file__),'minicap'),'shared')
        cpu_abi=self.get_cpu_version()
        sdk_version=self.get_sdk_version()
        if os.path.isdir(path):
            if system is 'Windows':
                cmd='adb -s {0} push {1}\\android-{2}\{3}\minicap.so /data/local/tmp/'.format(self.device_name,path,sdk_version,cpu_abi)
            else:
                cmd='adb -s {0} push {1}/android-{2}/{3}/minicap.so /data/local/tmp/'.format(self.device_name,path,sdk_version,cpu_abi)

            logging.info(cmd)
            p1 = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p1.communicate()
            if p1.returncode==0:
                logging.info('push_minicap_so==>success')
        else:
            logging.info('minicap dir not exist!')

    #将minicap文件push到手机指定目录下
    def push_minicap(self):
        path=os.path.join(os.path.join(os.path.dirname(__file__),'minicap'),'bin')
        cpu_abi=self.get_cpu_version()
        if os.path.isdir(path):
            if system is 'Windows':
                cmd='adb -s {0} push {1}\{2}\minicap /data/local/tmp/'.format(self.device_name,path,cpu_abi)
            else:
                cmd='adb -s {0} push {1}/{2}/minicap /data/local/tmp/'.format(self.device_name,path,cpu_abi)
            logging.info(cmd)
            p1 = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p1.communicate()
            if p1.returncode==0:
                logging.info('push_minicap==>success')
        else:
            logging.info('minicap dir not exist!')

    #检查minicap、minicap.so文件是否存在在/data/local/tmp目录下
    def check_minicap_exist(self):
        p1 = subprocess.Popen('adb -s {} shell cd data&&cd local&&cd tmp&&ls minicap* -l'.format(self.device_name), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if len(p1.stdout.readlines())>=2:
            logging.info('minicap and minicap.so exist!')
            return  True
        else:
            logging.info('minicap or minicap.so not found!')
            return False

    #进到手机/data/local/tmp目录下，修改minicap\minicap.so文件操作权限
    def chmod_minicap_permission(self):
        if self.check_minicap_exist()==True:
            p2 = subprocess.Popen('adb -s {} shell cd data&&cd local&&cd tmp&&chmod 777 mini*&&ls mini* -l'.format(self.device_name),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if 'rwx' in p2.stdout.read():
                logging.info('chmod permission success!')
                return True
            else:
                logging.info('chmod permission failed!')
                return False
        else:
            logging.info('check_minicap_permissin failed!')


    #开启minicap服务
    def minicap_server(self):
        cmd='adb -s {} shell "LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1080x1920@1080x1920/0"'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(p.stdout.read())

    #利用minicap截图
    def minicap_screenshot(self,pic_name):
        cmd='adb -s {} shell "LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P 1080x1920@1080x1920/0 -s > /mnt/sdcard/{}.jpg"'.format(self.device_name,pic_name)
        p = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if 'JPG encoder' in p.stdout.read():
            logging.info('命令执行:{}==>截图成功'.encode(str_encode).format(cmd))

    def pull_screenshot(self,pic_name):
        if not os.path.exists(os.path.join(os.path.dirname(__file__),'screenshot_result')):
            os.mkdir(os.path.join(os.path.dirname(__file__),'screenshot_result'))
        cmd='adb -s {0} pull /mnt/sdcard/{1}.jpg {2}'.format(self.device_name,pic_name,os.path.join(os.path.dirname(__file__),'screenshot_result'))
        p = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
        if p.returncode==0:
            logging.info('{}命令拉取图片==>成功'.encode(str_encode).format(cmd))



class GetDeviceInfo(object):
    def __init__(self):
        pass

    #通过应用包名appPackage来获取app版本号
    def getAppVersion(self,device_name,packagename):
        try:
            if system is 'Windows':
                cmd="adb -s %s shell dumpsys package %s | findstr versionName"%(device_name,packagename)
            else:
                cmd="adb -s %s shell dumpsys package %s | grep versionName"%(device_name,packagename)
            versionName=os.popen(cmd).read().strip().split('=')[-1]
            return versionName
        except Exception as e:
            print e

    #获取手机设备信息
    def get_phone_Msg(self,device_name):
        os.popen('adb -s {} shell cat /system/build.prop >{}'.format(device_name,os.path.join(os.path.join(os.path.dirname(__file__),'log'),'build.txt'))) #存放的手机信息
        l_list = []
        with  open(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'build.txt'), "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.split('=')
                #Android 系统，如anroid 4.0
                if (line[0] == 'ro.build.version.release'):
                    l_list.append(line[1])
                    #手机名字
                if (line[0]=='ro.product.model'):
                    l_list.append(line[1])
                    #手机品牌
                if (line[0]=='ro.product.brand'):
                    l_list.append(line[1])
        return l_list

class ResultReport(object):
    #report_name = '1'
    def __init__(self):
        creat_time=time.strftime("%Y_%m_%d_%H_%M_%S")
        report_name='Monkey测试结果报告_{}'.format(creat_time).decode('utf-8').encode('gbk')
        report_name=os.path.join(os.path.dirname(__file__),'{}.xlsx'.format(report_name))
        self.workbook = xlsxwriter.Workbook(report_name)

        if os.path.exists(os.path.join(os.path.dirname(__file__),'screenshot_result')):
            try:
                shutil.rmtree(os.path.join(os.path.dirname(__file__),'screenshot_result'))   #shutil.rmtree用于删除非空目录
                logging.info("删除截图目录成功!".encode(str_encode))
            except WindowsError:
                pass
        else:
            pass
        if os.path.exists(os.path.join(os.path.dirname(__file__),'log')):

            try:
                shutil.rmtree(os.path.join(os.path.dirname(__file__),'log'))   #shutil.rmtree用于删除非空目录
                logging.info("删除log目录成功!".encode(str_encode))
                time.sleep(0.5)
                os.mkdir(os.path.join(os.path.dirname(__file__),'log'))
                logging.info('创建log目录成功!'.encode(str_encode))
            except WindowsError:
                pass
        else:
            os.mkdir(os.path.join(os.path.dirname(__file__),'log'))
            logging.info('创建log目录成功'.encode(str_encode))

    def gen_monkey_report(self):
        global count
        try:
            count,events_dict,events_data_dict,events_count_dict,abnormal_dict,abnormal_dict_2=anlayzeData(device_name,packapgename,count,throttle)
        except Exception as e:
            logging.info(e)

        worksheet3 = self.workbook.add_worksheet('Monkey测试报告汇总')
        worksheet4 = self.workbook.add_worksheet('异常明细表')
        worksheet = self.workbook.add_worksheet('Monkey测试报告详细')
        worksheet2 = self.workbook.add_worksheet('Activity截图信息')

        activity_list=[]   #用于存放activity列表
        events_count_list=[]   #用于存放各个activity列表对应的事件总数
        for k,v in events_count_dict.items():
            try:
                if '(' in k and ')' in k:
                        k=k.split(' (')[0]  #防止从monkey提取出来的activity包含 (has extras)等字样
            except Exception as e:
                logging.info('从activity中去除has extras字样出现异常:{}'.format(e))

            activity_list.append(k)
            events_count_list.append(sum(v))


        worksheet.set_column('A:A',len(activity_list[-1])+7)  #设置A列列宽
        worksheet.set_column('B:G',len(str(count))+14)  #设置B:G列列宽
        worksheet.set_column('F:F',len(str(count))+25)

        #创建图表字体样式
        format_title=self.workbook.add_format()    #设置title和content样式
        format_head=self.workbook.add_format()
        format_title_yellew=self.workbook.add_format()
        format_content=self.workbook.add_format()
        format_content_no_border=self.workbook.add_format()

        format_content_left=self.workbook.add_format()
        format_content_left_border=self.workbook.add_format()

        format_screenshot_activity=self.workbook.add_format()
        format_screenshot_activity_red=self.workbook.add_format()
        format_Exceptions_red=self.workbook.add_format()

        format_Exceptions_green=self.workbook.add_format()

        #根据条件，如包括高、大则标红色
        worksheet.conditional_format('F5:G5', {'type':     'text',
                                       'criteria': 'not containing',
                                       'value':    '未检查到异常',
                                      'format':   format_Exceptions_red})

        worksheet3.conditional_format('G5:K5', {'type':     'text',
                                       'criteria': 'not containing',
                                       'value':    '未检查到异常',
                                      'format':   format_Exceptions_red})

        format_Exceptions_red.set_align('center')
        format_Exceptions_red.set_font(u'微软雅黑')
        format_Exceptions_red.set_font_size(11)
        format_Exceptions_red.set_font_color('#FF0000')
        format_Exceptions_red.set_text_wrap()    #自动换行
        format_Exceptions_red.set_align('center')  #水平居中
        format_Exceptions_red.set_align('vcenter')  #垂直居中
        format_Exceptions_red.set_border(1)

        format_Exceptions_green.set_align('center')
        format_Exceptions_green.set_font(u'微软雅黑')
        format_Exceptions_green.set_font_size(11)
        format_Exceptions_green.set_font_color('#00B050')
        format_Exceptions_green.set_text_wrap()    #自动换行
        format_Exceptions_green.set_align('center')  #水平居中
        format_Exceptions_green.set_align('vcenter')  #垂直居中
        format_Exceptions_green.set_border(1)

        format_title.set_border(1)
        format_title.set_font_size(12)
        format_title.set_align('center')
        format_title.set_bg_color('#cccccc')
        format_title.set_font(u'微软雅黑')
        format_title.set_text_wrap()    #自动换行
        format_title.set_align('center')  #水平居中
        format_title.set_align('vcenter')  #垂直居中

        format_title_yellew.set_border(1)
        format_title_yellew.set_bold()
        format_title_yellew.set_font_size(12)
        format_title_yellew.set_align('center')
        format_title_yellew.set_bg_color('#FFFF00')
        format_title_yellew.set_font(u'微软雅黑')
        format_title_yellew.set_text_wrap()    #自动换行
        format_title_yellew.set_align('center')  #水平居中
        format_title_yellew.set_align('vcenter')  #垂直居中


        format_head.set_bold(1)  #加粗
        format_head.set_border(1)
        format_head.set_font_size(20)
        format_head.set_text_wrap()    #自动换行
        format_head.set_align('center')  #水平居中
        format_head.set_align('vcenter')  #垂直居中
        format_head.set_font(u'微软雅黑')


        format_screenshot_activity.set_bold(1)  #加粗
        format_screenshot_activity.set_border(1)
        format_screenshot_activity.set_font_size(15)
        format_screenshot_activity.set_text_wrap()    #自动换行
        format_screenshot_activity.set_align('center')  #水平居中
        format_screenshot_activity.set_align('vcenter')  #垂直居中
        format_screenshot_activity.set_font(u'微软雅黑')


        format_screenshot_activity_red.set_bold(1)  #加粗
        format_screenshot_activity_red.set_border(1)
        format_screenshot_activity_red.set_font_size(15)
        format_screenshot_activity_red.set_text_wrap()    #自动换行
        format_screenshot_activity_red.set_align('center')  #水平居中
        format_screenshot_activity_red.set_align('vcenter')  #垂直居中
        format_screenshot_activity_red.set_font(u'微软雅黑')
        format_screenshot_activity_red.set_font_color('#FF0000')

        format_content.set_border(1)
        format_content.set_align('center')
        format_content.set_font(u'微软雅黑')
        format_content.set_font_size(11)
        format_content.set_text_wrap()    #自动换行
        format_content.set_align('center')  #水平居中
        format_content.set_align('vcenter')  #垂直居中

        format_content_no_border.set_align('center')
        format_content_no_border.set_align('vcenter')
        format_content_no_border.set_font(u'微软雅黑')
        format_content_no_border.set_font_size(11)
        format_content_no_border.set_text_wrap()    #自动换行

        format_content_left.set_align('left')
        format_content_left.set_align('vcenter')
        format_content_left.set_font(u'微软雅黑')
        format_content_left.set_font_size(11)
        format_content_left.set_text_wrap()    #自动换行

        format_content_left_border.set_align('left')
        format_content_left_border.set_align('vcenter')
        format_content_left_border.set_font(u'微软雅黑')
        format_content_left_border.set_font_size(11)
        format_content_left_border.set_text_wrap()    #自动换行
        format_content_left_border.set_border()


        worksheet.set_row(0,36)   #设置第一行，行高为36
        worksheet.merge_range('A1:G1',u'Monkey随机测试覆盖activti及事件类型详细统计',format_head)
        worksheet2.set_row(0,36)   #设置第一行，行高为36
        worksheet2.merge_range('A1:K1',u'Activity与界面截图对应表（仅供参考）',format_head)
        worksheet3.set_row(0,36)   #设置第一行，行高为36
        worksheet3.merge_range('A1:K1',u'Monkey随机事件覆盖测试汇总概况',format_head)

        worksheet4.set_row(0,36)   #设置第一行，行高为36
        worksheet4.merge_range('A1:D1',u'日志异常明细表',format_head)

        worksheet4.set_column('A1:C1',22)
        worksheet4.set_column('D1:D1',120)

        worksheet3.set_row(4,72)
        worksheet3.set_row(5,72)   #设置第5\6行，行高为50

        #设置表4，从第三行起，前一百行，行高为30px
        for col in xrange(100):
            worksheet4.set_row(2+col,30)

        #表4，异常明细表
        title=['错误类别','出现次数','所属分析器','异常日志明细']
        worksheet4.write_row('A2',title,format_title_yellew)
        logcat_exception_dict=anlayzeLogcatLog(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'app_error.log'))

        global excel_lineon
        excel_lineon=3
        #汇总表中，判断是否检查到异常逻辑
        if len(abnormal_dict)>0 or len(abnormal_dict_2)>0 or len(logcat_exception_dict)>0:
            abnormal_flag='存在异常!'
            exception_flag='异常个数:{}'.format(len(abnormal_dict)+len(abnormal_dict_2)+len(logcat_exception_dict))
            if len(logcat_exception_dict)>0:
                logging.info('logcat error插入异常起始行号为:{}'.format(excel_lineon).encode(str_encode))
                for key,value in logcat_exception_dict.iteritems():
                    if len(key)==2:
                        worksheet4.write('A{}'.format(excel_lineon),key[0],format_content)
                        worksheet4.write('B{}'.format(excel_lineon),value,format_content)
                        worksheet4.write('C{}'.format(excel_lineon),'logcat error',format_content)
                        worksheet4.write('D{}'.format(excel_lineon),key[1],format_content_left_border)
                        excel_lineon+=1
            if len(abnormal_dict)>0:
                excel_lineon=excel_lineon
                logging.info('monkey log插入异常起始行号为:{}'.format(excel_lineon).encode(str_encode))
                for key,value in abnormal_dict.iteritems():
                    logging.info('key=={},Value={}'.format(key,value).encode(str_encode))
                    if len(value)==3 and isinstance(value[-1],(list,tuple)):
                        worksheet4.write('A{}'.format(excel_lineon),key,format_content)
                        worksheet4.write('B{}'.format(excel_lineon),value[1],format_content)
                        worksheet4.write('C{}'.format(excel_lineon),'monkey',format_content)
                        worksheet4.write('D{}'.format(excel_lineon),str(value),format_content_left_border)
                        excel_lineon+=1
            if len(abnormal_dict_2)>0:
                excel_lineon=excel_lineon
                logging.info('logcat log插入异常起始行号为:{}'.format(excel_lineon).encode(str_encode))
                for key,value in abnormal_dict_2.iteritems():
                    if len(value)==3 and isinstance(value[1],(list,tuple)):
                        worksheet4.write('A{}'.format(excel_lineon),key,format_content)
                        worksheet4.write('B{}'.format(excel_lineon),value[1],format_content)
                        worksheet4.write('C{}'.format(excel_lineon),'logcat log',format_content)
                        worksheet4.write('D{}'.format(excel_lineon),str(value),format_content_left_border)
                        excel_lineon+=1
        else:
            abnormal_flag='未检查到异常'
            exception_flag='未分析到异常界面及原因!'

        # exception_flag_detail=[]
        # exception_flag_reason=[]
        # if len(abnormal_dict)>0:
        # #分析monkey行为日志
        # 	if system is 'Windows':
        # 		with open(os.path.join(os.path.dirname(__file__),'log\\monkey.log'),'rb') as f_r:
        # 			with open(os.path.join(os.path.dirname(__file__),'log\\monkey_bak.log'),'wb') as f_w:
        # 				for eachline in f_r.readlines():
        # 					f_w.write(eachline.strip()+'\n')   #删除空白行
        # 		logging.info('检查到monkey异常个数为:{}'.format(len(abnormal_dict)))
        # 		exception_list=abnormal_dict.keys()
        # 		exception_dict={}
        #
        # 		if os.path.exists(os.path.join(os.path.dirname(__file__),'log\\monkey_bak.log')):
        # 			with open(os.path.join(os.path.dirname(__file__),'log\\monkey_bak.log')) as f_bak_r:
        # 				for line_no,line_content in enumerate(f_bak_r):
        # 					for exception in exception_list:
        # 						if exception in line_content:
        # 							logging.info('异常行号为:{} 异常字段为:{} 异常行详细为:{}'.format(line_no+1,exception,line_content))
        # 							exception_dict[line_no+1]=line_content.strip()
        # 							exception_flag_detail.append('异常行号为:{} 异常字段为:{} 异常行详细为:{}'.format(line_no+1,exception,line_content))
        # 				logging.info('monkey异常集合为:{}'.format(exception_dict).encode(str_encode))
                        # for k,v in exception_dict.iteritems():
                        # 	f_bak_r.seek(0)
                        # 	if 'Reason:' in f_bak_r.readlines()[k+1]:
                        # 		f_bak_r.seek(0)
                        # 		logging.info('行号:{} 异常原因：{}'.format(k,f_bak_r.readlines()[k+1]))
                        # 		exception_flag_reason.append('行号:{} 异常原因：{}'.format(k,f_bak_r.readlines()[k+1]))

        # if len(exception_flag_detail)>0 or len(exception_flag_reason)>0:
        # 	exception_flag='异常发生的界面:{} 异常原因:{}'.format(exception_flag_detail,exception_flag_reason).encode(str_encode)
        # else:
        # 	exception_flag='未分析到异常界面及原因!'

        #获取设备信息
        p1=GetDeviceInfo()
        app_version=p1.getAppVersion(device_name,packapgename)
        module=get_deviceModel(device_name)

        headings_title = [u'测试包名',u'软件版本号',u'设备型号',u'设备序列号',u'遍历事件总数',u'实际提取事件总数',u'遍历Activiy总数',u'是否检查到异常']

        headings_info = [u'遍历Activity名称',u'遍历Event总数', u'Event总数占比',u'Event类型',u'Event类型数占比',u'Event动作',u'Event动作数占比']

        #计算每个actvity事件数占比，actvity事件数/实际提取事件总数
        events_count_percent_list=[]
        for percent in events_count_list:
            percent='%.3f%%'%(float(percent)/len(events_dict)*100)
            events_count_percent_list.append(percent)

        #匹配事件类型与事件动作正则表达式
        event_action_re_mode=re.compile(r'.*?\[\' (.*) \((.*)\)')
        event_list=[]    #存事件详细
        event_type_list=[]  #存事件类型

        events_type_list=[]   #存放所有activity下的事件类型
        events_actions_list=[]   #存放所有activity下所有事件类型->动作列表
        events_types_percents_list=[]   #存所有activity事件下占比列表
        events_actions_percents_list=[]   #存所有事件动作占比列表


        for k,v in events_data_dict.items():
            #对每个activity包含的所有事件数据进行处理
            for i in str(v).split(','):
                event=event_action_re_mode.findall(i)[0]
                event_list.append(event)
                event_type_list.append(event[0])

            event_type_percent_list=[]  #存事件类型占比
            event_action_percent_list=[]  #存事件动作占比

            for value in Counter(event_type_list).values():
                percent='%.3f%%'%(float(value)/sum(Counter(event_type_list).values())*100)
                event_type_percent_list.append(percent)

            events_type_list.append(str(Counter(event_type_list).items()))
            events_types_percents_list.append(str(event_type_percent_list))

            temp=[]   #临时列表，对类型进行排序，经过特殊处理后的事件数据
            for k,v in Counter(event_list).items():
                t="{}->{}".format(str(k).strip('\(').strip('\)').replace(',',':').replace('\'',''),v)
                temp.append(t)
            # for i in sorted(temp):
            # 	print i
            # print
            # events_actions_list.append(str(sorted(temp)))   #将排序后的事件类型添加到新列表集合中
            events_actions_list.append(str(Counter(event_list).items()))   #将事件动作存放新列表中

            for value in Counter(event_list).values():
                percent='%.3f%%'%(float(value)/sum(Counter(event_list).values())*100)
                event_action_percent_list.append(percent)

            events_actions_percents_list.append(str(event_action_percent_list))

        print "*"*50+'\n'
        print events_actions_list
        print events_type_list
        print "*"*50+'\n'

        data_title=[[packapgename],[app_version],[module],[device_name],[count],[len(events_dict)],[len(events_count_dict)],[str(abnormal_flag)],[str(exception_flag)]]   #统计项

        data_info=[activity_list,events_count_list,events_count_percent_list,events_type_list,events_types_percents_list,events_actions_list,events_actions_percents_list]   #详细列表

        worksheet.write('A2', headings_title[0], format_title)
        worksheet.write('A3', headings_title[1], format_title)
        worksheet.write('A4', headings_title[2], format_title)
        worksheet.write('A5', headings_title[3], format_title)

        worksheet.merge_range('D2:E2',headings_title[4],format_title)
        worksheet.merge_range('D3:E3',headings_title[5],format_title)
        worksheet.merge_range('D4:E4',headings_title[6],format_title)
        worksheet.merge_range('D5:E5',headings_title[7],format_title)


        worksheet.merge_range('B2:C2',data_title[0][0],format_content)
        worksheet.merge_range('B3:C3',data_title[1][0],format_content)
        worksheet.merge_range('B4:C4',data_title[2][0],format_content)
        worksheet.merge_range('B5:C5',data_title[3][0],format_content)


        worksheet.merge_range('F2:G2',data_title[4][0],format_content)
        worksheet.merge_range('F3:G3',data_title[5][0],format_content)
        worksheet.merge_range('F4:G4',data_title[6][0],format_content)
        worksheet.merge_range('F5:G5',data_title[7][0],format_content)

        worksheet.write_row('A9', headings_info, format_title)
        worksheet.write_column('A10', data_info[0], format_content_no_border)
        worksheet.write_column('B10', data_info[1], format_content_no_border)
        worksheet.write_column('C10', data_info[2], format_content_no_border)
        worksheet.write_column('D10', data_info[3], format_content_left)
        worksheet.write_column('E10', data_info[4], format_content_left)
        worksheet.write_column('F10', data_info[5], format_content_left)
        worksheet.write_column('G10', data_info[6], format_content_left)


        worksheet2.merge_range('A2:F2','Activity名称',format_title)
        worksheet2.merge_range('G2:K2','对应截图信息',format_title)

        worksheet3.merge_range('A2:F2','遍历事件总数',format_title)
        worksheet3.merge_range('A3:F3','实际提取事件总数',format_title)
        worksheet3.merge_range('A4:F4','遍历Activiy总数',format_title)
        worksheet3.merge_range('A5:F5','是否检查到异常',format_title)
        worksheet3.merge_range('A6:F6','异常详细',format_title)

        worksheet3.merge_range('G2:K2',data_title[4][0],format_content)
        worksheet3.merge_range('G3:K3',data_title[5][0],format_content)
        worksheet3.merge_range('G4:K4',data_title[6][0],format_content)
        worksheet3.merge_range('G5:K5',data_title[7][0],format_content)
        worksheet3.merge_range('G6:K6',data_title[8][0],format_Exceptions_green)

        worksheet3.merge_range('A9:F9','Activity名称',format_title)
        worksheet3.merge_range('G9:K9','事件数',format_title)

        #插入截图到worksheet2中
        activity_list_no_packagename=[]  #用于存储不含包名的activity

        for activity in activity_list:
            activity_=activity.split('/')[-1].strip()
            try:
                if '(' in activity_ and ')' in activity_:
                            activity_=activity_.split(' (')[0]  #防止从monkey提取出来的activity包含 (has extras)等字样
            except Exception as e:
                logging.info('去除has extras字样出现异常:{}'.format(e))

            activity_list_no_packagename.append(activity_)

        #输出去掉包名的activity列表
        print activity_list_no_packagename
        activity_list_no_packagename_len=len(activity_list_no_packagename)
        if activity_list_no_packagename_len>0:
            for i in xrange(activity_list_no_packagename_len):
                if i==0:
                    worksheet2.merge_range('A{}:F{}'.format(3,30*(i+1)+1),activity_list_no_packagename[i],format_screenshot_activity)
                    if activity_list_no_packagename[i]+'.jpg' in os.listdir(os.path.join(os.path.dirname(__file__),'screenshot_result')):
                        worksheet2.insert_image('G3', './screenshot_result/{}.jpg'.format(activity_list_no_packagename[i]),{'x_scale': 0.3, 'y_scale': 0.3})
                    else:
                        worksheet2.merge_range('G{}:K{}'.format(3,30*(i+1)+1),u'暂无截图信息',format_screenshot_activity_red)
                else:
                    worksheet2.merge_range('A{}:F{}'.format(30*i+2,30*(i+1)+1),activity_list_no_packagename[i],format_screenshot_activity)

                    if activity_list_no_packagename[i]+'.jpg' in os.listdir(os.path.join(os.path.dirname(__file__),'screenshot_result')):
                        worksheet2.insert_image('G{}'.format(30*i+2), './screenshot_result/{}.jpg'.format(activity_list_no_packagename[i]),{'x_scale': 0.3, 'y_scale': 0.3})
                    else:
                        worksheet2.merge_range('G{}:K{}'.format(30*i+2,30*(i+1)+1),u'暂无截图信息',format_screenshot_activity_red)

        #表3，activity覆盖排名数据生成

        events_count_dict_bak={}
        for k,v in events_count_dict.items():
            events_count_dict_bak[k]=sum(v)
        print events_count_dict_bak
        activity_reverse_list = sorted(events_count_dict_bak.items(), key=lambda events_count_dict_bak:events_count_dict_bak[1],reverse=True)   #按照字典中的value值大小进行降序排列

        activitys=[]
        keys=[]
        for i in activity_reverse_list:
            try:
                if '(' in i[0] and ')' in i[0]:
                    activity_els=i[0].split(' (')[0]  #防止从monkey提取出来的activity包含 (has extras)等字样
                    activitys.append(activity_els)   #提取排序后的activtiy
                else:
                    activitys.append(i[0])

            except Exception as e:
                logging.info('取出排序后的activity出现异常{}'.format(e))
            keys.append(i[1])        #提取对应activiy事件数
        data_info3=[activitys,keys]
        for line in xrange(len(activitys)):
            worksheet3.merge_range('A{}:F{}'.format(line+10,line+10), data_info3[0][line], format_content)
            worksheet3.merge_range('G{}:K{}'.format(line+10,line+10), data_info3[1][line], format_content)

        #生成饼状图

        chart = self.workbook.add_chart({'type': 'pie'})
        lines=len(activitys)

        #如果activity数小于等于5，则全部生成饼状图，如果大于5，则只取前5条生成
        if 0<lines<=5:
            chart.add_series({
                'categories': '=Monkey测试报告汇总!$A$10:$A${}'.format(lines+9),
                'values':     '=Monkey测试报告汇总!$G$10:$G${}'.format(lines+9),
            })
        elif lines>5:
            chart.add_series({
                'categories': '=Monkey测试报告汇总!$A$10:$A$14',
                'values':     '=Monkey测试报告汇总!$G$10:$G$14',
            })


        chart.set_title ({'name': 'Activity事件覆盖占比饼状图'})

        worksheet3.insert_chart('M2', chart, {'x_offset': 25, 'y_offset': 10})

        #关闭表
        try:
            logging.info('start ready close workbook...')
            #self.workbook._store_workbook()
            #logging.info('保存成功！！')
            for x in xrange(3):
                    logging.info('close ResultReport workbook 倒计时 {} sec'.format(3-x).encode(str_encode))
                    time.sleep(1)
            self.workbook.close()
            logging.info('close workbook success...')
        except Exception,e:
            # traceback.print_exc()
            logging.info(e)
            for x in xrange(1,4):
                    logging.info('Close ResultReport retry {}'.format(x).encode(str_encode))
                    try:
                        self.workbook.close()
                        #self.gen_monkey_report()
                        logging.info("第{}次重试关闭成功,并报告生成完成!".format(x).encode(str_encode))
                        break
                    except Exception, ee:
                        logging.info(ee)
                        logging.info("关闭时出现异常，重试{}次完毕!".format(x).encode(str_encode))
        else:
            logging.info("报告生成完成!".encode(str_encode))



class ResultReportException(object):
    def __init__(self):
        logging.info('设备异常中断，开始收集已获取到的信息，并准备生成报告！'.encode(str_encode))
        creat_time=time.strftime("%Y_%m_%d_%H_%M_%S")
        report_name='Monkey测试结果报告_{}'.format(creat_time).decode('utf-8').encode('gbk')
        report_name=os.path.join(os.path.dirname(__file__),'{}.xlsx'.format(report_name))
        self.workbook = xlsxwriter.Workbook(report_name)

        if os.path.exists(os.path.join(os.path.dirname(__file__),'screenshot_result')):
            try:
                logging.info('截图目录存在!'.encode(str_encode))
            except WindowsError:
                pass
        else:
            pass
        if os.path.exists(os.path.join(os.path.dirname(__file__),'log')):
            try:
                logging.info('log目录存在!'.encode(str_encode))
            except WindowsError:
                pass
        else:
            logging.info('log目录不存在，准备退出应用!'.encode(str_encode))
            sys.exit(0)

    def gen_monkey_report(self):
        global count
        try:
            count,events_dict,events_data_dict,events_count_dict,abnormal_dict,abnormal_dict_2=anlayzeDataException(device_name,packapgename,count,throttle)
        except Exception as e:
            logging.info(e)

        worksheet3 = self.workbook.add_worksheet('Monkey测试报告汇总')
        worksheet4 = self.workbook.add_worksheet('异常明细表')
        worksheet = self.workbook.add_worksheet('Monkey测试报告详细')
        worksheet2 = self.workbook.add_worksheet('Activity截图信息')

        activity_list=[]   #用于存放activity列表
        events_count_list=[]   #用于存放各个activity列表对应的事件总数
        for k,v in events_count_dict.items():
            try:
                if '(' in k and ')' in k:
                        k=k.split(' (')[0]  #防止从monkey提取出来的activity包含 (has extras)等字样
            except Exception as e:
                logging.info('从activity中去除has extras字样出现异常:{}'.format(e))

            activity_list.append(k)
            events_count_list.append(sum(v))

        worksheet.set_column('A:A',len(activity_list[-1])+7)  #设置A列列宽
        worksheet.set_column('B:G',len(str(count))+14)  #设置B:G列列宽
        worksheet.set_column('F:F',len(str(count))+25)

        #创建图表字体样式
        format_title=self.workbook.add_format()    #设置title和content样式
        format_head=self.workbook.add_format()
        format_title_yellew=self.workbook.add_format()
        format_content=self.workbook.add_format()
        format_content_no_border=self.workbook.add_format()

        format_content_left=self.workbook.add_format()
        format_content_left_border=self.workbook.add_format()

        format_screenshot_activity=self.workbook.add_format()
        format_screenshot_activity_red=self.workbook.add_format()
        format_Exceptions_red=self.workbook.add_format()

        format_Exceptions_green=self.workbook.add_format()

        #根据条件，如包括高、大则标红色
        worksheet.conditional_format('F5:G5', {'type':     'text',
                                       'criteria': 'not containing',
                                       'value':    '未检查到异常',
                                      'format':   format_Exceptions_red})

        worksheet3.conditional_format('G5:K5', {'type':     'text',
                                       'criteria': 'not containing',
                                       'value':    '未检查到异常',
                                      'format':   format_Exceptions_red})

        format_Exceptions_red.set_align('center')
        format_Exceptions_red.set_font(u'微软雅黑')
        format_Exceptions_red.set_font_size(11)
        format_Exceptions_red.set_font_color('#FF0000')
        format_Exceptions_red.set_text_wrap()    #自动换行
        format_Exceptions_red.set_align('center')  #水平居中
        format_Exceptions_red.set_align('vcenter')  #垂直居中
        format_Exceptions_red.set_border(1)

        format_Exceptions_green.set_align('center')
        format_Exceptions_green.set_font(u'微软雅黑')
        format_Exceptions_green.set_font_size(11)
        format_Exceptions_green.set_font_color('#00B050')
        format_Exceptions_green.set_text_wrap()    #自动换行
        format_Exceptions_green.set_align('center')  #水平居中
        format_Exceptions_green.set_align('vcenter')  #垂直居中
        format_Exceptions_green.set_border(1)

        format_title.set_border(1)
        format_title.set_font_size(12)
        format_title.set_align('center')
        format_title.set_bg_color('#cccccc')
        format_title.set_font(u'微软雅黑')
        format_title.set_text_wrap()    #自动换行
        format_title.set_align('center')  #水平居中
        format_title.set_align('vcenter')  #垂直居中

        format_title_yellew.set_border(1)
        format_title_yellew.set_bold()
        format_title_yellew.set_font_size(12)
        format_title_yellew.set_align('center')
        format_title_yellew.set_bg_color('#FFFF00')
        format_title_yellew.set_font(u'微软雅黑')
        format_title_yellew.set_text_wrap()    #自动换行
        format_title_yellew.set_align('center')  #水平居中
        format_title_yellew.set_align('vcenter')  #垂直居中


        format_head.set_bold(1)  #加粗
        format_head.set_border(1)
        format_head.set_font_size(20)
        format_head.set_text_wrap()    #自动换行
        format_head.set_align('center')  #水平居中
        format_head.set_align('vcenter')  #垂直居中
        format_head.set_font(u'微软雅黑')


        format_screenshot_activity.set_bold(1)  #加粗
        format_screenshot_activity.set_border(1)
        format_screenshot_activity.set_font_size(15)
        format_screenshot_activity.set_text_wrap()    #自动换行
        format_screenshot_activity.set_align('center')  #水平居中
        format_screenshot_activity.set_align('vcenter')  #垂直居中
        format_screenshot_activity.set_font(u'微软雅黑')


        format_screenshot_activity_red.set_bold(1)  #加粗
        format_screenshot_activity_red.set_border(1)
        format_screenshot_activity_red.set_font_size(15)
        format_screenshot_activity_red.set_text_wrap()    #自动换行
        format_screenshot_activity_red.set_align('center')  #水平居中
        format_screenshot_activity_red.set_align('vcenter')  #垂直居中
        format_screenshot_activity_red.set_font(u'微软雅黑')
        format_screenshot_activity_red.set_font_color('#FF0000')

        format_content.set_border(1)
        format_content.set_align('center')
        format_content.set_font(u'微软雅黑')
        format_content.set_font_size(11)
        format_content.set_text_wrap()    #自动换行
        format_content.set_align('center')  #水平居中
        format_content.set_align('vcenter')  #垂直居中

        format_content_no_border.set_align('center')
        format_content_no_border.set_align('vcenter')
        format_content_no_border.set_font(u'微软雅黑')
        format_content_no_border.set_font_size(11)
        format_content_no_border.set_text_wrap()    #自动换行

        format_content_left.set_align('left')
        format_content_left.set_align('vcenter')
        format_content_left.set_font(u'微软雅黑')
        format_content_left.set_font_size(11)
        format_content_left.set_text_wrap()    #自动换行

        format_content_left_border.set_align('left')
        format_content_left_border.set_align('vcenter')
        format_content_left_border.set_font(u'微软雅黑')
        format_content_left_border.set_font_size(11)
        format_content_left_border.set_text_wrap()    #自动换行
        format_content_left_border.set_border()


        worksheet.set_row(0,36)   #设置第一行，行高为36
        worksheet.merge_range('A1:G1',u'Monkey随机测试覆盖activti及事件类型详细统计',format_head)
        worksheet2.set_row(0,36)   #设置第一行，行高为36
        worksheet2.merge_range('A1:K1',u'Activity与界面截图对应表（仅供参考）',format_head)
        worksheet3.set_row(0,36)   #设置第一行，行高为36
        worksheet3.merge_range('A1:K1',u'Monkey随机事件覆盖测试汇总概况',format_head)

        worksheet4.set_row(0,36)   #设置第一行，行高为36
        worksheet4.merge_range('A1:D1',u'日志异常明细表',format_head)

        worksheet4.set_column('A1:C1',22)
        worksheet4.set_column('D1:D1',120)

        worksheet3.set_row(4,72)
        worksheet3.set_row(5,72)   #设置第5\6行，行高为50

        #设置表4，从第三行起，前一百行，行高为30px
        for col in xrange(100):
            worksheet4.set_row(2+col,30)

        #表4，异常明细表
        title=['错误类别','出现次数','所属分析器','异常日志明细']
        worksheet4.write_row('A2',title,format_title_yellew)
        logcat_exception_dict=anlayzeLogcatLog(os.path.join(os.path.join(os.path.dirname(__file__),'log'),'app_error.log'))

        global excel_lineon
        excel_lineon=3
        #汇总表中，判断是否检查到异常逻辑
        if len(abnormal_dict)>0 or len(abnormal_dict_2)>0 or len(logcat_exception_dict)>0:
            abnormal_flag='存在异常!'
            exception_flag='异常个数:{}'.format(len(abnormal_dict)+len(abnormal_dict_2)+len(logcat_exception_dict))
            if len(logcat_exception_dict)>0:
                logging.info('logcat error插入异常起始行号为:{}'.format(excel_lineon).encode(str_encode))
                for key,value in logcat_exception_dict.iteritems():
                    if len(key)==2:
                        worksheet4.write('A{}'.format(excel_lineon),key[0],format_content)
                        worksheet4.write('B{}'.format(excel_lineon),value,format_content)
                        worksheet4.write('C{}'.format(excel_lineon),'logcat error',format_content)
                        worksheet4.write('D{}'.format(excel_lineon),key[1],format_content_left_border)
                        excel_lineon+=1
            if len(abnormal_dict)>0:
                excel_lineon=excel_lineon
                logging.info('monkey log插入异常起始行号为:{}'.format(excel_lineon).encode(str_encode))
                for key,value in abnormal_dict.iteritems():
                    if len(value)==2 and isinstance(value[0],(list,tuple)):
                        worksheet4.write('A{}'.format(excel_lineon),key,format_content)
                        worksheet4.write('B{}'.format(excel_lineon),value[0][-1],format_content)
                        worksheet4.write('C{}'.format(excel_lineon),'monkey',format_content)
                        worksheet4.write('D{}'.format(excel_lineon),str(value),format_content_left_border)
                        excel_lineon+=1
            if len(abnormal_dict_2)>0:
                excel_lineon=excel_lineon
                logging.info('logcat log插入异常起始行号为:{}'.format(excel_lineon).encode(str_encode))
                for key,value in abnormal_dict_2.iteritems():
                    if len(value)==2 and isinstance(value[0],(list,tuple)):
                        worksheet4.write('A{}'.format(excel_lineon),key,format_content)
                        worksheet4.write('B{}'.format(excel_lineon),value[0][-1],format_content)
                        worksheet4.write('C{}'.format(excel_lineon),'logcat log',format_content)
                        worksheet4.write('D{}'.format(excel_lineon),str(value),format_content_left_border)
                        excel_lineon+=1
        else:
            abnormal_flag='未检查到异常'
            exception_flag='未分析到异常界面及原因!'

        # exception_flag_detail=[]
        # exception_flag_reason=[]
        # if len(abnormal_dict)>0:
        # #分析monkey行为日志
        # 	if system is 'Windows':
        # 		with open(os.path.join(os.path.dirname(__file__),'log\\monkey.log'),'rb') as f_r:
        # 			with open(os.path.join(os.path.dirname(__file__),'log\\monkey_bak.log'),'wb') as f_w:
        # 				for eachline in f_r.readlines():
        # 					f_w.write(eachline.strip()+'\n')   #删除空白行
        # 		logging.info('检查到monkey异常个数为:{}'.format(len(abnormal_dict)))
        # 		exception_list=abnormal_dict.keys()
        # 		exception_dict={}
        #
        # 		if os.path.exists(os.path.join(os.path.dirname(__file__),'log\\monkey_bak.log')):
        # 			with open(os.path.join(os.path.dirname(__file__),'log\\monkey_bak.log')) as f_bak_r:
        # 				for line_no,line_content in enumerate(f_bak_r):
        # 					for exception in exception_list:
        # 						if exception in line_content:
        # 							logging.info('异常行号为:{} 异常字段为:{} 异常行详细为:{}'.format(line_no+1,exception,line_content))
        # 							exception_dict[line_no+1]=line_content.strip()
        # 							exception_flag_detail.append('异常行号为:{} 异常字段为:{} 异常行详细为:{}'.format(line_no+1,exception,line_content))
        # 				logging.info('monkey异常集合为:{}'.format(exception_dict).encode(str_encode))
                        # for k,v in exception_dict.iteritems():
                        # 	f_bak_r.seek(0)
                        # 	if 'Reason:' in f_bak_r.readlines()[k+1]:
                        # 		f_bak_r.seek(0)
                        # 		logging.info('行号:{} 异常原因：{}'.format(k,f_bak_r.readlines()[k+1]))
                        # 		exception_flag_reason.append('行号:{} 异常原因：{}'.format(k,f_bak_r.readlines()[k+1]))

        # if len(exception_flag_detail)>0 or len(exception_flag_reason)>0:
        # 	exception_flag='异常发生的界面:{} 异常原因:{}'.format(exception_flag_detail,exception_flag_reason).encode(str_encode)
        # else:
        # 	exception_flag='未分析到异常界面及原因!'

        #获取设备信息
        p1=GetDeviceInfo()
        app_version=p1.getAppVersion(device_name,packapgename)
        module=get_deviceModel(device_name)

        headings_title = [u'测试包名',u'软件版本号',u'设备型号',u'设备序列号',u'遍历事件总数',u'实际提取事件总数',u'遍历Activiy总数',u'是否检查到异常']

        headings_info = [u'遍历Activity名称',u'遍历Event总数', u'Event总数占比',u'Event类型',u'Event类型数占比',u'Event动作',u'Event动作数占比']

        #计算每个actvity事件数占比，actvity事件数/实际提取事件总数
        events_count_percent_list=[]
        for percent in events_count_list:
            percent='%.3f%%'%(float(percent)/len(events_dict)*100)
            events_count_percent_list.append(percent)

        #匹配事件类型与事件动作正则表达式
        event_action_re_mode=re.compile(r'.*?\[\' (.*) \((.*)\)')
        event_list=[]    #存事件详细
        event_type_list=[]  #存事件类型

        events_type_list=[]   #存放所有activity下的事件类型
        events_actions_list=[]   #存放所有activity下所有事件类型->动作列表
        events_types_percents_list=[]   #存所有activity事件下占比列表
        events_actions_percents_list=[]   #存所有事件动作占比列表


        for k,v in events_data_dict.items():
            # print k,'=====>',v

            #对每个activity包含的所有事件数据进行处理
            for i in str(v).split(','):
                event=event_action_re_mode.findall(i)[0]
                event_list.append(event)
                event_type_list.append(event[0])

            event_type_percent_list=[]  #存事件类型占比
            event_action_percent_list=[]  #存事件动作占比

            for value in Counter(event_type_list).values():
                percent='%.3f%%'%(float(value)/sum(Counter(event_type_list).values())*100)
                event_type_percent_list.append(percent)



            events_type_list.append(str(Counter(event_type_list).items()))
            events_types_percents_list.append(str(event_type_percent_list))

            temp=[]   #临时列表，对类型进行排序，经过特殊处理后的事件数据
            for k,v in Counter(event_list).items():
                t="{}->{}".format(str(k).strip('\(').strip('\)').replace(',',':').replace('\'',''),v)
                temp.append(t)
            # for i in sorted(temp):
            # 	print i
            # print
            # events_actions_list.append(str(sorted(temp)))   #将排序后的事件类型添加到新列表集合中
            events_actions_list.append(str(Counter(event_list).items()))   #将事件动作存放新列表中

            for value in Counter(event_list).values():
                percent='%.3f%%'%(float(value)/sum(Counter(event_list).values())*100)
                event_action_percent_list.append(percent)

            events_actions_percents_list.append(str(event_action_percent_list))


        data_title=[[packapgename],[app_version],[module],[device_name],[count],[len(events_dict)],[len(events_count_dict)],[str(abnormal_flag)],[str(exception_flag)]]   #统计项

        data_info=[activity_list,events_count_list,events_count_percent_list,events_type_list,events_types_percents_list,events_actions_list,events_actions_percents_list]   #详细列表

        worksheet.write('A2', headings_title[0], format_title)
        worksheet.write('A3', headings_title[1], format_title)
        worksheet.write('A4', headings_title[2], format_title)
        worksheet.write('A5', headings_title[3], format_title)

        worksheet.merge_range('D2:E2',headings_title[4],format_title)
        worksheet.merge_range('D3:E3',headings_title[5],format_title)
        worksheet.merge_range('D4:E4',headings_title[6],format_title)
        worksheet.merge_range('D5:E5',headings_title[7],format_title)


        worksheet.merge_range('B2:C2',data_title[0][0],format_content)
        worksheet.merge_range('B3:C3',data_title[1][0],format_content)
        worksheet.merge_range('B4:C4',data_title[2][0],format_content)
        worksheet.merge_range('B5:C5',data_title[3][0],format_content)


        worksheet.merge_range('F2:G2',data_title[4][0],format_content)
        worksheet.merge_range('F3:G3',data_title[5][0],format_content)
        worksheet.merge_range('F4:G4',data_title[6][0],format_content)
        worksheet.merge_range('F5:G5',data_title[7][0],format_content)

        worksheet.write_row('A9', headings_info, format_title)
        worksheet.write_column('A10', data_info[0], format_content_no_border)
        worksheet.write_column('B10', data_info[1], format_content_no_border)
        worksheet.write_column('C10', data_info[2], format_content_no_border)
        worksheet.write_column('D10', data_info[3], format_content_left)
        worksheet.write_column('E10', data_info[4], format_content_left)
        worksheet.write_column('F10', data_info[5], format_content_left)
        worksheet.write_column('G10', data_info[6], format_content_left)


        worksheet2.merge_range('A2:F2','Activity名称',format_title)
        worksheet2.merge_range('G2:K2','对应截图信息',format_title)

        worksheet3.merge_range('A2:F2','遍历事件总数',format_title)
        worksheet3.merge_range('A3:F3','实际提取事件总数',format_title)
        worksheet3.merge_range('A4:F4','遍历Activiy总数',format_title)
        worksheet3.merge_range('A5:F5','是否检查到异常',format_title)
        worksheet3.merge_range('A6:F6','异常详细',format_title)

        worksheet3.merge_range('G2:K2',data_title[4][0],format_content)
        worksheet3.merge_range('G3:K3',data_title[5][0],format_content)
        worksheet3.merge_range('G4:K4',data_title[6][0],format_content)
        worksheet3.merge_range('G5:K5',data_title[7][0],format_content)
        worksheet3.merge_range('G6:K6',data_title[8][0],format_Exceptions_green)

        worksheet3.merge_range('A9:F9','Activity名称',format_title)
        worksheet3.merge_range('G9:K9','事件数',format_title)

        #插入截图到worksheet2中
        activity_list_no_packagename=[]  #用于存储不含包名的activity

        for activity in activity_list:
            activity_=activity.split('/')[-1].strip()
            try:
                if '(' in activity_ and ')' in activity_:
                            activity_=activity_.split(' (')[0]  #防止从monkey提取出来的activity包含 (has extras)等字样
            except Exception as e:
                logging.info('去除has extras字样出现异常:{}'.format(e))

            activity_list_no_packagename.append(activity_)

        #输出去掉包名的activity列表
        print activity_list_no_packagename
        activity_list_no_packagename_len=len(activity_list_no_packagename)
        if activity_list_no_packagename_len>0:
            for i in xrange(activity_list_no_packagename_len):
                if i==0:
                    worksheet2.merge_range('A{}:F{}'.format(3,30*(i+1)+1),activity_list_no_packagename[i],format_screenshot_activity)
                    if activity_list_no_packagename[i]+'.jpg' in os.listdir(os.path.join(os.path.dirname(__file__),'screenshot_result')):
                        worksheet2.insert_image('G3', './screenshot_result/{}.jpg'.format(activity_list_no_packagename[i]),{'x_scale': 0.3, 'y_scale': 0.3})
                    else:
                        worksheet2.merge_range('G{}:K{}'.format(3,30*(i+1)+1),u'暂无截图信息',format_screenshot_activity_red)
                else:
                    worksheet2.merge_range('A{}:F{}'.format(30*i+2,30*(i+1)+1),activity_list_no_packagename[i],format_screenshot_activity)

                    if activity_list_no_packagename[i]+'.jpg' in os.listdir(os.path.join(os.path.dirname(__file__),'screenshot_result')):
                        worksheet2.insert_image('G{}'.format(30*i+2), './screenshot_result/{}.jpg'.format(activity_list_no_packagename[i]),{'x_scale': 0.3, 'y_scale': 0.3})
                    else:
                        worksheet2.merge_range('G{}:K{}'.format(30*i+2,30*(i+1)+1),u'暂无截图信息',format_screenshot_activity_red)

        #表3，activity覆盖排名数据生成

        events_count_dict_bak={}
        for k,v in events_count_dict.items():
            events_count_dict_bak[k]=sum(v)
        activity_reverse_list = sorted(events_count_dict_bak.items(), key=lambda events_count_dict_bak:events_count_dict_bak[1],reverse=True)   #按照字典中的value值大小进行降序排列

        activitys=[]
        keys=[]

        for i in activity_reverse_list:
            try:
                if '(' in i[0] and ')' in i[0]:
                    activity_els=i[0].split(' (')[0]  #防止从monkey提取出来的activity包含 (has extras)等字样
                    activitys.append(activity_els)   #提取排序后的activtiy
                else:
                    activitys.append(i[0])

            except Exception as e:
                logging.info('取出排序后的activity出现异常{}'.format(e))
            keys.append(i[1])        #提取对应activiy事件数
        # print '==========2',activitys
        data_info3=[activitys,keys]
        for line in xrange(len(activitys)):
            worksheet3.merge_range('A{}:F{}'.format(line+10,line+10), data_info3[0][line], format_content)
            worksheet3.merge_range('G{}:K{}'.format(line+10,line+10), data_info3[1][line], format_content)

        #生成饼状图

        chart = self.workbook.add_chart({'type': 'pie'})
        lines=len(activitys)

        #如果activity数小于等于5，则全部生成饼状图，如果大于5，则只取前5条生成
        if 0<lines<=5:
            chart.add_series({
                'categories': '=Monkey测试报告汇总!$A$10:$A${}'.format(lines+9),
                'values':     '=Monkey测试报告汇总!$G$10:$G${}'.format(lines+9),
            })
        elif lines>5:
            chart.add_series({
                'categories': '=Monkey测试报告汇总!$A$10:$A$14',
                'values':     '=Monkey测试报告汇总!$G$10:$G$14',
            })


        chart.set_title ({'name': 'Activity事件覆盖占比饼状图'})

        worksheet3.insert_chart('M2', chart, {'x_offset': 25, 'y_offset': 10})

        #关闭表
        try:
            logging.info('start ready close workbook...')
            for x in xrange(3):
                    logging.info('close ResultReportException workbook 倒计时 {} sec'.format(3-x).encode(str_encode))
                    time.sleep(1)
            self.workbook.close()
            logging.info('close workbook success...')
        except Exception,e:
            # traceback.print_exc()
            logging.info(e)
            logging.info("关闭时出现异常，请查看报告是否成功!".encode(str_encode))


        else:
            logging.info("报告生成完成!".encode(str_encode))



def quit(signum,frame):
    logging.info('您强制中止程序!开始中止采集！！'.encode(str_encode))
    # os.popen('taskkill /f /pid {}'.format(os.getpid()))
    os.kill(os.getpid(),signal.SIGTERM)
    logging.info('中止成功！！'.encode(str_encode))
    sys.exit()

def check_device_status(device_name):
        while 1:
            time.sleep(3)
            device=os.popen('adb devices')
            device_info=device.read()
            #如果通过os.popen获取内容为空，则使用subprocess.Popen方法获取
            if len(device_info)==0:
                device=subprocess.Popen('adb devices',shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                device_info=device.stdout.read()
            serino=device_info.strip('List of devices attached').split()

            if device_name in serino[::2]:   #判断指定设备是否在返回的设备列表中
                index=serino[::2].index(device_name)
                if serino[1::2][index]=='device':   #如果设备存在，获取索引号，通过引号，去取设备当前状态，如果为device则为在线
                    pass
                else:
                    logging.info('adb devices==>{}\n serino==>{}'.format(device_info,serino))
                    logging.info('当前设备{}，状态为:{},所有设备状态列表为:{}'.format(device_name,serino[1::2][index],serino[1::2]).encode(str_encode))
                    if system is 'Windows':
                        logging.info('亲，当前测试设备【{}】状态不在线，状态为：{}，请检查!\n'.encode(str_encode).format(device_name,serino[1::2][index]))
                        p=ResultReportException()
                        p.gen_monkey_report()   #生成报告
                        os.popen('taskkill /f /pid {}'.format(os.getpid()))

                        sys.exit()
                    else:
                        logging.info('亲，当前测试设备【{}】状态不在线,状态为:{}，请检查!\n'.encode(str_encode).format(device_name,serino[1::2][index]))
                        p=ResultReportException()
                        p.gen_monkey_report()   #生成报告
                        os.popen('kill -9 {}'.format(os.getpid()))
                        sys.exit()
            else:
                logging.info('adb devices==>{}\n serino==>{}'.format(device_info,serino))
                logging.info('当前设备名为:{},所有设备列表为:{}'.format(device_name,serino[::2]).encode(str_encode))
                if system is 'Windows':
                    logging.info('亲，当前测试设备【{}】未连接或已断开，请检查！\n'.encode('gbk').format(device_name))
                    p=ResultReportException()
                    p.gen_monkey_report()   #生成报告
                    os.popen('taskkill /f /pid {}'.format(os.getpid()))

                    sys.exit()

                else:
                    logging.info('亲，当前测试设备【{}】未连接或已断开，请检查！\n'.format(device_name))
                    p=ResultReportException()
                    p.gen_monkey_report()   #生成报告
                    os.popen('kill -9 {}'.format(os.getpid()))
                    sys.exit()

#主方法入口
def main():
    logging.info('开始执行程序...'.encode(str_encode))
    try:
        platformVersion=get_platformVersion(device_name)   #获取设备版本
        deviceModel=get_deviceModel(device_name)    #获取设备型号
    except Exception:
        platformVersion=''
        deviceModel=''
    try:
        device_pix=get_device_pix(device_name)   #获取设备分辨率
    except Exception:
        try:
            device_pix=get_device_display(device_name)
        except:
            device_pix=''
    logging.info('开始获取手机设备信息，系统型号为:{}'.format(deviceModel).encode(str_encode))
    logging.info('开始获取手机设备信息，系统版本号为:{}'.format(platformVersion).encode(str_encode))
    logging.info('开始获取手机设备信息，分辨率为:{}'.format(device_pix).encode(str_encode))
    try:
        logging.info('手机自动亮屏，解锁操作'.encode(str_encode))
        autoLockscreen(device_name)   #手机自动亮屏，解锁
    except Exception:
        pass
    #packapgename=appActivity.split('/')[0]
    #logging.info('packapgename===={}'.format(packapgename))
    startAppActivity_ADB(device_name,appActivity) #启动指定activity
    for x in xrange(5):
        logging.info('App启动，请稍候{} sec'.format(5-x).encode(str_encode))
        time.sleep(1)
    while True:
        logging.info('进入循环'.encode(str_encode))
        try:
            app=appActivity.split('/')[0]
            logging.info('获取到app=====>{}'.format(app).encode(str_encode))
            activity_top_current=get_device_currentActivity(device_name,app)        #判断是否启动待测应用为前置
            logging.info('获取到activity_top_current====>{}'.format(activity_top_current).encode(str_encode))
            activity=activity_top_current.split('/')
            logging.info('获取到activity====>{}'.format(str(activity)).encode(str_encode))
            if activity[-1] in appActivity or activity[0] in appActivity:
                logging.info('指定{}主Activity启动成功!'.format(appActivity).encode(str_encode))
                for x in xrange(3):
                    logging.info('倒计时 {} sec'.format(3-x).encode(str_encode))
                    time.sleep(1)
                break
        except Exception as e:
            logging.info('异常了！！！error:{}'.format(e).encode(str_encode))
            pass
    if switch=='on':
        logging.info('黑名单控制开关已打开，进入uiautomator框架，黑名单基于控件元素定位有效！'.encode(str_encode))
        try:
            thread_blackListActivity(device_name,app,blackUrlList,blackList,activity_top_current,selectElements)   #黑名单功能
        except Exception as e:
            logging.info(e)

        try:
            start_uiautomator(device_name,selectElements)   #引导功能，selectElements==> 基于uiautomator框架查找控件
        except Exception as e:
            logging.info(e)
            logging.info('基于uiautomator框架识别元素控件引导出现异常，切换至boundl相对坐标SelectList方式来执行引导'.encode(str_encode))
            startAppSelectList(device_name,selectList)   #引导功能，selectList=> 基于相对坐标，查找控件
    else:
        logging.info('黑名单控制开关已关闭，进入基于控件元素引导功能！'.encode(str_encode))
        try:
            start_uiautomator(device_name,selectElements)   #引导功能，selectElements==> 基于uiautomator框架查找控件
        except Exception as e:
            logging.info(e)
            logging.info('基于uiautomator框架识别元素控件引导出现异常，切换至boundl相对坐标SelectList方式来执行引导'.encode(str_encode))
            startAppSelectList(device_name,selectList)   #引导功能，selectList=> 基于相对坐标，查找控件

    p=ResultReport()   #monkey执行

    t=threading.Thread(target=p.gen_monkey_report)
    t.setDaemon(True)
    t.start()
    logging.info('开始主逻辑==>方法名为:【gen_monkey_report】线程名为:{}'.format(t.getName()).encode(str_encode))
    t.join()

    logging.info('主逻辑运行完成'.encode(str_encode))

    # p.gen_monkey_report()   #生成报告
    try:
        logging.info('开始关闭App!'.encode(str_encode))
        stopcmd = 'adb -s %s shell am  force-stop %s' %(device_name,app)
        logging.info('使用命令:{}'.format(stopcmd).encode(str_encode))
        os.popen(stopcmd)
        logging.info('关闭App成功!!'.encode(str_encode))
    except Exception as eend:
        logging.info('关闭App失败,原因:{}!'.format(eend).encode(str_encode))
    logging.info('程序运行结束!'.encode(str_encode))
    os.kill(os.getpid(),signal.SIGTERM)

#主程序调用入口
if __name__ == '__main__':
    if os.path.exists(os.path.join(os.path.dirname(__file__),'config.yaml')):
        f = open(os.path.join(os.path.dirname(__file__),'config.yaml'))
        dataMap = yaml.load(f)
        device_ord=dataMap['MonkeyConfig']['device_ord']
        logging.info('读取到device_ord 为 {}'.format(device_ord))
        device_name = getdevices(device_ord)
        #logging.info('str_encode is {}'.format(str_encode))
        logging.info('读取到Device name为{}'.format(device_name).encode(str_encode))
        packapgename=dataMap['MonkeyConfig']['packapgname']
        logging.info('读取到packapgename 为{}'.format(packapgename).encode(str_encode))
        count=dataMap['MonkeyConfig']['count']
        logging.info('读取到count 为{}'.format(count).encode(str_encode))
        exception_list=dataMap['MonkeyConfig']['Exceptions']
        if len(exception_list)>0:
            logging.info('读取到异常关键字{}个分别为'.format(len(exception_list)).encode(str_encode))
            for excp in exception_list:
                logging.info('{}'.format(excp).encode(str_encode))
        appActivity=dataMap['MonkeyConfig']['appActivity']
        logging.info('读取到 appActivity 为{}'.format(appActivity).encode(str_encode))
        throttle=dataMap['MonkeyConfig']['throttle']
        logging.info('读取到 throttle 为{}'.format(throttle).encode(str_encode))
        selectList=dataMap['MonkeyConfig']['selectList']
        selectElements=dataMap['MonkeyConfig']['selectElements']
        blackUrlList=dataMap['MonkeyConfig']['blackUrlList']   #url黑名单
        bulen=len(blackUrlList)
        if bulen>0:
            logging.info('读取到黑名单Activity{}个分别为'.format(bulen).encode(str_encode))
            for blackurl in blackUrlList:
                logging.info('{}'.format(blackurl).encode(str_encode))
        blackList=dataMap['MonkeyConfig']['blackList']     #文本元素黑名单
        blen=len(blackList)
        if blen>0:
            logging.info('读取到黑名单元素文本{}个分别为'.format(blen).encode(str_encode))
            for black in blackList:
                logging.info('{}'.format(black).encode(str_encode))
        switch=dataMap['MonkeyConfig']['switchUiautomator']
        logging.info('读取到 switch 为{}'.format(switch).encode(str_encode))
        pct_touch=dataMap['MonkeyConfig']['pct-touch']
        logging.info('读取到 pct_touch 为{}'.format(pct_touch).encode(str_encode))
        pct_motion=dataMap['MonkeyConfig']['pct-motion']
        logging.info('读取到 pct_motion 为{}'.format(pct_motion).encode(str_encode))
        pct_nav=dataMap['MonkeyConfig']['pct-nav']
        logging.info('读取到 pct_nav 为{}'.format(pct_nav).encode(str_encode))
        pct_majornav=dataMap['MonkeyConfig']['pct-majornav']
        logging.info('读取到 pct_majornav 为{}'.format(pct_majornav).encode(str_encode))
        logLevel=dataMap['MonkeyConfig']['logLevel']
        logging.info('读取到 logLevel 为{}'.format(logLevel).encode(str_encode))
        sleeptimes=3
        for x in xrange(sleeptimes):
            logging.info('倒计时 {} sec'.format(sleeptimes-x).encode(str_encode))
            time.sleep(1)



    else:
        print "config.yaml配置文件不存在!".encode('str_encode')
        exit(0)

    #startAppActivity
    signal.signal(signal.SIGINT,quit)   #中断进程信号(control+c)
    signal.signal(signal.SIGTERM,quit)  #软件终止信号
    ##检查设备运行状态
    t=threading.Thread(target=check_device_status,args=(device_name,))
    t.start()
    ##主函数入口
    main()
    '''
    t2=threading.Thread(target=startAppActivity,args=(device_name,appActivity))
    t2.start()
    logging.info(t2)
    #t1 = check_errorMessage(os.path.join(os.path.join(os.path.dirname(__file__), 'log'), 'monkey.log'), exception_list)
    #logging.info(str(t1))
'''
