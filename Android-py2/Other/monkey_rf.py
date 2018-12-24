#coding=utf-8

import sys
import time,traceback
import os
import platform
import subprocess
import random
import re
import xlsxwriter
from collections import Counter
import threading
import shutil

import logging

reload(sys)
sys.setdefaultencoding('utf-8')


#导入异常,则在线安装

try:
	import xlsxwriter
except ImportError:
	os.popen('pip install XlsxWriter')
try:
	import yaml
except ImportError:
	print "start install yaml"
	os.popen('pip install -i https://pypi.douban.com/simple/ yaml')


# 配置日志信息
logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s %(process)d  %(threadName)s [%(message)s]",
                        filename=os.path.join(os.getcwd(),"monkey_lib.log"),
                        datefmt="%a,%d %b %Y %H:%M:%S",
                        filemode='w+')
# # 定义一个Handler打印INFO及以上级别的日志到sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# # 设置日志打印格式
formatter = logging.Formatter('%(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(levelname)s %(process)d  %(threadName)s [%(message)s]')
console.setFormatter(formatter)
# # 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)


#判断系统类型，windows使用findstr，linux使用grep
system = platform.system()
if system is "Windows":
    find_util = "findstr"
else:
    find_util = "grep"

#设置字符串编码，用于在cmd控制台执行时，中文显示处理
if system is 'Windows':
	str_encode='utf-8'
else:
	str_encode='utf-8'

#返回一个随机整数，用作-s随机数生成器
def get_digit():
	num=random.randint(1,100)
	return num

#调用monkeyrunner指定开始启动activity
def startAppActivity(device_name):

	from com.android.monkeyrunner import MonkeyRunner as mr
	from com.android.monkeyrunner import MonkeyDevice as md
	from com.android.monkeyrunner import MonkeyImage as mi
	from com.android.monkeyrunner.easy import EasyMonkeyDevice  #提供了根据ID进行访问
	from com.android.monkeyrunner.easy import By    #根据ID返回PyObject的方法

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
	componentName="com.kugou.fanxing/com.kugou.fanxing.modul.mainframe.ui.MainFrameActivity"

	#启动特定的Activity
	device.startActivity(component=componentName)
	time.sleep(3)
	print "delay 3 sec"


def startAppActivity_ADB(device_name,StartActivity):
	cmd='adb -s {} shell am start -n {}'.format(device_name,StartActivity)
	try:
		logging.info('启动指定StartActivity...'.encode(str_encode))
		startApp=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = startApp.communicate()
		activity_top_current=get_device_currentActivity(device_name)
		app=activity_top_current.split('/')[0]
		if app==packapgename:
			print 'StartActivity Success!!! ==> {}'.format(StartActivity)
			return
		else:
			print 'StartActivity error!'
			exit(0)
	except Exception as e:
		print e


#获取手机分辨率
def get_device_pix(device_name):
    result = os.popen("adb -s {} shell wm size".format(device_name), "r")
    return result.readline().split("Physical size:")[1].split()[0]

#自动亮屏，解锁屏幕
def autoLockscreen(device_name):
		cmd_poweroff_status='adb -s %s shell dumpsys window policy|%s mScreenOnFully'%(device_name,find_util)
		cmd_lock_status='adb -s %s shell dumpsys window policy|%s mShowingLockscreen'%(device_name,find_util)
		lockScreen=subprocess.Popen(cmd_lock_status, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #处理锁屏命令
		powerOff=subprocess.Popen(cmd_poweroff_status, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #处理黑屏命令
		mAwake=powerOff.stdout.read().split()[0].split('=')[-1]   #获取当前手机屏幕是否黑屏，电源休眠状态,false为黑屏
		if mAwake=='false':  #判断手机是否黑屏
			print "current devices mAwake is false."
			logging.info('当前手机状态为==>黑屏'.encode(str_encode))
			cmd='adb -s {} shell input keyevent 26'.format(device_name)
			os.popen(cmd)  #点击power，亮屏
			logging.info('执行点击power，亮屏'.encode(str_encode))
			mShowingLockscreen=lockScreen.stdout.read().split()[0].split('=')[-1]    #获取当前手机是否为锁屏状态，true为锁屏
			if mShowingLockscreen=='true':   #判断手机是否锁屏
				print 'current devices status is lock screen!!!'
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
				print 'current devices status is lock screen!!!'
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






#截图功能
def screenshot(device_name,screenshot_name):
	if not os.path.exists(os.path.join(os.getcwd(),'screenshot_result')):
		os.mkdir(os.path.join(os.getcwd(),'screenshot_result'))
	os.popen('adb -s {} shell /system/bin/screencap -p /sdcard/{}.png'.format(device_name,screenshot_name))
	if system is 'Windows':
		os.popen('adb pull /sdcard/{}.png {}\{}.png'.format(screenshot_name,os.path.join(os.getcwd(),'screenshot_result'),screenshot_name))
	else:
		os.popen('adb pull /sdcard/{}.png {}/{}.png'.format(screenshot_name,os.path.join(os.getcwd(),'screenshot_result'),screenshot_name))



#获取当前activity
def get_device_currentActivity(device_name):
	try:
		activity_top_current=os.popen("adb -s %s shell dumpsys activity top | %s ACTIVITY"%(device_name,find_util)).read()
		activity_top_current=activity_top_current.split()[1]
		logging.info('当前运行程序平台为 :{}'.format(system).encode(str_encode))
		if system is "Windows":
			print "Current Activity:==>".encode('utf-8'),activity_top_current
		else:
			print "Current Activity:==>",activity_top_current
		return activity_top_current
	except Exception:
		if system is 'Windows':
			print '未检查到任何设备，请检查!'.encode('utf-8')
		else:
			print '未检查到任何设备，请检查!'

#获取当前界面activity，循环监控，如当前界面activity发生变化， 则开启自动截图
def get_device_currentActivity_and_screenshot(device_name):
	while 1:
		activity_top_current=os.popen("adb -s %s shell dumpsys activity top | %s ACTIVITY"%(device_name,find_util)).read()
		activity_top_current=activity_top_current.split()[1]

		#如果不存在，创建目录，执行截图
		if not os.path.exists(os.path.join(os.getcwd(),'screenshot_result')):
			os.mkdir(os.path.join(os.getcwd(),'screenshot_result'))
			screenshot(device_name,activity_top_current.split('/')[-1])
		else:
			if '{}.png'.format(activity_top_current) in os.listdir(os.path.join(os.getcwd(),'screenshot_result')):
				print '{}.png'.format(activity_top_current)
			else:
				'{}.png not exist'.format(activity_top_current)
				screenshot(device_name,activity_top_current.split('/')[-1])
	print "exit loop screenshot..."

#根据名称来结束进程
def kill_process_by_name(name):
    if system is "Windows":
        os.popen('taskkill /f /im %s'%name)
        print 'taskkill /f /im %s'%name
    else:
        pid_list=os.popen("ps -ef | awk '{print $2}'|grep %s"%name)
        for pid in pid_list:
            os.popen('kill -9 %s'%int(pid))
            print 'kill -9 %s'%int(pid)


#用于Logcat捕获app操作日志
def adb_logcat(device_name,packapgename):
	if system is 'Windows':
		print '开始抓取logcat...\n'.encode('utf-8')
	else:
		print '开始抓取logcat...\n'
	# if system is "Windows":
	# 	pid=os.popen('adb -s %s shell ps | grep %s | gawk "{print $2}"'%(device_name,packapgename)).read().strip('\n')
	# else:
	# 	pid=os.popen("adb -s %s shell ps | grep %s | awk '{print $2}'"%(device_name,packapgename)).read().strip('\n')

	# print "包名为{0}==>对应的PID为:{1}".format(packapgename,pid)

	adb_logcat_cmd='adb -s %s logcat -d -v time -b main %s %s> %sapp.log'%(device_name,find_util,packapgename,os.path.join(os.getcwd(),'log\\'))    #adb logcat执行命令，通过包名，来过滤日志信息
	logging.info(adb_logcat_cmd)
	while 1:
		subprocess.Popen(adb_logcat_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	logging.info('exit adb logcat...')


#执行monkey命令
def runMonkeyCMD(device_name,app,count):
    try:
    	activity_top_current=get_device_currentActivity(device_name)
    	packapgename=activity_top_current.split('/')[0]

    	#新开线程，用于实时监控屏幕activiy，进行截图操作
    	screenshot_pro=threading.Thread(target=get_device_currentActivity_and_screenshot,args=(device_name,))
    	screenshot_pro.setDaemon(True)
    	screenshot_pro.start()
    	print "start new threading :[{}] use screenshot".format(screenshot_pro.getName())

		#新开线程，用于抓取logcat日志
    	# adb_logcat_pro=threading.Thread(target=adb_logcat,args=(device_name,packapgename))
    	# adb_logcat_pro.setDaemon(True)
    	# adb_logcat_pro.start()
    	# print "start new threading :[{}] use logcat".format(adb_logcat_pro.getName())

    	s=get_digit()   #生成随机序列号

    	if packapgename==app:
    		print "app is activity_top_current!!!"
        cmd="adb -s %s shell monkey"%(device_name)
        p =  os.popen(cmd)
        if 'usage:' in p.read():
            print "monkey exist!"
            cmd1='%s -p %s -s %s --ignore-crashes --ignore-timeouts --monitor-native-crashes --throttle 500 -v -v -v %s'%(cmd,app,s,count)
            # cmd1='%s -p %s -s %s --ignore-crashes --ignore-timeouts --monitor-native-crashes --throttle 300 -v -v -v 500>monkey.log 2>&1 &'%(cmd,app,s)
            print cmd1
            # print os.popen(cmd1).read()
            device=subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            device_info=device.stdout.read()
            return device_info
        else:
            print "monkey not fonud!"
            return None
    except Exception,e:
        traceback.print_exc()
        pass

#数据分析
def anlayzeData(device_name,packagename,count,exception_list):
	activitys_list=[]   #用于存储所有activity列表
	events_dict={}   #用于存储所有事件类型，以事件类型为key，activiy为value
	events_dict_bak={}   #用于统计具有相同value的key，保存到新的字典中存储
	events_count_dict={}    #用于存储各个activity对应的事件类型个数
	events_data_dict={}    #用于存储各个activity对应的事件类型详细

	device_info=runMonkeyCMD(device_name,packagename,count)
	# if device_info.count('Monkey finished')>0:
	# 	print 'Monkey finished!'
	# else:
	# 	print 'Monkey not finished and exit process!!!'
	# 	exit(0)

	if system is 'Windows':
		with open(os.path.join(os.getcwd(),'log\\monkey.log'),'wb') as f_w:
			f_w.write(device_info)

		f_r=open(os.path.join(os.getcwd(),'log\\monkey.log'),'rb')

		f_w_event=open(os.path.join(os.getcwd(),'log\\event.log'),'wb')
	else:
		with open(os.path.join(os.getcwd(),'log/monkey.log'),'wb') as f_w:
			f_w.write(device_info)

		f_r=open(os.path.join(os.getcwd(),'log/monkey.log'),'rb')

		f_w_event=open(os.path.join(os.getcwd(),'log/event.log'),'wb')

	#提取遍历过的所有activity
	activity_re_mode=re.compile(r'.*cmp=(.*)in package')

	#event事件类型正则匹配模式
	event_re_mode=re.compile(r'Sending(.*): ')

	print '##'*50+'====='+'##'*50+'\n'

	for line_no,line_content in enumerate(f_r):

		# print line_no+1,'===========>',line_content
		#提取事件类型记录
		if ':Sending' in line_content and '(' in line_content and ')' in line_content:
			event=event_re_mode.findall(line_content)
			print line_no+1,'==>',event
			f_w_event.write('%s==>%s\n'%(line_no+1,event))
			events_dict[str(event)+str(line_no+1)]=str(value)
		#提取activity记录
		if 'Allowing start of Intent' in line_content and 'in package %s'%packagename in line_content:
			# print line_no,line_content
			activity = activity_re_mode.findall(line_content)[0].split('}')[0]
			print line_no+1,'==>',activity
			f_w_event.write('%s==>%s\n'%(line_no+1,activity))
			activitys_list.append(activity)
			value=activity+str(line_no+1)
			continue

	print '##'*50+'====='+'##'*50+'\n'
	print activitys_list   #遍历过的所有activity列表
	print len(activitys_list)    #遍历activity个数
	print "activitys:",list(set(activitys_list))    #activity去重后的列表
	print "activitys count:",len(list(set(activitys_list)))   #activity去重后的个数
	print 'event count:',len(events_dict)   #统计事件个数
	print '##'*50+'====='+'##'*50+"\n"
	#根据查询出来的事件类型，提取出所有相同的value值对应的key，组成新的字典
	for k,v in events_dict.items():
		if events_dict_bak.has_key(v):
			events_dict_bak[v].append(k)
		else:
			events_dict_bak[v]=[k]
	# print activity_dict_bak

	#根据上述生成的新的字典，重新提取key中activity值（key去重），组成新的字典,统计覆盖事件类型数量
	for k,v in events_dict_bak.items():
		print k,'==>',len(v)
		#匹配activty值
		activity_key_mode=re.compile(r'(\D+)\d+')
		g=activity_key_mode.findall(k)[0]
		if events_count_dict.has_key(g):
			events_count_dict[g].append(len(v))
		else:
			events_count_dict[g]=[len(v)]
	print events_count_dict

	#根据上述生成的新的字典，重新提取key中activity值（key去重），组成新的字典,统计覆盖的各个事件类型详细
	for k,v in events_dict_bak.items():
		print k,'==>',v
		#匹配activty值
		activity_key_mode=re.compile(r'(\D+)\d+')
		g=activity_key_mode.findall(k)[0]
		if events_data_dict.has_key(g):
			events_data_dict[g].append(v)
		else:
			events_data_dict[g]=[v]
	print events_data_dict

	print '\n'+'#'*40
	#计算各个activity对应的事件总数
	print 'event count:',len(events_dict)   #统计事件总数
	for k,v in events_count_dict.items():
		print k,'==>',sum(v)

	f_r.close()
	f_w_event.close()
	if system is 'Windows':
		logging.info('开始检查monkey异常字段'.encode(str_encode))
		if os.path.exists(os.path.join(os.getcwd(),'log\\monkey.log')):
			abnormal_dict=check_errorMessage(os.path.join(os.getcwd(),'log\\monkey.log'),exception_list)
		else:
			logging.info('monkey.log文件不存在'.encode(str_encode))
			abnormal_dict={}
	else:
		if os.path.exists(os.path.join(os.getcwd(),'log/monkey.log')):
			abnormal_dict=check_errorMessage(os.path.join(os.getcwd(),'log/monkey.log'),exception_list)
		else:
			logging.info('monkey.log文件不存在'.encode(str_encode))
			abnormal_dict={}


	if system is 'Windows':
		logging.info('开始检查logcat异常字段'.encode(str_encode))
		if os.path.exists(os.path.join(os.getcwd(),'log\\app.log')):
			abnormal_dict_2=check_errorMessage(os.path.join(os.getcwd(),'log\\app.log'),exception_list)
		else:
			logging.info('app.log文件不存在'.encode(str_encode))
			abnormal_dict_2={}
	else:
		if os.path.exists(os.path.join(os.getcwd(),'log/app.log')):
			abnormal_dict_2=check_errorMessage(os.path.join(os.getcwd(),'log/app.log'),exception_list)
		else:
			logging.info('app.log文件不存在'.encode(str_encode))
			abnormal_dict_2={}

	# abnormal_dict_2={}
	# abnormal_dict_2=check_errorMessage(os.path.join(os.getcwd(),'log\\app.log'),exception_list)
	logging.info('monkey.log文件检查到异常情况:{}'.format(str(abnormal_dict)).encode(str_encode))
	logging.info('app.log文件检查到异常情况:{}'.format(str(abnormal_dict_2)).encode(str_encode))
	return count,events_dict,events_data_dict,events_count_dict,abnormal_dict,abnormal_dict_2   #返回入参随机事件总数、提取的所有事件类型含遍历的activity集合、各个activtiy对应的事件集合



#检查指定文件对象是否包含指定内容,如果不包启则返回True，主要用于Monkey结果分析

def check_errorMessage(path,exception_list):
    if isinstance(exception_list,unicode):
		exception_list=eval(exception_list)
    if isinstance(exception_list,str):
		exception_list=eval(exception_list)
    logging.info(type(exception_list))
    abnormal_dict={}
    if isinstance(exception_list,list):
	    if os.path.exists(os.path.join(path)):
	        with open(os.path.join(path),'rb') as fopen:
	            for line_no,line_content in enumerate(fopen):
	                for e in exception_list:
	                    if e in line_content:
	                        # print e,line_no,line_content
	                        abnormal_dict[e]=line_no+1
	                    else:
	                        continue
	    else:
	        print "monkey.log not found!"

		print '#'*25+'abnormal list:'+'#'*25
	    print abnormal_dict
	    return abnormal_dict


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
	    if system is 'Windows':
	        os.popen('adb -s {} shell cat /system/build.prop >{}build.txt'.format(device_name,os.path.join(os.getcwd(),'log\\'))) #存放的手机信息
	    else:
	        os.popen('adb -s {} shell cat /system/build.prop >{}build.txt'.format(device_name,os.path.join(os.getcwd(),'log/'))) #存放的手机信息

	    l_list = []
	    if system is 'Windows':
	        with open(os.path.join(os.getcwd(),'log\\build.txt'), "r") as f:
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
	    else:
	        with open(os.path.join(os.getcwd(),'log/build.txt'), "r") as f:
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

	# def __del__(self):
	# 	if os.path.exists(os.path.join(os.getcwd(),'build.txt')):
	# 		os.remove(os.path.join(os.getcwd(),'build.txt'))

class ResultReport(object):
	def __init__(self):
		# creat_time=time.strftime("%Y_%m_%d_%H_%M_%S")
		# report_name='Monkey测试结果报告_{}'.format(creat_time).decode('utf-8').encode('gbk')
		if system is 'Windows':
			report_name='Monkey测试结果报告'
			report_name='{}.xlsx'.format(report_name).decode('utf-8').encode('gbk')
		else:
			report_name='Monkey测试结果报告'
			report_name='{}.xlsx'.format(report_name).decode('utf-8').encode('utf-8')

		self.workbook = xlsxwriter.Workbook(report_name)

		if os.path.exists(os.path.join(os.getcwd(),'screenshot_result')):
			shutil.rmtree(os.path.join(os.getcwd(),'screenshot_result'))   #shutil.rmtree用于删除非空目录
			print "delete sreenshot dir success!"
		else:
			pass
		if os.path.exists(os.path.join(os.getcwd(),'log')):
			# kill_process_by_name('grep.exe')
			# kill_process_by_name('adb.exe')   #清除adb及grep进程
			# print "删除grep.exe和adb.exe进程..."
			shutil.rmtree(os.path.join(os.getcwd(),'log'))   #shutil.rmtree用于删除非空目录
			print "Delete log dir success!"
			time.sleep(0.5)
			os.mkdir(os.path.join(os.getcwd(),'log'))
			print 'Create new log dir success!'
		else:
			os.mkdir(os.path.join(os.getcwd(),'log'))
			print 'Create new log dir success!'

	def gen_monkey_report(self,device_name,packapgename,count,exception_list):

		count,events_dict,events_data_dict,events_count_dict,abnormal_dict,abnormal_dict_2=anlayzeData(device_name,packapgename,count,exception_list)

		worksheet3 = self.workbook.add_worksheet('Monkey测试报告汇总')
		worksheet = self.workbook.add_worksheet('Monkey测试报告详细')
		worksheet2 = self.workbook.add_worksheet('Activity截图信息')


		#检查monkey是否检查到异常日志
		if len(abnormal_dict)>0 and len(abnormal_dict_2)>0:
			exception_key_monkey=abnormal_dict.items()
			exception_key_logcat=abnormal_dict_2.items()
			abnormal_flag='monkey异常字段及行号:{0}\nlogcat异常字段及行号:{1}'.format(str(exception_key_monkey),str(exception_key_logcat))

		else:
			abnormal_flag='未检查到异常'

		activity_list=[]   #用于存放activity列表
		events_count_list=[]   #用于存放各个activity列表对应的事件总数
		for k,v in events_count_dict.items():
			# print k,'==>',sum(v)
			activity_list.append(k)
			events_count_list.append(sum(v))
		print activity_list
		print events_count_list

		worksheet.set_column('A:A',len(activity_list[-1])+7)  #设置A列列宽
		worksheet.set_column('B:G',len(str(count))+14)  #设置B:G列列宽
		worksheet.set_column('F:F',len(str(count))+25)

		#创建图表字体样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_head=self.workbook.add_format()
		format_content=self.workbook.add_format()
		format_content_no_border=self.workbook.add_format()

		format_content_left=self.workbook.add_format()

		format_screenshot_activity=self.workbook.add_format()
		format_screenshot_activity_red=self.workbook.add_format()
		format_Exceptions_red=self.workbook.add_format()

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

		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')
		format_title.set_font(u'微软雅黑')

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

		worksheet.set_row(0,36)   #设置第一行，行高为36
		worksheet.merge_range('A1:G1',u'Monkey随机测试覆盖activti及事件类型详细统计',format_head)
		worksheet2.set_row(0,36)   #设置第一行，行高为36
		worksheet2.merge_range('A1:K1',u'Activity与界面截图对应表（仅供参考）',format_head)
		worksheet3.set_row(0,36)   #设置第一行，行高为36
		worksheet3.merge_range('A1:K1',u'Monkey随机事件覆盖测试汇总概况',format_head)

		#获取设备信息
		p1=GetDeviceInfo()
		app_version=p1.getAppVersion(device_name,packapgename)
		module=p1.get_phone_Msg(device_name)[1]
		print app_version,module

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
			print k,'=====>',v

			#对每个activity包含的所有事件数据进行处理
			for i in str(v).split(','):
				event=event_action_re_mode.findall(i)[0]
				event_list.append(event)
				event_type_list.append(event[0])


			print Counter(event_list)
			print Counter(event_type_list)
			print Counter(event_type_list).keys()
			print Counter(event_type_list).values()

			event_type_percent_list=[]  #存事件类型占比
			event_action_percent_list=[]  #存事件动作占比

			for value in Counter(event_type_list).values():
				percent='%.3f%%'%(float(value)/sum(Counter(event_type_list).values())*100)
				event_type_percent_list.append(percent)

			print event_type_percent_list

			events_type_list.append(str(Counter(event_type_list).items()))
			events_types_percents_list.append(str(event_type_percent_list))

			temp=[]   #临时列表，对类型进行排序，经过特殊处理后的事件数据
			for k,v in Counter(event_list).items():
				t="{}->{}".format(str(k).strip('\(').strip('\)').replace(',',':').replace('\'',''),v)
				temp.append(t)
			for i in sorted(temp):
				print i
			print
			# events_actions_list.append(str(sorted(temp)))   #将排序后的事件类型添加到新列表集合中
			events_actions_list.append(str(Counter(event_list).items()))   #将事件动作存放新列表中

			for value in Counter(event_list).values():
				percent='%.3f%%'%(float(value)/sum(Counter(event_list).values())*100)
				event_action_percent_list.append(percent)

			events_actions_percents_list.append(str(event_action_percent_list))

			print event_type_percent_list
			print event_action_percent_list


		print "*"*50+'\n'
		print events_actions_list
		print events_type_list
		print "*"*50+'\n'

		data_title=[[packapgename],[app_version],[module],[device_name],[count],[len(events_dict)],[len(events_count_dict)],[str(abnormal_flag)]]   #统计项

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

		worksheet3.merge_range('G2:K2',data_title[4][0],format_content)
		worksheet3.merge_range('G3:K3',data_title[5][0],format_content)
		worksheet3.merge_range('G4:K4',data_title[6][0],format_content)
		worksheet3.merge_range('G5:K5',data_title[7][0],format_content)

		worksheet3.merge_range('A9:F9','Activity名称',format_title)
		worksheet3.merge_range('G9:K9','事件数',format_title)



		#插入截图到worksheet2中
		activity_list_no_packagename=[]  #用于存储不含包名的activity

		for activity in activity_list:
			activity_list_no_packagename.append(activity.split('/')[-1].strip())

		#输出去掉包名的activity列表
		print activity_list_no_packagename
		activity_list_no_packagename_len=len(activity_list_no_packagename)
		if activity_list_no_packagename_len>0:
			for i in xrange(activity_list_no_packagename_len):
				if i==0:
					worksheet2.merge_range('A{}:F{}'.format(3,30*(i+1)+1),activity_list_no_packagename[i],format_screenshot_activity)
					if activity_list_no_packagename[i]+'.png' in os.listdir(os.path.join(os.getcwd(),'screenshot_result')):
						worksheet2.insert_image('G3', './screenshot_result/{}.png'.format(activity_list_no_packagename[i]),{'x_scale': 0.3, 'y_scale': 0.3})
					else:
						worksheet2.merge_range('G{}:K{}'.format(3,30*(i+1)+1),u'暂无截图信息',format_screenshot_activity_red)
				else:
					worksheet2.merge_range('A{}:F{}'.format(30*i+2,30*(i+1)+1),activity_list_no_packagename[i],format_screenshot_activity)

					if activity_list_no_packagename[i]+'.png' in os.listdir(os.path.join(os.getcwd(),'screenshot_result')):
						worksheet2.insert_image('G{}'.format(30*i+2), './screenshot_result/{}.png'.format(activity_list_no_packagename[i]),{'x_scale': 0.3, 'y_scale': 0.3})
					else:
						worksheet2.merge_range('G{}:K{}'.format(30*i+2,30*(i+1)+1),u'暂无截图信息',format_screenshot_activity_red)

		#表3，activity覆盖排名数据生成

		events_count_dict_bak={}
		for k,v in events_count_dict.items():
			# print k,'==>',sum(v)
			events_count_dict_bak[k]=sum(v)
		print events_count_dict_bak
		activity_reverse_list = sorted(events_count_dict_bak.items(), key=lambda events_count_dict_bak:events_count_dict_bak[1],reverse=True)   #按照字典中的value值大小进行降序排列

		activitys=[]
		keys=[]
		for i in activity_reverse_list:
			activitys.append(i[0])   #提取排序后的activtiy
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

		try:
			print 'start ready close workbook...'
			time.sleep(0.2)
			self.workbook.close()
			print 'close workbook success...'
		except Exception,e:
			# traceback.print_exc()
			print e
			if system is 'Windows':
				print "出现异常，报告生成失败!".encode('utf-8')
			else:
				print "出现异常，报告生成失败!"

		else:
			if system is 'Windows':
				print "报告生成完成!".encode('utf-8')
			else:
				print "报告生成完成!"

class monkey_rf():
	def main(self,device_name,packapgename,appActivity,count,exception_list):
		logging.info('开始执行程序...'.encode('utf-8'))
		autoLockscreen(device_name)   #手机自动亮屏，解锁
		startAppActivity_ADB(device_name,appActivity) #启动指定activity
		p=ResultReport()
		p.gen_monkey_report(device_name,packapgename,count,exception_list)
		logging.info('程序运行结束!'.encode('utf-8'))

if __name__ == '__main__':
	# if os.path.exists(os.path.join('config.yaml')):
	# 	f = open('config.yaml')
	# 	dataMap = yaml.load(f)
	# 	device_name=dataMap['MonkeyConfig']['device_Name']
	# 	packapgename=dataMap['MonkeyConfig']['packapgname']
	# 	count=dataMap['MonkeyConfig']['count']
	# 	exception_list=dataMap['MonkeyConfig']['Exceptions']
	# 	appActivity=dataMap['MonkeyConfig']['appActivity']
	# else:
	# 	if system is 'Windows':
	# 		print "config.yaml配置文件不存在!".encode('utf-8')
	# 	else:
	# 		print "config.yaml配置文件不存在!"
	# 	exit(0)

		device_name=sys.argv[1]
		packapgename=sys.argv[2]
		appActivity=sys.argv[3]
		count=sys.argv[4]
		exception_list=sys.argv[5]

        # device_name='K31GLMA660800338'
        # packapgename='com.kugou.fanxing'
        # appActivity= "com.kugou.fanxing/com.kugou.fanxing.modul.mainframe.ui.MainFrameActivity"
        # count=100
        # exception_list=['NullPointer','IllegalState','IllegalArgument','ArrayIndexOutOfBounds','RuntimeException','SecurityException','ANR','CRASH',
        # 'EXCEPTION','FATAL','ClassNotFoundException','StackOverflowError','OutOfMemoryError']
		p=monkey_rf()

		print "param list:===>",device_name,packapgename,appActivity,count,exception_list
		p.main(device_name,packapgename,appActivity,count,exception_list)

	# startAppActivity(device_name)
	# anlayzeData(device_name,packapgename,100)
	# p=ResultReport()
	# p.gen_monkey_report()
	# p=GetDeviceInfo()
	# print p.get_phone_Msg(device_name)
	# print p.getAppVersion(device_name,packapgename)
	# startAppActivity_ADB(device_name,appActivity)
	# autoLockscreen(device_name)


	# p=MiniCapScreen('71CDBLN22VVP')
	# print p.get_cpu_version()
	# print p.get_sdk_version()
