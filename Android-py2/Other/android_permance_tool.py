#coding=utf-8
"""Usage: 
android_permance_tool.py [-h | --help]
android_permance_tool.py <device_name> <packagename> <collect_type> <delay_time> <max_time> <report_name>
android_permance_tool.py [--merge] <merge_type> <xlsfile1> <xlsfile2>
android_permance_tool.py [--mergefx] <merge_type> <xlsfile1> <xlsfile2>
android_permance_tool.py [-vv]

功能1：Android端性能数据收集及图表自动生成工具（支持内存、cpu、流量、fps、电量、 电压、温度），且同时兼容windows\liunx\mac机上执行采集
功能2：支持两个版本性能数据分析比较，汇总，自动生成新的汇总结果报告，且支持性能测试定制化报告生成
功能3：打印输出当前连接手机设备的应用包名、Activity名

Author：zouzhiquan

Arguments1:
  device_name     第1个sys.arg[1]参数为：设备序列号
  packagename     第2个sys.arg[2]参数为：采集应用包名
  collect_type    第3个sys.arg[3]参数为：采集类型分为memory、cpu、fps、net、battery、All,其中All为全部采集
  delay_time      第4个sys.arg[4]参数为采集间隔，单位秒，当设置为0时，则持续采集
  max_time        第5个sys.arg[5]参数为采集时长，单位秒
  report_name     第6个sys.arg[6]参数为生成报告名称

Arguments2:
  merge           第1个sys.arg[1]参数为:需执行的动作为合并汇总报告，使用--merge或--mergefx（繁星定制化模板）
  merge_type      第2个sys.arg[2]参数为：合并汇总指标类别,分为memory、cpu、fps、net、battery、All,其中All为全部分析（当使用--mergefx时，类别只能选择All）
  xlsfile1        第3个sys.arg[3]参数为：报告文件1，报告文件需放在脚本根目录下
  xlsfile2        第4个sys.arg[4]参数为：报告文件2，报告文件需放在脚本根目录下


Example1:
说明:针对android性能数据采集命令示例
示例1：python android_permance_tool.py K31GLMA660800338 com.kugou.fanxing battery 2 30  采集com.kugou.fanxing电量指标30秒
示例2：python android_permance_tool.py K31GLMA660800338 com.kugou.fanxing memory 0 30  采集com.kugou.fanxing内存指标30秒
示例3：python android_permance_tool.py K31GLMA660800338 com.kugou.fanxing All 1 60  采集com.kugou.fanxing全部指标60秒
示例4：python android_permance_tool.py AA7DKF4LRGBMPVYL com.kugou.android All 1 30  采集com.kugou.android全部指标30秒

Example2:
说明:针对版本数据自动分析，对比分析两个版本之间结果汇总示例 (表格1为基线版本，表格2为测试版本)
示例1：python android_permance_tool.py --merge fps android_permance_report_2016_12_01_15_38_44.xlsx android_permance_report_2016_12_01_15_44_01.xlsx
示例2：python android_permance_tool.py --merge All android_permance_report1.xlsx android_permance_report2.xlsx

Example3:
说明: 定制化报告模板生成，对比分析两个版本之间结果汇总示例 (表格1为基线版本，表格2为测试版本)
示例1：python android_permance_tool.py --mergefx All 基线版本.xlsx 测试版本.xlsx

Options:
  -H --help    查看帮助信息
  --merge      合并功能
  --mergefx    定制化合并报告
  -vv          输出当前应用包名、activity名
"""

import os,sys
import platform
import subprocess
import re
import time
import logging
import traceback
from datetime import datetime
import threading
import shutil
from collections import Counter
import ctypes
import signal

#导入异常,则在线安装
try:
	from docopt import docopt
	import xlsxwriter
except ImportError:
	print "start install docopt and xlsxwriter"
	os.popen('pip install docopt')
	os.popen('pip install XlsxWriter')
try:
	import xlrd
except ImportError:
	print "start install xlrd"
	os.popen('pip install -i https://pypi.douban.com/simple/ xlrd')


reload(sys)
sys.setdefaultencoding('utf-8')



#用于开启报告名称标记,True则每次生成报告以时间命名
Debug=True
report_name=''
report_merge_name=''

#******打印日志文件*******************

# 配置日志信息
logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(process)d  %(funcName)s [line:%(lineno)d] %(threadName)s [%(message)s]",
                        filename=os.path.join(os.getcwd(),"android_permance_tool.log"),
                        datefmt="%a,%d %b %Y %H:%M:%S",
                        filemode='w+')
# # 定义一个Handler打印INFO及以上级别的日志到sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# # 设置日志打印格式
formatter = logging.Formatter('%(asctime)s %(levelname)s %(process)d %(funcName)s [line:%(lineno)d] %(threadName)s [%(message)s]')
console.setFormatter(formatter)
# # 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)


##定义过虑的后端进程标识
ext=['support','pushservice','remote','hotfix','push']
ext_=[]


#定义Linux控制台颜色输出类
class styles:
        HEADER = '\033[95m'  #紫色
        BLUE = '\033[94m'   #蓝色
        GREEN = '\033[92m'  #绿色
        YELLOW = '\033[93m'  #黄色
        RED = '\033[91m'     #深红
        ENDC = '\033[0m'    #关闭所有属性，恢复控制台默认
        BOLD='\033[1m'      #加粗
        UNDERLINE='\033[4m'   #下划线


if platform.system() is "Windows":
#定义Window控制台颜色输出类
	class WindowsCmdOutPut():

		STD_INPUT_HANDLE = -10
		STD_OUTPUT_HANDLE = -11
		STD_ERROR_HANDLE = -12
		# get handle

		std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

		def __init__(self):

			# 字体颜色定义 ,关键在于颜色编码，由2位十六进制组成，分别取0~f，前一位指的是背景色，后一位指的是字体色
			#由于该函数的限制，应该是只有这16种，可以前景色与背景色组合。也可以几种颜色通过或运算组合，组合后还是在这16种颜色中

			# Windows CMD命令行 字体颜色定义 text colors
			self.FOREGROUND_BLACK = 0x00 # black.
			self.FOREGROUND_DARKBLUE = 0x01 # dark blue.
			self.FOREGROUND_DARKGREEN = 0x02 # dark green.
			self.FOREGROUND_DARKSKYBLUE = 0x03 # dark skyblue.
			self.FOREGROUND_DARKRED = 0x04 # dark red.
			self.FOREGROUND_DARKPINK = 0x05 # dark pink.
			self.FOREGROUND_DARKYELLOW = 0x06 # dark yellow.
			self.FOREGROUND_DARKWHITE = 0x07 # dark white.
			self.FOREGROUND_DARKGRAY = 0x08 # dark gray.
			self.FOREGROUND_BLUE = 0x09 # blue.
			self.FOREGROUND_GREEN = 0x0a # green.
			self.FOREGROUND_SKYBLUE = 0x0b # skyblue.
			self.FOREGROUND_RED = 0x0c # red.
			self.FOREGROUND_PINK = 0x0d # pink.
			self.FOREGROUND_YELLOW = 0x0e # yellow.
			self.FOREGROUND_WHITE = 0x0f # white.


			# Windows CMD命令行 背景颜色定义 background colors
			self.BACKGROUND_BLUE = 0x10 # dark blue.
			self.BACKGROUND_GREEN = 0x20 # dark green.
			self.BACKGROUND_DARKSKYBLUE = 0x30 # dark skyblue.
			self.BACKGROUND_DARKRED = 0x40 # dark red.
			self.BACKGROUND_DARKPINK = 0x50 # dark pink.
			self.BACKGROUND_DARKYELLOW = 0x60 # dark yellow.
			self.BACKGROUND_DARKWHITE = 0x70 # dark white.
			self.BACKGROUND_DARKGRAY = 0x80 # dark gray.
			self.BACKGROUND_BLUE_1 = 0x90 # blue.
			self.BACKGROUND_GREEN_2 = 0xa0 # green.
			self.BACKGROUND_SKYBLUE = 0xb0 # skyblue.
			self.BACKGROUND_RED = 0xc0 # red.
			self.BACKGROUND_PINK = 0xd0 # pink.
			self.BACKGROUND_YELLOW = 0xe0 # yellow.
			self.BACKGROUND_WHITE = 0xf0 # white.



		def set_cmd_text_color(self,color, handle=std_out_handle):
			Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
			return Bool

		#reset white
		def resetColor(self):
			self.set_cmd_text_color(self.FOREGROUND_RED | self.FOREGROUND_GREEN | self.FOREGROUND_BLUE)

		###############################################################

		#暗蓝色
		#dark blue
		def printDarkBlue(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKBLUE)
			sys.stdout.write(mess)
			self.resetColor()

		#暗绿色
		#dark green
		def printDarkGreen(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKGREEN)
			sys.stdout.write(self,mess)
			self.resetColor()

		#暗天蓝色
		#dark sky blue
		def printDarkSkyBlue(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKSKYBLUE)
			sys.stdout.write(mess)
			self.resetColor()

		#暗红色
		#dark red
		def printDarkRed(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKRED)
			sys.stdout.write(mess)
			self.resetColor()

		#暗粉红色
		#dark pink
		def printDarkPink(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKPINK)
			sys.stdout.write(mess)
			self.resetColor()

		#暗黄色
		#dark yellow
		def printDarkYellow(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKYELLOW)
			sys.stdout.write(mess)
			self.resetColor()

		#暗白色
		#dark white
		def printDarkWhite(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKWHITE)
			sys.stdout.write(mess)
			self.resetColor()

		#暗灰色
		#dark gray
		def printDarkGray(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_DARKGRAY)
			sys.stdout.write(mess)
			self.resetColor()

		#蓝色
		#blue
		def printBlue(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_BLUE)
			sys.stdout.write(mess)
			self.resetColor()

		#绿色
		#green
		def printGreen(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_GREEN)
			sys.stdout.write(mess)
			self.resetColor()

		#天蓝色
		#sky blue
		def printSkyBlue(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_SKYBLUE)
			sys.stdout.write(mess)
			self.resetColor()

		#红色
		#red
		def printRed(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_RED)
			sys.stdout.write(mess)
			self.resetColor()

		#粉红色
		#pink
		def printPink(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_PINK)
			sys.stdout.write(mess)
			self.resetColor()

		#黄色
		#yellow
		def printYellow(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_YELLOW)
			sys.stdout.write(mess)
			self.resetColor()

		#白色
		#white
		def printWhite(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_WHITE)
			sys.stdout.write(mess)
			self.resetColor()

		##################################################

		#白底黑字
		#white bkground and black text
		def printWhiteBlack(self,mess):
			self.set_cmd_text_color(self.FOREGROUND_BLACK | self.BACKGROUND_WHITE)
			sys.stdout.write(mess)
			self.resetColor()

		#白底黑字
		#white bkground and black text
		def printWhiteBlack_2(self,mess):
			self.set_cmd_text_color(0xf0)
			sys.stdout.write(mess)
			self.resetColor()


		#黄底蓝字
		#white bkground and black text
		def printYellowRed(self,mess):
			self.set_cmd_text_color(self.BACKGROUND_YELLOW | self.FOREGROUND_RED)
			sys.stdout.write(mess)
			self.resetColor()


system = platform.system()
if system is "Windows":
	window=WindowsCmdOutPut()
	window.printGreen('当前运行系统为:{}\n'.format(system).encode('gbk'))
else:
	logging.info('当前运行系统为:{}'.format(system))


#设置字符串编码，用于在cmd控制台执行时，中文显示处理
if system is 'Windows':
	str_encode='gbk'
	find_util = "findstr"
else:
	str_encode='utf-8'
	find_util = "grep"



#判断python版本是否大于3
if platform.python_version().split('.')[0]<int(3):
    if system is 'Windows':
        logging.info('当前环境版本为{}，本程序目前仅兼容python2系列！'.format(platform.python_version()).encode('gbk'))
        exit(0)
else:
    if system is 'Windows':
       logging.info('当前环境版本为{}'.encode('gbk').format(platform.python_version()))
    else:
       logging.info('当前环境版本为{}'.format(platform.python_version()))



#判断docopt和XlsxWriter模块是否安装
docopt_lib=os.popen('pip freeze| {} docopt'.format(find_util)).read()
XlsxWriter_lib=os.popen('pip freeze| {} XlsxWriter'.format(find_util)).read()
if len(docopt_lib)==0:
	os.popen('pip install docpot')
if len(XlsxWriter_lib)==0:
	os.popen('pip install XlsxWriter')


#计时程序，计时单位1s，获取当前最大时间转换后的秒数
timeit=0
seconds_start=0
seconds_end=0
current_time_format=''
seconds_start_format=''
seconds_end_format=''
def timer(max_time):
	global timeit
	global seconds_start
	global seconds_end
	global current_time_format
	global seconds_end_format
	if system is "Windows":
		print "#"*25+"运行时长转换后对应的时间为:".encode('gbk')+"#"*25
	else:
		print "#"*25+"运行时长转换后对应的时间为:"+"#"*25
	current_time=time.strftime("%Y-%m-%d %H:%M:%S")
	d=datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S")
	#把具体格式时间转换成秒数
	seconds_start=time.mktime(d.timetuple())
	#秒数转换成具体对应的格式时间
	seconds_start_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds_start))
	seconds_end=seconds_start+int(max_time)
	if system is "Windows":
		print "把当前时间转换成秒数为:".encode('gbk'),seconds_start
	else:
		print "把当前时间转换成秒数为:",seconds_start

	if system is "Windows":
		print "最大时间到达后,转换后的秒数为:".encode('gbk'),seconds_end
	else:
		print "最大时间到达后,转换后的秒数为:",seconds_end
	seconds_end_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds_end))
	if system is "Windows":
		window=WindowsCmdOutPut()
		window.printGreen("程序执行对应的开始时间为:{}\n".format(seconds_start_format).encode('gbk'))
		window.printGreen("程序执行对应结束时间为:{}\n".format(seconds_end_format).encode('gbk'))
		window.printWhite('')
		logging.info("程序执行对应的开始时间为:{}".format(seconds_start_format).encode('gbk'))
		logging.info("程序执行对应结束时间为:{}".format(seconds_end_format).encode('gbk'))
		window.printWhite('')

	else:
		print styles.GREEN+"程序执行对应的开始时间为:",seconds_start_format+styles.ENDC
		print styles.GREEN+"程序执行对应结束时间为:",seconds_end_format+styles.ENDC


	for i in xrange(int(seconds_start),int(seconds_end)):
		time.sleep(1)
		timeit=i
		current_time_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeit))


#打开，关闭飞行模式
def turn_airplane_mode(device_name,flag):
	#打开飞行模式
	if flag==1:
		os.popen('adb -s {} shell settings put global airplane_mode_on 1'.format(device_name))
		os.popen('adb -s {} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true'.format(device_name))
		if system is "Windows":
			print "飞行模式已打开".encode('gbk')
		else:
			print "飞行模式已打开"
	#关闭飞行模式
	elif flag==0:
		os.popen('adb -s {} shell settings put global airplane_mode_on 0'.format(device_name))
		os.popen('adb -s {} shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false'.format(device_name))
		if system is "Windows":
			print "飞行模式已关闭".encode('gbk')
		else:
			print "飞行模式已关闭"


#获取当前设备序列号、当前应用包名、activity名等
def get_current_device_info():
	device=os.popen('adb devices')
	device_info=device.read()
	serino=device_info.strip('List of devices attached').split()

	if system is "Windows":
		window=WindowsCmdOutPut()
		if len(serino[::2])==len(serino[1::2]) and len(serino[1::2])>0:   #如果设备连接数大于0
			if len(list(set(serino[1::2])))==1 and list(set(serino[1::2]))[0]=="device":    #如果设备连接状态都为devices
				print "\n返回所有连接在线设备序列号:{}".encode('gbk').format(serino[::2])
				print "获取到当前连接的第一台设备序列号为:{}".encode('gbk').format(serino[::2][0])
				p=Android_Permance()
				print
				device_name_packinfo=p.get_device_currentActivity(serino[::2][0])
				if device_name_packinfo:
					packapgename=device_name_packinfo.split('/')
					print '当前应用包名为:{}'.encode('gbk').format(packapgename[0])
			else:
				print "please check adb devices list exists offline !!!"
		else:
			window.printRed("未获取到任何设备序列号\n".encode('gbk'))
			window.printWhite('')   #恢复控制台默认字体颜色
	else:
		if len(serino[::2])==len(serino[1::2]) and len(serino[1::2])>0:   #如果设备连接数大于0
			if len(list(set(serino[1::2])))==1 and list(set(serino[1::2]))[0]=="device":    #如果设备连接状态都为devices
				print "\n返回所有连接在线设备序列号:{}".format(serino[::2])
				print "获取到当前连接的第一台设备序列号为:{}".format(serino[::2][0])
				p=Android_Permance()
				print
				device_name_packinfo=p.get_device_currentActivity(serino[::2][0])
				if device_name_packinfo:
					packapgename=device_name_packinfo.split('/')
					print '当前应用包名为:{}'.format(packapgename[0])
			else:
				print "please check adb devices or exists offline !!!"
		else:
			print styles.RED+"未获取到任何设备序列号"+styles.ENDC


class Android_Permance(object):
	def __str__(self):
		print "开始进行android资源分析"

	#获取内存占用信息
	def get_device_memInfo(self,device_name,packapgename,delay_time):
		#控制采样次数
		# times=10

		PSS_total_list=[]
		Priv_Dirty_total_list=[]
		PSS_Dalvik_list=[]
		Priv_Dirty_Dalvik_list=[]

		VSS_list=[]
		RSS_list=[]
		time_list=[]
		Dalvik_Heap_list=[]
		Native_Heap_list=[]
		Dalvik_Heap_Alloc_list=[]

		#初始化采集次数为0，创建采集列表
		times=0
		times_list=[]

		while True:
			if int(delay_time)!=0:
				time.sleep(int(delay_time))
			current_time=time.strftime("%Y-%m-%d %H:%M:%S")
			d=datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S")
			#把具体格式时间转换成秒数
			seconds_current=time.mktime(d.timetuple())
			seconds_current_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds_current))
			if system is "Windows":
				logging.info("获取开始运行的秒数:{}".encode('gbk').format(timeit))
				logging.info("获取当前运行的秒数:{}".encode('gbk').format(seconds_current))
				logging.info("获取开始的具体时间:{}".encode('gbk').format(current_time_format))
				logging.info("获取当前运行的具体时间:{}".encode('gbk').format(seconds_current_format))
			else:
				logging.info("获取开始运行的秒数:{}".format(timeit))
				logging.info("获取当前运行的秒数:{}".format(seconds_current))
				logging.info("获取开始的具体时间:{}".format(current_time_format))
				logging.info("获取当前运行的具体时间:{}".format(seconds_current_format))

			if int(seconds_current)>=int(seconds_end):
				if system is "Windows":
					logging.info("已达到最大指定运行时长,停止采集!".encode('gbk'))
					logging.info("当前已完成采集次数为:{}次".encode('gbk').format(times))
				else:
					logging.info("已达到最大指定运行时长,停止采集!")
					logging.info("当前已完成采集次数为:{}次".format(times))
				break

			else:

		# for i in xrange(int(times)):
				if system is "Windows":
					logging.info("*"*20+"第{}次内存开始采样".encode('gbk').format(times+1)+"*"*20)
				else:
					logging.info("*"*20+"第{}次内存开始采样".format(times+1)+"*"*20)
				_time=self.get_device_currenTime(device_name)
				if system is "Windows":
					logging.info( "获取内存时间:{}".encode('gbk').format(_time))
				else:
					logging.info( "获取内存时间:{}".format(_time))
				time_list.append(str(_time))

				#*****************提取系统总内存*************************
				MemTotal=os.popen("adb -s {0} shell cat /proc/meminfo |{1} MemTotal".format(device_name,find_util)).read().strip('\n')
				MemFree=os.popen("adb -s {0} shell cat /proc/meminfo |{1} MemFree".format(device_name,find_util)).read().strip('\n')
				#从字符串中提取内存值大小
				mode=re.compile(r'\d+')
				MemTotal=int(mode.findall(MemTotal)[0])
				MemFree=int(mode.findall(MemFree)[0])
				if system is "Windows":
					logging.info( "系统总内存为:{}KB".encode('gbk').format(MemTotal))
					logging.info( "系统剩余内存为:{}KB".encode('gbk').format(MemFree))
				else:
					logging.info( "系统总内存为:{}KB".format(MemTotal))
					logging.info( "系统剩余内存为:{}KB".format(MemFree))

				#**********获取单个应用程序最大内存限制及java虚拟机的最大内存限制****************
				#查看单个应用程序最大内存限制
				if system is "Windows":
					logging.info( "#"+"*"*5+"获取单个应用程序最大内存限制及java虚拟机的最大内存限制".encode('gbk')+"*"*5)
				else:
					logging.info( "#"+"*"*5+"获取单个应用程序最大内存限制及java虚拟机的最大内存限制"+"*"*5)
				heapgrowthlimit=os.popen("adb -s {0} shell getprop|{1} heapgrowthlimit".format(device_name,find_util)).read()
				mode = re.compile(r'\d+')

				try:
					heapgrowthlimit=mode.findall(heapgrowthlimit)[-1]
				except IndexError:
					logging.info('捕获到索引异常==>heapgrowthlimit值为:{}'.encode(str_encode).format(heapgrowthlimit))
					heapgrowthlimit=0

				#单个java虚拟机最大的内存限制
				heapsize=os.popen("adb -s {0} shell getprop|{1} dalvik.vm.heapsize".format(device_name,find_util)).read()
				mode = re.compile(r'\d+')

				try:
					heapsize=mode.findall(heapsize)[-1]
				except IndexError:
					logging.info('捕获到索引异常==>heapsize值为:{}'.encode(str_encode).format(heapsize))
					heapsize=0

				if system is "Windows":
					logging.info( "获取单个应用程序最大内存限制:{} MB".encode('gbk').format(heapgrowthlimit))
					logging.info( "java虚拟机的最大内存限制:{} MB".encode('gbk').format(heapsize))
				else:
					logging.info( "获取单个应用程序最大内存限制:{} MB".format(heapgrowthlimit))
					logging.info( "java虚拟机的最大内存限制:{} MB".format(heapsize))

				#************************获取PSS及Private内存值******************************
				if system is "Windows":
					logging.info("*"*20+"获取PSS内存信息".encode('gbk')+"*"*20)
				else:
					logging.info("*"*20+"获取PSS内存信息"+"*"*20)
				try:
					#指定包名下的内存详细
					# PSS_info=os.popen("adb -s {0} shell dumpsys meminfo {1}".format(device_name,packapgename)).read()
					# print PSS_info
					if system is "Windows":
						PSS_total=os.popen('adb -s %s shell dumpsys meminfo %s | findstr TOTAL| gawk "{print $2}"'%(device_name,packapgename)).read().strip('\n').split('\n')[0]
						Priv_Dirty_total=os.popen('adb -s %s shell dumpsys meminfo %s | findstr TOTAL| gawk "{print $3}"'%(device_name,packapgename)).read().strip('\n').split('\n')[0]

						PSS_Dalvik=os.popen('adb -s %s shell dumpsys meminfo %s | findstr Dalvik| gawk "{print $3}"'%(device_name,packapgename)).readline().strip('\n').split('\n')[0]
						Priv_Dirty_Dalvik=os.popen('adb -s %s shell dumpsys meminfo %s | findstr Dalvik| gawk "{print $4}"'%(device_name,packapgename)).readline().strip('\n').split('\n')[0]
					else:
						PSS_total=os.popen("adb -s %s shell dumpsys meminfo %s | grep TOTAL| awk '{print $2}'"%(device_name,packapgename)).read().strip('\n').split('\n')[0]
						Priv_Dirty_total=os.popen("adb -s %s shell dumpsys meminfo %s | grep TOTAL| awk '{print $3}'"%(device_name,packapgename)).read().strip('\n').split('\n')[0]

						PSS_Dalvik=os.popen("adb -s %s shell dumpsys meminfo %s | grep Dalvik| awk '{print $3}'"%(device_name,packapgename)).readline().strip('\n').split('\n')[0]
						Priv_Dirty_Dalvik=os.popen("adb -s %s shell dumpsys meminfo %s | grep Dalvik| awk '{print $4}'"%(device_name,packapgename)).readline().strip('\n').split('\n')[0]

					if system is "Windows":
						logging.info( "PSS Total占用内存大小:{}KB".encode('gbk').format(PSS_total))
						logging.info( "Priv_Dirty_total占用内存大小:{}KB".encode('gbk').format(Priv_Dirty_total))
						logging.info( "PSS_Dalvik占用内存大小:{}KB".encode('gbk').format(PSS_Dalvik))
						logging.info( "Priv_Dirty_Dalvik占用内存大小:{}KB".encode('gbk').format(Priv_Dirty_Dalvik))
					else:
						logging.info( "PSS Total占用内存大小:{}KB".format(PSS_total))
						logging.info( "Priv_Dirty_total占用内存大小:{}KB".format(Priv_Dirty_total))
						logging.info( "PSS_Dalvik占用内存大小:{}KB".format(PSS_Dalvik))
						logging.info( "Priv_Dirty_Dalvik占用内存大小:{}KB".format(Priv_Dirty_Dalvik))

					#增加容错处理
					if len(str(PSS_total))==0 or PSS_total=='':
						PSS_total=0
					if len(str(Priv_Dirty_total))==0 or Priv_Dirty_total=='':
						Priv_Dirty_total=0
					if len(str(PSS_Dalvik))==0 or PSS_Dalvik=='':
						PSS_Dalvik=0
					if len(str(Priv_Dirty_Dalvik))==0 or Priv_Dirty_Dalvik=='':
						Priv_Dirty_Dalvik=0

					PSS_total_list.append(int(PSS_total))
					Priv_Dirty_total_list.append(int(Priv_Dirty_total))
					PSS_Dalvik_list.append(int(PSS_Dalvik))
					Priv_Dirty_Dalvik_list.append(int(Priv_Dirty_Dalvik))

					# #获取PSS内存占用方式二
					# PSS_v2=os.popen("adb -s {0} shell dumpsys meminfo -c|grep proc|grep {1}| grep -v pushservice".format(device_name,packapgename)).read()
					# PSS_v2=PSS_v2.strip('\n').split(',')[-2]
					# print "方式二，获取PSS占用内存大小：{}KB".format(PSS_v2)

					# PSS_v2_list.append(int(PSS_v2))

					#**************提取dalvik heap占用内存大小*************
					Dalvik_info=os.popen('adb -s %s shell dumpsys meminfo %s | findstr Dalvik'%(device_name,packapgename)).readline().strip().split()
					logging.info('Dalvik为：{}'.format(Dalvik_info).encode('gbk'))
					logging.info('Dalvik拆分后长度为：{}'.format(len(Dalvik_info)).encode('gbk'))
					if system is "Windows":
						Dalvik_Heap_size=os.popen('adb -s %s shell dumpsys meminfo %s | findstr  Dalvik | gawk "{print $7}"'%(device_name,packapgename)).readline().strip('\n')
						Dalvik_Heap_Alloc_size=os.popen('adb -s %s shell dumpsys meminfo %s | findstr  Dalvik | gawk "{print $%d}"'%(device_name,packapgename,len(Dalvik_info)-1)).readline().strip('\n')
						Native_Heap_size=os.popen('adb -s %s shell dumpsys meminfo %s | findstr  Native | gawk "{print $7}"'%(device_name,packapgename)).readline().strip('\n')
					else:
						Dalvik_Heap_size=os.popen("adb -s %s shell dumpsys meminfo %s | grep  Dalvik | awk '{print $7}'"%(device_name,packapgename)).readline().strip('\n')
						Dalvik_Heap_Alloc_size=os.popen("adb -s %s shell dumpsys meminfo %s | grep  Dalvik | awk '{print $%d}'"%(device_name,packapgename,len(Dalvik_info)-1)).readline().strip('\n')
						Native_Heap_size=os.popen("adb -s %s shell dumpsys meminfo %s | grep  Native | awk '{print $7}'"%(device_name,packapgename)).readline().strip('\n')
					if system is "Windows":
						logging.info( "Dalvik Heap占用内存大小:{}KB".encode('gbk').format(Dalvik_Heap_size))
						logging.info( "Dalvik_Heap_Alloc占用内存大小:{}KB".encode('gbk').format(Dalvik_Heap_Alloc_size))
						logging.info( "Native Heap占用内存大小:{}KB".encode('gbk').format(Native_Heap_size))

					else:
						logging.info( "Dalvik Heap占用内存大小:{}KB".format(Dalvik_Heap_size))
						logging.info( "Dalvik_Heap_Alloc占用内存大小:{}KB".format(Dalvik_Heap_Alloc_size))
						logging.info( "Native Heap占用内存大小:{}KB".format(Native_Heap_size))

					#增加容错处理
					if len(str(Dalvik_Heap_size))==0 or Dalvik_Heap_size=='':
						Dalvik_Heap_size=0
					if len(str(Native_Heap_size))==0 or Native_Heap_size=='':
						Native_Heap_size=0
					if len(str(Dalvik_Heap_Alloc_size))==0 or Dalvik_Heap_Alloc_size=='':
						Dalvik_Heap_Alloc_size=0
						
					Dalvik_Heap_list.append(int(Dalvik_Heap_size))
					Native_Heap_list.append(int(Native_Heap_size))
					Dalvik_Heap_Alloc_list.append(int(Dalvik_Heap_Alloc_size))

					#*************************判断是否存在OOM内存泄露*****************************
					if int(Dalvik_Heap_size)>=int(heapgrowthlimit)*1024 or int(Dalvik_Heap_size)>=int(heapsize)*1024:
						raise AssertionError("dalvik heap size值超过最大限制，可能存在OOM内存泄露!")
					else:
						if system is "Windows": 
							logging.info( "获取单个应用程序最大内存限制:{} KB".encode('gbk').format(int(heapgrowthlimit)*1024))
							logging.info( "java虚拟机的最大内存限制:{} KB".encode('gbk').format(int(heapsize)*1024))
							logging.info( "dalvik heap size值没有超过最大限制！".encode('gbk'))
						else:
							logging.info( "获取单个应用程序最大内存限制:{} KB".format(int(heapgrowthlimit)*1024))
							logging.info( "java虚拟机的最大内存限制:{} KB".format(int(heapsize)*1024))
							logging.info( "dalvik heap size值没有超过最大限制！")

					#************************获取VSS和RSS内存信息*********************************
					if system is "Windows": 
						logging.info("*"*20+"获取VSS和RSS内存信息".encode('gbk')+"*"*20)
					else:
						logging.info("*"*20+"获取VSS和RSS内存信息"+"*"*20)
					HEAD=os.popen("adb -s {0} shell top -n 1 | {1} PID".format(device_name,find_util)).read()
					#获取HEAD字段显示
					# print HEAD
					#获取指定包名对应的那条top信息
					VSS_RSS_info=os.popen("adb -s {0} shell top -n 1 | {1} {2}".format(device_name,find_util,packapgename)).readline()
					# print VSS_RSS_info
					#提取VSS及RSS对应的值
					if system is "Windows":
						VSS=os.popen('adb -s %s shell top -n 1 | findstr %s|gawk "{print $6}"'%(device_name,packapgename)).readline()
						RSS=os.popen('adb -s %s shell top -n 1 | findstr %s|gawk "{print $7}"'%(device_name,packapgename)).readline()
					else:
						VSS=os.popen("adb -s %s shell top -n 1 | grep %s|awk '{print $6}'"%(device_name,packapgename)).readline()
						RSS=os.popen("adb -s %s shell top -n 1 | grep %s|awk '{print $7}'"%(device_name,packapgename)).readline()

					mode=re.compile(r'\d+')
					try:
						VSS=mode.findall(VSS)[0]
						RSS=mode.findall(RSS)[0]
					except IndexError:
						logging.info('索引异常,故赋值为0，VSS值为{},RSS值为:{}'.encode(str_encode).format(VSS,RSS))
						VSS=0
						RSS=0
					if system is "Windows": 
						logging.info( "VSS内存占用:{}KB".encode('gbk').format(VSS))
						logging.info( "RSS内存占用:{}KB".encode('gbk').format(RSS))
					else:
						logging.info( "VSS内存占用:{}KB".format(VSS))
						logging.info( "RSS内存占用:{}KB".format(RSS))
					VSS_list.append(int(VSS))
					RSS_list.append(int(RSS))

					times=times+1
					continue

				except Exception,e:
					print e

		try:
			print time_list,PSS_total_list,Priv_Dirty_total_list,PSS_Dalvik_list,Priv_Dirty_Dalvik_list,VSS_list,RSS_list,int(heapgrowthlimit)*1024,int(heapsize)*1024,MemTotal,MemFree,Dalvik_Heap_list,Native_Heap_list,Dalvik_Heap_Alloc_list
			
			return time_list,PSS_total_list,Priv_Dirty_total_list,PSS_Dalvik_list,Priv_Dirty_Dalvik_list,VSS_list,RSS_list,int(heapgrowthlimit)*1024,int(heapsize)*1024,MemTotal,MemFree,Dalvik_Heap_list,Native_Heap_list,Dalvik_Heap_Alloc_list
		except Exception,e:
			print e

	#获取设备ip地址，仅针对wifi
	def get_device_IP(self,device_name):
		if system is "Windows":
			ip=os.popen('adb -s %s shell netcfg | %s wlan0 |gawk "{print $3}"'%(device_name,find_util)).read().strip('\n').split('/')[0]	
		else:
			ip=os.popen("adb -s %s shell netcfg | %s wlan0 |awk '{print $3}'"%(device_name,find_util)).read().strip('\n').split('/')[0]
		return ip

	#判断指定设备，某进程运行状态，是否为前置应用
	def get_device_process_active(self,device_name,packapgename):
		current_activity=self.get_device_currentActivity(device_name)
		check_packagename=current_activity.split('/')[0]
		# print check_packagename

		process=os.popen("adb -s %s shell ps | %s %s"%(device_name,find_util,packapgename)).read().strip('\n')
		# print process

		if len(process)>0 and str(check_packagename)==str(packapgename):
			if system is "Windows":
				print "当前进程正在运行，且在前台激活窗口！".encode('gbk')
			else:
				print "当前进程正在运行，且在前台激活窗口！"
			return True
		else:
			if system is "Windows":
				print "当前进程没有打开或不为前置程序！".encode('gbk')
			else:
				print "当前进程没有打开或不为前置程序！"
			return False

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

	#获取CPU占用信息
	def get_device_cpu(self,device_name,packapgename,delay_time):

		time_list=[]
		cpu_precent_total_list=[]
		cpu_precent_user_list=[]
		cpu_precent_kernel_list=[]
		cpu_precent_v2_list=[]
		activity_list=[]
		cpu_frequency_list=[]
		cpu_temperature_list=[]

		#初始化采集次数为0，创建采集列表
		times=0
		times_list=[]

		while True:
			if int(delay_time)!=0:
				time.sleep(int(delay_time))
			current_time=time.strftime("%Y-%m-%d %H:%M:%S")
			d=datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S")
			#获取当前时间，把具体格式时间转换成秒数
			seconds_current=time.mktime(d.timetuple())
			seconds_current_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds_current))
			if system is "Windows":
				logging.info("获取开始运行的秒数:{}".encode('gbk').format(timeit))
				logging.info("获取当前运行的秒数:{}".encode('gbk').format(seconds_current))
				logging.info("获取开始的具体时间:{}".encode('gbk').format(current_time_format))
				logging.info("获取当前运行的具体时间:{}".encode('gbk').format(seconds_current_format))
			else:
				logging.info("获取开始运行的秒数:{}".format(timeit))
				logging.info("获取当前运行的秒数:{}".format(seconds_current))
				logging.info("获取开始的具体时间:{}".format(current_time_format))
				logging.info("获取当前运行的具体时间:{}".format(seconds_current_format))

			if int(seconds_current)>=int(seconds_end):
				if system is "Windows":
					logging.info("已达到最大指定运行时长,停止采集!".encode('gbk'))
					logging.info("当前已完成采集次数为:{}次".encode('gbk').format(times))
				else:
					logging.info("已达到最大指定运行时长,停止采集!")
					logging.info("当前已完成采集次数为:{}次".format(times))
				break

			else:

		# for i in xrange(int(times)):
				if system is "Windows":
					logging.info("*"*20+"第{}次开始CPU采样".encode('gbk').format(times+1)+"*"*20)
				else:
					logging.info("*"*20+"第{}次开始CPU采样".format(times+1)+"*"*20)
				_time=self.get_device_currenTime(device_name)
				if system is "Windows":
					logging.info("获取CPU时间:{}".encode('gbk').format(_time))
				else:
					logging.info("获取CPU时间:{}".format(_time))
				time_list.append(str(_time))

				#获取当前activity
				try:
					current_activity=self.get_device_currentActivity(device_name)
					activity_list.append(current_activity)
				except Exception,e:
					traceback.print_exc()

				#获取cpu温度
				cpu_count=self.get_cpu_kel(device_name)
				try:
					cpu_temperature=os.popen('adb -s {} shell cat /sys/class/thermal/thermal_zone{}/temp'.format(device_name,cpu_count)).read().strip()
					if 'Permission denied' in cpu_temperature:
						logging.info('获取CPU温度提示异常:{}'.encode(str_encode).format(cpu_temperature))
						window.printDarkRed('当前设备获取CPU温度时，提示获取异常Permission denied，故将温度赋值为0\n'.encode(str_encode))
						window.printWhite('')
						cpu_temperature=0    #如果无法获取CPU温度时（有些机型会存在Permission denied），则将CPU温度值赋值为0
					else:
						logging.info('CPU温度获取正常'.encode(str_encode))

				except Exception as e:
					logging.info('获取CPU温度提示异常:{}'.encode(str_encode).format(e))
					window.printDarkRed('当前设备获取CPU温度时，提示获取异常Permission denied，故将温度赋值为0\n'.encode(str_encode))
					window.printWhite('')
					cpu_temperature=0    #如果无法获取CPU温度时（有些机型会存在Permission denied），则将CPU温度值赋值为0
				else:
					#增加容错，如果CPU传感器的数量小于核数，则向下取1，如为8核CPU，但CPU8不存在， CPU7存在， 即取CPU7对应的传感器温度
					thermal_list=[]
					thermal_cmd='adb -s {} shell "cd /sys/class/thermal/&&ls"'.format(device_name)
					re_thermal_mode=re.compile(r'thermal_zone[0-9]')
					for i in os.popen(thermal_cmd).readlines():
						thermal_zone=re_thermal_mode.findall(i)
						if len(thermal_zone)>0:
							thermal_list.append(thermal_zone[-1])
					logging.info('{}'.format(thermal_list))
					if 'thermal_zone{}'.format(cpu_count) not in thermal_list:
						if 'thermal_zone{}'.format(cpu_count-1) in thermal_list:
							logging.info('从传感器thermal_zone{}采集温度!'.format(cpu_count-1).encode(str_encode))
							cpu_temperature=os.popen('adb -s {} shell cat /sys/class/thermal/thermal_zone{}/temp'.format(device_name,cpu_count-1)).read().strip()
					else:
						logging.info('从传感器thermal_zone{}采集温度！'.format(cpu_count).encode(str_encode))
				if len(str(cpu_temperature))>2:
					cpu_temperature=int(cpu_temperature)/1000.0
				logging.info('当前获取CPU温度为:{}℃'.format(cpu_temperature).encode(str_encode))
				cpu_temperature_list.append(cpu_temperature)

				#获取当前CPU使用频率
				cpu_frequency=os.popen('adb -s {} shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'.format(device_name)).read().strip()
				cpu_frequency=int(cpu_frequency)/1024    #由khz转换为mhz
				logging.info('当前使用频率为:{}mhz'.format(cpu_frequency).encode(str_encode))
				cpu_frequency_list.append(cpu_frequency)

				#方式一，通过adb dumpsys获取cpu
				if system is "Windows":
					if len(ext_)==0:
						cpu_info=os.popen("adb -s %s shell dumpsys cpuinfo | findstr %s | findstr -v pushservice | findstr -v remote |findstr -v support | findstr -v hotfix"%(device_name,packapgename)).readline().strip('\n').strip('\r')
						cpu_precent_total=os.popen('adb -s %s shell dumpsys cpuinfo | findstr %s | findstr -v pushservice | findstr -v remote |findstr -v support | findstr -v hotfix |gawk "{print $1}" '%(device_name,packapgename)).readline().strip('\n')
						cpu_precent_user=os.popen('adb -s %s shell dumpsys cpuinfo | findstr %s | findstr -v pushservice | findstr -v remote |findstr -v support | findstr -v hotfix |gawk "{print $3}" '%(device_name,packapgename)).readline().strip('\n')
						cpu_precent_kernel=os.popen('adb -s %s shell dumpsys cpuinfo | findstr %s | findstr -v pushservice | findstr -v remote |findstr -v support | findstr -v hotfix |gawk "{print $6}" '%(device_name,packapgename)).readline().strip('\n')
					else:
						cpu_info=os.popen("adb -s %s shell dumpsys cpuinfo | findstr %s"%(device_name,packapgename)).readline().strip('\n').strip('\r')
						cpu_precent_total=os.popen('adb -s %s shell dumpsys cpuinfo | findstr %s |gawk "{print $1}" '%(device_name,packapgename)).readline().strip('\n')
						cpu_precent_user=os.popen('adb -s %s shell dumpsys cpuinfo | findstr %s |gawk "{print $3}" '%(device_name,packapgename)).readline().strip('\n')
						cpu_precent_kernel=os.popen('adb -s %s shell dumpsys cpuinfo | findstr %s |gawk "{print $6}" '%(device_name,packapgename)).readline().strip('\n')

				else:
					if len(ext_)==0:
						cpu_info=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s | %s -v pushservice | %s -v remote|grep -v support | grep -v hotfix"%(device_name,find_util,packapgename,find_util,find_util)).readline().strip('\n')
						cpu_precent_total=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s | %s -v pushservice |awk '{print $1}'|grep -v support | grep -v remote| grep -v hotfix"%(device_name,find_util,packapgename,find_util)).readline().strip('\n')
						cpu_precent_user=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s | %s -v pushservice |awk '{print $3}' | grep -v support | grep -v remote | grep -v hotfix"%(device_name,find_util,packapgename,find_util)).readline().strip('\n')
						cpu_precent_kernel=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s | %s -v pushservice |awk '{print $6}'|grep -v support | grep -v remote | grep -v hotfix"%(device_name,find_util,packapgename,find_util)).readline().strip('\n')
					else:
						cpu_info=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s "%(device_name,find_util,packapgename)).readline().strip('\n')
						cpu_precent_total=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s |awk '{print $1}'"%(device_name,find_util,packapgename)).readline().strip('\n')
						cpu_precent_user=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s |awk '{print $3}' "%(device_name,find_util,packapgename)).readline().strip('\n')
						cpu_precent_kernel=os.popen("adb -s %s shell dumpsys cpuinfo | %s %s  |awk '{print $6}'"%(device_name,find_util,packapgename)).readline().strip('\n')


				if system is "Windows":
					logging.info(cpu_info.encode('gbk'))
					logging.info("进程占用的总的CPU百分比为:{}".encode('gbk').format(cpu_precent_total))
					logging.info("用户占用的CPU百分比为:{}".encode('gbk').format(cpu_precent_user))
					logging.info("内核占用的CPU百分比为:{}".encode('gbk').format(cpu_precent_kernel))
				else:
					logging.info(cpu_info)
					logging.info("进程占用的总的CPU百分比为:{}".format(cpu_precent_total))
					logging.info("用户占用的CPU百分比为:{}".format(cpu_precent_user))
					logging.info("内核占用的CPU百分比为:{}".format(cpu_precent_kernel))

				#增加容错处理
				if len(str(cpu_precent_total))==0 or cpu_precent_total=='':
					cpu_precent_total='0'
				if len(str(cpu_precent_user))==0 or cpu_precent_user=='':
					cpu_precent_user='0'
				if len(str(cpu_precent_kernel))==0 or cpu_precent_kernel=='':
					cpu_precent_kernel='0'

				cpu_precent_total=cpu_precent_total.strip('%')
				cpu_precent_total_list.append(eval(cpu_precent_total))
				cpu_precent_user=cpu_precent_user.strip('%')
				cpu_precent_user_list.append(eval(cpu_precent_user))
				cpu_precent_kernel=cpu_precent_kernel.strip('%')
				cpu_precent_kernel_list.append(eval(cpu_precent_kernel))

				#方式二，通过adb top获取cpu，取三次值
				if system is "Windows":
					if len(ext_)==0:
						cpu_top_info=os.popen("adb -s %s shell top -n 3 | findstr %s | findstr -v pushservice | findstr -v remote | findstr -v support | findstr -v hotfix"%(device_name,packapgename)).read().strip('\n')
						cpu_top=os.popen('adb -s %s shell top -n 3 | findstr %s | findstr -v pushservice | findstr -v remote | findstr -v support | findstr -v hotfix | gawk "{print $3}"'%(device_name,packapgename)).read().strip('\n')
					else:
						cpu_top_info=os.popen("adb -s %s shell top -n 3 | findstr %s "%(device_name,packapgename)).read().strip('\n')
						cpu_top=os.popen('adb -s %s shell top -n 3 | findstr %s | gawk "{print $3}"'%(device_name,packapgename)).read().strip('\n')

				else:
					if len(ext_)==0:
						cpu_top_info=os.popen("adb -s %s shell top -n 3 | grep %s | grep -v pushservice | grep -v remote | grep -v support | grep -v hotfix"%(device_name,packapgename)).read().strip('\n')
						cpu_top=os.popen("adb -s %s shell top -n 3 | grep %s | grep -v pushservice | grep -v remote | grep -v support | grep -v hotfix | awk '{print $3}'"%(device_name,packapgename)).read().strip('\n')
					else:
						cpu_top_info=os.popen("adb -s %s shell top -n 3 | grep %s "%(device_name,packapgename)).read().strip('\n')
						cpu_top=os.popen("adb -s %s shell top -n 3 | grep %s | awk '{print $3}'"%(device_name,packapgename)).read().strip('\n')

				#获取百分比数字
				mode=re.compile(r'\d+')
				temp=[]
				for i in cpu_top.split('\n'):
					temp.append(mode.findall(i)[0])
				#取三次中，最大的那次CPU占比值
				cpu_precent_v2=max(temp)
				cpu_precent_v2=cpu_precent_v2.strip('%')
				cpu_precent_v2_list.append(eval(cpu_precent_v2))
				if system is "Windows":
					logging.info("方式二，占用CPU百分比为:{}%".encode('gbk').format(cpu_precent_v2))
				else:
					logging.info( "方式二，占用CPU百分比为:{}%".format(cpu_precent_v2))
				times=times+1
				continue

		try:
			print cpu_precent_total_list,cpu_precent_user_list,cpu_precent_kernel_list,cpu_precent_v2_list,time_list,activity_list,cpu_temperature_list,cpu_frequency_list
			return cpu_precent_total_list,cpu_precent_user_list,cpu_precent_kernel_list,cpu_precent_v2_list,time_list,activity_list,cpu_temperature_list,cpu_frequency_list
		except Exception,e:
			print e


	#获取cpu核数
	def get_cpu_kel(self,device_name):
		cpu_process=[]
		cmd='adb shell "cd /sys/devices/system/cpu&&ls"'
		re_cpu_mode=re.compile(r'cpu[0-9]')
		for i in os.popen(cmd).readlines():
			cpu=re_cpu_mode.findall(i)
			if len(cpu)>0:
				cpu_process.append(cpu)
		# print len(cpu_process)
		return len(cpu_process)



	#获取电量信息
	def get_device_battery(self,device_name):
		battery=os.popen("adb -s {0} shell dumpsys battery | {1} level".format(device_name,find_util)).readline().strip('\n')
		# print battery
		mode=re.compile(r'\d+')
		try:
			battery=mode.findall(battery)[0]
		except IndexError:
			logging.info('电量获取索引异常,故赋值为0，battery:{}'.encode(str_encode).format(battery))
			battery=0
		if system is "Windows":
			logging.info("当前电量值为:{}".encode('gbk').format(battery))
		else:
			logging.info("当前电量值为:{}".format(battery))
		return battery


	#获取流量信息
	def get_device_net(self,device_name,packapgename,delay_time):
		# times=10
		try:
			net_wifi_rcv_list=[]
			net_wifi_send_list=[]
			net_wifi_rcv_packets_list=[]
			net_wifi_send_packets_list=[]
			_net2_rx_bytes_list=[]
			_net2_tx_bytes_list=[]
			time_list=[]

			#初始化采集次数为0，创建采集列表
			times=0
			times_list=[]

			while True:
				if int(delay_time)!=0:
					time.sleep(int(delay_time))
				current_time=time.strftime("%Y-%m-%d %H:%M:%S")
				d=datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S")
				#把具体格式时间转换成秒数
				seconds_current=time.mktime(d.timetuple())
				seconds_current_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds_current))

				if system is "Windows":
					logging.info("获取开始运行的秒数:{}".encode('gbk').format(timeit))
					logging.info("获取当前运行的秒数:{}".encode('gbk').format(seconds_current))
					logging.info("获取开始的具体时间:{}".encode('gbk').format(current_time_format))
					logging.info("获取当前运行的具体时间:{}".encode('gbk').format(seconds_current_format))
				else:
					logging.info("获取开始运行的秒数:{}".format(timeit))
					logging.info("获取当前运行的秒数:{}".format(seconds_current))
					logging.info("获取开始的具体时间:{}".format(current_time_format))
					logging.info("获取当前运行的具体时间:{}".format(seconds_current_format))

				if int(seconds_current)>=int(seconds_end):
					if system is "Windows":
						logging.info("已达到最大指定运行时长,停止采集!".encode('gbk'))
						logging.info("当前已完成采集次数为:{}次".encode('gbk').format(times))
					else:
						logging.info("已达到最大指定运行时长,停止采集!")
						logging.info("当前已完成采集次数为:{}次".format(times))
					break

			# for i in xrange(int(times)):
				else:
					if system is "Windows":
						logging.info("*"*20+"第{}次开始流量采样".encode('gbk').format(times+1)+"*"*20)
					else:
						logging.info("*"*20+"第{}次开始流量采样".format(times+1)+"*"*20)

					time.sleep(1)

					_time=self.get_device_currenTime(device_name)
					if system is "Windows":
						logging.info("获取流量时间:{}".encode('gbk').format(_time))
					else:
						logging.info("获取流量时间:{}".format(_time))
					time_list.append(str(_time))
					if system is "Windows":
						pid=os.popen('adb -s %s shell ps | findstr %s | gawk "{print $2}"'%(device_name,packapgename)).read()
					else:
						pid=os.popen("adb -s %s shell ps | grep %s | awk '{print $2}'"%(device_name,packapgename)).read()

					try:
						pid=pid.split()[0]
					except IndexError:
						logging.info('pid获取异常!pid值为:{}'.encode(str_encode).format(pid))
						pass

					if system is "Windows":
						logging.info("包名为{0}==>对应的PID为:{1}".encode('gbk').format(packapgename,pid))
					else:
						logging.info("包名为{0}==>对应的PID为:{1}".format(packapgename,pid))

					#方式一，**********通过PID的方式，获取对应PID下的wifi网络对应的流量信息*****************
					net_wifi_info=os.popen("adb -s {0} shell cat /proc/{1}/net/dev|{2} wlan0".format(device_name,pid,find_util)).read().strip('\n')
					if system is "Windows":
						logging.info("adb shell cat /proc/+Pid+/net/dev获取到的流量信息为:{}".encode('gbk').format(net_wifi_info))
					else:
						logging.info("adb shell cat /proc/+Pid+/net/dev获取到的流量信息为:{}".format(net_wifi_info))
					if system is "Windows":
						net_wifi_rcv=os.popen('adb -s %s shell cat /proc/%s/net/dev|findstr wlan0 | gawk "{print $2}"'%(device_name,pid)).read().strip('\n')
						net_wifi_rcv_packets=os.popen('adb -s %s shell cat /proc/%s/net/dev|findstr wlan0 | gawk "{print $3}"'%(device_name,pid)).read().strip('\n')			
						net_wifi_send=os.popen('adb -s %s shell cat /proc/%s/net/dev|findstr wlan0 | gawk "{print $10}"'%(device_name,pid)).read().strip('\n')
						net_wifi_send_packets=os.popen('adb -s %s shell cat /proc/%s/net/dev|findstr wlan0 | gawk "{print $11}"'%(device_name,pid)).read().strip('\n')
					else:
						net_wifi_rcv=os.popen("adb -s %s shell cat /proc/%s/net/dev|grep wlan0 | awk '{print $2}'"%(device_name,pid)).read().strip('\n')
						net_wifi_rcv_packets=os.popen("adb -s %s shell cat /proc/%s/net/dev|grep wlan0 | awk '{print $3}'"%(device_name,pid)).read().strip('\n')			
						net_wifi_send=os.popen("adb -s %s shell cat /proc/%s/net/dev|grep wlan0 | awk '{print $10}'"%(device_name,pid)).read().strip('\n')
						net_wifi_send_packets=os.popen("adb -s %s shell cat /proc/%s/net/dev|grep wlan0 | awk '{print $11}'"%(device_name,pid)).read().strip('\n')

					#增加容错处理
					if len(str(net_wifi_rcv))==0 or net_wifi_rcv=='':
						net_wifi_rcv=0

					if len(str(net_wifi_send))==0 or net_wifi_send=='':
						net_wifi_send=0

					if len(str(net_wifi_rcv_packets))==0 or net_wifi_rcv_packets=='':
						net_wifi_rcv_packets=0

					if len(str(net_wifi_send_packets))==0 or net_wifi_send_packets=='':
						net_wifi_send_packets=0


					net_wifi_rcv=int(net_wifi_rcv)/1024
					net_wifi_send=int(net_wifi_send)/1024
					net_wifi_rcv_packets=int(net_wifi_rcv_packets)/1024
					net_wifi_send_packets=int(net_wifi_send_packets)/1024

					net_wifi_rcv_list.append(int(net_wifi_rcv))
					net_wifi_send_list.append(int(net_wifi_send))
					net_wifi_rcv_packets_list.append(int(net_wifi_rcv_packets))
					net_wifi_send_packets_list.append(int(net_wifi_send_packets))
					if system is "Windows":
						logging.info("当前通过adb shell cat /proc/+Pid+/net/dev接收的字节数为:{}KB".encode('gbk').format(net_wifi_rcv))
						logging.info("当前通过adb shell cat /proc/+Pid+/net/dev发送的字节数为:{}KB".encode('gbk').format(net_wifi_send))
						logging.info("当前通过adb shell cat /proc/+Pid+/net/dev接收的数据包大小为:{}KB".encode('gbk').format(net_wifi_rcv_packets))
						logging.info("当前通过adb shell cat /proc/+Pid+/net/dev发送的数据包大小为:{}KB".encode('gbk').format(net_wifi_send_packets))
					else:
						logging.info("当前接收的字节数为:{}KB".format(net_wifi_rcv))
						logging.info("当前发送的字节数为:{}KB".format(net_wifi_send))
						logging.info("当前接收的数据包大小为:{}KB".format(net_wifi_rcv_packets))
						logging.info("当前发送的数据包大小为:{}KB".format(net_wifi_send_packets))


					#方式二，*****************通过UID的方式来获取从开机后总的流量信息******************************
					if system is "Windows":
						uid=os.popen('adb -s %s shell cat /proc/%s/status | findstr Uid | gawk "{print $2}"'%(device_name,pid)).read()
					else:
						uid=os.popen("adb -s %s shell cat /proc/%s/status | grep Uid | awk '{print $2}'"%(device_name,pid)).read()
					if system is "Windows":
						logging.info("进程PID:{0}对应的UID号为:{1}".encode('gbk').format(pid,uid))
					else:
						logging.info("进程PID:{0}对应的UID号为:{1}".format(pid,uid))

					#通过UID的方式，来获取对应UID下的流量信息
					net2=os.popen("adb -s {0} shell cat /proc/net/xt_qtaguid/stats | {1} {2}".format(device_name,find_util,uid)).read().strip('\n')
					if system is 'Windows':
						logging.info("通过adb shell cat /proc/net/xt_qtaguid/stats获取到的流量信息为:{}".encode('gbk').format(net2))

					#计算wifi接收数据流量,包含tcp，udp等所有网络流量传输的统计,第6列为接收数据
					if system is "Windows":
						net2_rx_bytes=os.popen('adb -s %s shell cat /proc/net/xt_qtaguid/stats | gawk "{print $2,$4,$6}"| findstr wlan0 | findstr %s'%(device_name,uid)).readlines()
					else:
						net2_rx_bytes=os.popen("adb -s %s shell cat /proc/net/xt_qtaguid/stats | awk '{print $2,$4,$6}'| grep wlan0 | grep %s"%(device_name,uid)).readlines()

					net2_rx_bytes_list=[]
					for i in net2_rx_bytes:
						net2_rx_bytes_list.append(int(i.strip('\n').split()[-1]))

					net2_rx_bytes=sum(net2_rx_bytes_list)/1024
					if system is "Windows":
						logging.info("通过adb shell cat /proc/net/xt_qtaguid/stats 统计开机后App所有接收数据流量大小为:{}KB".encode('gbk').format(net2_rx_bytes))
					else:
						logging.info("通过adb shell cat /proc/net/xt_qtaguid/stats 统计开机后App所有接收数据流量大小为:{}KB".format(net2_rx_bytes))
					_net2_rx_bytes_list.append(int(net2_rx_bytes))


					#计算wifi发送数据流量,包含tcp，udp等所有网络流量传输的统计,第8列为发送数据
					if system is "Windows":

						net2_tx_bytes=os.popen('adb -s %s shell cat /proc/net/xt_qtaguid/stats | gawk "{print $2,$4,$8}"| findstr wlan0 | findstr %s'%(device_name,uid)).readlines()
					else:
						net2_tx_bytes=os.popen("adb -s %s shell cat /proc/net/xt_qtaguid/stats | awk '{print $2,$4,$8}'| grep wlan0 | grep %s"%(device_name,uid)).readlines()

					net2_tx_bytes_list=[]
					for i in net2_tx_bytes:
						net2_tx_bytes_list.append(int(i.strip('\n').split()[-1]))

					net2_tx_bytes=sum(net2_tx_bytes_list)/1024
					if system is "Windows":
						logging.info("通过adb shell cat /proc/net/xt_qtaguid/stats 统计开机后App所有发送数据流量大小为:{}KB".encode('gbk').format(net2_tx_bytes))
					else:
						logging.info("通过adb shell cat /proc/net/xt_qtaguid/stats 统计开机后App发送数据流量大小为:{}KB".format(net2_tx_bytes))

					_net2_tx_bytes_list.append(int(net2_tx_bytes))
					times=times+1
					continue

		except Exception,e:
			traceback.print_exc()
		try:
			print time_list,net_wifi_rcv_list,net_wifi_send_list,net_wifi_rcv_packets_list,net_wifi_send_packets_list,_net2_rx_bytes_list,_net2_tx_bytes_list
			return time_list,net_wifi_rcv_list,net_wifi_send_list,net_wifi_rcv_packets_list,net_wifi_send_packets_list,_net2_rx_bytes_list,_net2_tx_bytes_list
		except Exception, e:
			traceback.print_exc()


	#获取设备分辨率：
	def get_device_display(self,device_name):
		display=os.popen("adb -s {0} shell dumpsys display | {1} DisplayDeviceInfo".format(device_name,find_util)).read()
		# print display
		mode=re.compile(r'\d+ x \d+')   #提取屏幕分辨率
		try:
			display= mode.findall(display.strip('\n'))[0]
		except IndexError:
			logging.info('display获取索引异常{}'.encode(str_encode).format(display))
		# print "屏幕分辨率大小为:",display
		return display	

	#获取当前手机时刻时间
	def get_device_currenTime(self,device_name):
		year='%Y/%m/%d'
		now='%H:%M:%S'
		year=os.popen('adb -s {0} shell date +{1}'.format(device_name,year)).read()
		now=os.popen('adb -s {0} shell date +{1}'.format(device_name,now)).read()
		time_="{0} {1}".format(year.strip('\r\n'),now.strip('\r\n'))

		#如果没有获取到手机时间，则尝试获取本机电脑时间
		if ':' not in str(time_):
			time_=time.strftime('%Y/%m/%d %H:%M:%S')
		return time_

	#获取设备当前界面Activity信息
	def get_device_currentActivity(self,device_name):
		activity_top_current=os.popen("adb -s {0} shell dumpsys activity top | {1} ACTIVITY".format(device_name,find_util)).read()
		# print activity_top_current.strip('\n')
		try:
			activity_top_current=activity_top_current.split()[1]
		except Exception as e:
			pass
		if system is "Windows":
			print "获取当前界面的Activity:".encode('gbk'),activity_top_current
		else:
			print "获取当前界面的Activity:",activity_top_current
		return activity_top_current	


	#获取设备平台版本号
	def get_platformVersion(self,device_name):
		command='adb -s {}shell cat /system/build.prop'.format(device_name)  #方法一，获取android系统属性
		command1='adb -s {} shell getprop'.format(device_name)    #方法二，通过getprop获取android系统属性


		platform_version_cmd='%s ro.build.version.release'%command1

		platform_version = subprocess.Popen(platform_version_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return platform_version.stdout.read().strip()

	#获取手机设备信息
	def get_phone_Msg(self,device_name):
	    os.system('adb -s {} shell cat /system/build.prop >log.txt'.format(device_name)) #存放的手机信息
	    l_list = []
	    f = open("log.txt", "r")
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
	    f.close()

	    l_list.append(self.get_device_display(device_name))
	    l_list.append(device_name)
	    try:
		    device_name=l_list[-1].strip('\n')
		    device_version=l_list[0].strip('\n')
		    device_name=l_list[1].strip('\n')
		    device_brand=l_list[2].strip('\n')
		    device_display=l_list[3].strip('\n')
	    except  IndexError:
			logging.info('获取手机信息失败:{}'.encode(str_encode).format(l_list))
			device_brand=''

	    # print "手机名称:",device_name
	    # print "手机品牌：",device_brand
	    # print "手机版本:",device_version
	    # print "手机分辨率:",device_display
	    # print "手机序列号为:",device_name
	    # print l_list
	    return l_list


	#获取帧率
	def get_device_fps(self,device_name,packapgename,delay_time):
		# times=10
		frames_list=[]
		seconds_list=[]
		fps_list=[]
		time_list=[]
		activity_list=[]
		#初始化采集次数为0，创建采集列表
		times=0
		times_list=[]
		time_list2=[]
		time_list3=[]
		Draw_list=[]
		Prepare_list=[]
		Process_list=[]
		Execute_list=[]
		sum_time_line_list=[]
		flag_list=[]
		fps_per_list=[]


		try:
			l_list=self.get_phone_Msg(device_name)   #获取设备版本号
			logging.info('手机设备信息==>:{}'.format(l_list).encode(str_encode))
			while True:
				import time
				if int(delay_time)!=0:
					time.sleep(int(delay_time))
				current_time=time.strftime("%Y-%m-%d %H:%M:%S")
				d=datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S")
				#获取当前时间，把具体格式时间转换成秒数
				seconds_current=time.mktime(d.timetuple())
				seconds_current_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds_current))

				if system is "Windows":
					logging.info("获取开始运行的秒数:{}".encode('gbk').format(timeit))
					logging.info("获取当前运行的秒数:{}".encode('gbk').format(seconds_current))
					logging.info("获取开始的具体时间:{}".encode('gbk').format(current_time_format))
					logging.info("获取当前运行的具体时间:{}".encode('gbk').format(seconds_current_format))
				else:
					logging.info("获取开始运行的秒数:{}".format(timeit))
					logging.info("获取当前运行的秒数:{}".format(seconds_current))
					logging.info("获取开始的具体时间:{}".format(current_time_format))
					logging.info("获取当前运行的具体时间:{}".format(seconds_current_format))

				if int(seconds_current)>=int(seconds_end):
					if system is "Windows":
						logging.info("已达到最大指定运行时长,停止采集!".encode('gbk'))
						logging.info("当前已完成采集次数为:{}次".encode('gbk').format(times))
					else:
						logging.info("已达到最大指定运行时长,停止采集!")
						logging.info("当前已完成采集次数为:{}次".format(times))
					break

				else:
			# for i in xrange(int(times)):
					if system is "Windows":
						logging.info("*"*20+"第{}次开始fps采样".encode('gbk').format(times+1)+"*"*20)
					else:
						logging.info("*"*20+"第{}次开始fps采样".format(times+1)+"*"*20)
					_time=self.get_device_currenTime(device_name)
					# _time=time.strftime("%Y/%m/%d %H:%M:%S")
					if system is "Windows":
						logging.info("获取fps时间:{}".encode('gbk').format(_time))
					else:
						logging.info("获取fps时间:{}".format(_time))

					time_list.append(str(_time))

					#获取当前activity
					try:
						current_activity=self.get_device_currentActivity(device_name)
						activity_list.append(current_activity)
					except Exception,e:
						traceback.print_exc()

					# 流畅度阈值的界定：按官网的建议每秒小于60帧就能感觉到不流畅，也就是说每帧的阈值=1000/60 =16ms
					#将命令返回的所有数据保存到gfxinfo.log文件中
					fps=os.popen('adb -s {0} shell dumpsys gfxinfo {1}>gfxinfo.log'.format(device_name,packapgename)).read()
					with open("gfxinfo.log", "r") as f:
						content=f.read().split('Profile data in ms')
                        # content=content[-1].split('View hierarchy')[0].strip('\r\n')
                        #小米5出现数据格式不一致的问题， 需增加过滤Stats since字段内容
						content=content[-1].split('View hierarchy')[0].strip('\r\n').split('Stats since')[0].strip(('\r\n'))

						##兼容oppo机型
						content=content.replace('/android.view.ViewRootImpl@42901ac8','').strip()
						content=content.replace('/android.view.ViewRootImpl@4293ebf0','').strip()
						content=content.replace('/android.view.ViewRootImpl@42943a50','').strip()

					#取出所有帧数值，保存到gfxinfo_bak.log文件中
					with open("gfxinfo_bak.log",'w') as f:
						f.write(content.split('Execute')[-1].strip('\r\n'))

					with open("gfxinfo_bak.log",'r') as f:
						frames=f.readlines()
						f.seek(0)
						if len(frames)>0:
							_time=self.get_device_currenTime(device_name)
							time_list2.append(_time)   #记录当获取到有效帧数的手机时间
							if system is "Windows":
								Draw=os.popen('type gfxinfo_bak.log|gawk "{print $1}"').read()
								Process=os.popen('type gfxinfo_bak.log|gawk "{print $3}"').read()
								Execute=os.popen('type gfxinfo_bak.log|gawk "{print $4}"').read()
							else:
								Draw=os.popen("cat gfxinfo_bak.log|awk '{print $1}'").read()
								Process=os.popen("cat gfxinfo_bak.log|awk '{print $3}'").read()
								Execute=os.popen("cat gfxinfo_bak.log|awk '{print $4}'").read()
							Draw=Draw.split()
							Process=Process.split()
							Execute=Execute.split()
							#命令返回的每一行代表一帧，计算帧数量
							frames_len=len(frames)
							if system is "Windows":
								logging.info("计算帧的数量为:{}".encode('gbk').format(frames_len))
							else:
								logging.info("计算帧的数量为:{}".format(frames_len))

							frames_list.append(frames_len)

							#***********计算每一帧耗费的时间并生成新的数组，单位：s**************
							'''下述的循环体中代码，运行过程较耗时'''

							frame_time=[]
							for i in xrange(len(frames)):
								time = frames[i].split()
								times_list.append(times+1)   #记录采集序号
								# android 5.1.1中每一帧有四列数据：Draw  Prepare  Process  Execute
								l_list=self.get_phone_Msg(device_name)   #获取设备版本号
								version=l_list[0].strip('\r\n')
								version=version[:3]  #防止版本号获取回来为三位数字如4.4.2，此时通过切片，只取前面两位如4.4

								#判断取回来的版本号是否为数字，如果非数字，则重新从列表中取值
								if version[0].isdigit():
									pass
								else:
									version=l_list[2].strip('\r\n')   #获取列表第3个元素作为版本号
									version=version[:3]
								if float(version)>=5.1:
									#计算每一帧（即第一行）的耗时，单位ms
									sum_time_line=(float(time[0])+float(time[1])+float(time[2])+float(time[3]))
									#用于存放每帧耗时ms的列表
									sum_time_line_list.append(sum_time_line)
									if sum_time_line>=16.0:
										flag='Fail'
									else:
										flag='Pass'
									#用于存放是否大于16.6ms的标记列表
									flag_list.append(flag)

									try:
										Draw_list.append(float(time[0]))
										Prepare_list.append(float(time[1]))
										Process_list.append(float(time[2]))
										Execute_list.append(float(time[3]))
									except IndexError:
										print time
									sum_time = (float(time[0])+float(time[1])+float(time[2])+float(time[3]))/1000
									frame_time.append(sum_time)
									# print frame_time

								else:

									try:
										sum_time_line=float(time[0])+float(time[1])+float(time[2])
									except IndexError:
										sum_time_line=0
									sum_time_line_list.append(sum_time_line)
									if sum_time_line>=16.0:
										flag='Fail'
									else:
										flag='Pass'

									flag_list.append(flag)

									try:
										Draw_list.append(float(time[0]))
									except IndexError:
										print time
									try:
										Process_list.append(float(time[1]))
									except IndexError:
										print time
									try:
										Execute_list.append(float(time[2]))
									except IndexError:
										print time

									sum_time = (float(time[0])+float(time[1])+float(time[2]))/1000

									frame_time.append(sum_time)

							#*********计算frames总共耗费的时间：s***************
							seconds = 0.0
							for i in frame_time:
								seconds += i
							if system is "Windows":
								logging.info("耗时:%s秒".encode('gbk')%seconds)
							else:
								logging.info("耗时:%s秒"%seconds)
							seconds_list.append(seconds)

							#****************计算帧率，每隔1s取一次数据，fps = frames/seconds(帧的总数/耗时时间)************
							fps=float('%.2f'%(float(frames_len/seconds)))
							if system is "Windows":
								logging.info("fps帧率为:{}".encode('gbk').format(fps))
							else:
								logging.info("fps帧率为:{}".format(fps))
							fps_list.append(fps)

							times=times+1
							continue

						else:
							if system is "Windows":
								logging.info("没有获取到帧数,请滑动页面！或检查 开发者选项-》GPU呈现模式分析是否打开!".encode('gbk'))
							else:
								logging.info("没有获取到帧数,请滑动页面！或检查 开发者选项-》GPU呈现模式分析是否打开!")
							times=times+1
							continue

		except Exception,e:
			traceback.print_exc()
		try:
			l_list=self.get_phone_Msg(device_name)   #获取设备版本号
			version=l_list[0].strip('\r\n')
			version=version[:3]  #防止版本号获取回来为三位数字如4.4.2，此时通过切片，只取前面两位如4.4

			if version[0].isdigit():   #判断取回来的版本号是否为数字，如果非数字，则重新从列表中取值
				pass
			else:
				version=l_list[2].strip('\r\n')   #获取列表第3个元素作为版本号
				version=version[:3]

			if float(version)<5.1:
				Prepare_list=['NA']*len(Draw_list)

			#生成有效采集序号对应的时间列表
			from collections import Counter
			times=dict(Counter(times_list)).values()
			logging.info('采集序号与次数映射关系:{}'.format(dict(Counter(times_list))).encode(str_encode))
			logging.info('采集序号次数与获取时间映射关系:{}'.format(zip(time_list2,times)).encode(str_encode))
			for k,v in zip(time_list2,times):
				for i in range(v):
					time_list3.append(k)

			#生成有效采集序号对应的平均帧率列表
			from collections import Counter
			times=dict(Counter(times_list)).values()
			logging.info('采集序号与次数映射关系:{}'.format(dict(Counter(times_list))).encode(str_encode))
			logging.info('采集序号与平均帧率映射关系:{}'.format(zip(fps_list,times)).encode(str_encode))
			for k,v in zip(fps_list,times):
				for i in range(v):
					fps_per_list.append(k)

			print time_list,frames_list,seconds_list,fps_list
			return time_list,frames_list,seconds_list,fps_list,activity_list,times_list,Draw_list,Prepare_list,Process_list,Execute_list,sum_time_line_list,flag_list,time_list3,fps_per_list
		except Exception,e:
			traceback.print_exc()

	#获取设备当前电量、电压、温度
	def get_device_battery_info(self,device_name,delay_time):
		battery_list=[]
		voltage_list=[]
		temperature_list=[]
		usb_powered_list=[]
		wifi_powered_list=[]
		activity_list=[]
		time_list=[]

		#初始化采集次数为0，创建采集列表
		times=0
		times_list=[]
		l_list=self.get_platformVersion(device_name)   #获取设备版本号
		version=l_list[0].strip('\r\n')

		#**********获取设备电池毫安mAh数，仅支持5.0以上系统****************
		if eval(version)>=5.0:
			if system is "Windows":
				batterystats=os.popen('adb -s %s shell dumpsys batterystats | findstr Capacity |gawk "{print $2}"'%(device_name)).read()
				if len(str(batterystats))>0:
					batterystats=batterystats.split('\n')[0]
					mode=re.compile(r'\d+')
					Capacity=mode.findall(batterystats)[0]   #提取当前设备电池mAh容量
					logging.info("当前设备电池容量为:{} mAh".encode('gbk').format(Capacity))
				else:
					logging.info("当前设备无法获取电池mAh值！！！".encode('gbk'))
					Capacity='NA'
			else:
				batterystats=os.popen('adb -s %s shell dumpsys batterystats | grep Capacity |awk "{print $2}"'%(device_name)).read()
				if len(str(batterystats))>0:
					batterystats=batterystats.split('\n')[0]
					mode=re.compile(r'\d+')
					Capacity=mode.findall(batterystats)[0]   #提取当前设备电池mAh容量
					logging.info("当前设备电池容量为:{} mAh".format(Capacity))
				else:
					logging.info("当前设备无法获取电池mAh值！！！")
					Capacity='NA'
		else:
			if system is "Windows":
				logging.info("当前系统版本过低，小于5.0版本，不支持获取mAh值!".encode('gbk'))
				Capacity='NA'
			else:
				logging.info("当前系统版本过低，小于5.0版本，不支持获取mAh值!")
				Capacity='NA'


		while True:
			#如果delay_time不为0，则增加获取延迟
			if int(delay_time)!=0:
				time.sleep(int(delay_time))
			current_time=time.strftime("%Y-%m-%d %H:%M:%S")
			d=datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S")
			#获取当前时间，把具体格式时间转换成秒数
			seconds_current=time.mktime(d.timetuple())
			seconds_current_format=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds_current))
			#比较当前时间对应的秒数是否超过指定运行时长的最大值
			if int(seconds_current)>=int(seconds_end):
				if system is "Windows":
					logging.info("已达到最大指定运行时长,停止采集!".encode('gbk'))
					logging.info("当前已完成采集次数为:{}次".encode('gbk').format(times))
				else:
					logging.info("已达到最大指定运行时长,停止采集!")
					logging.info("当前已完成采集次数为:{}次".format(times))
				break

			else:
			# for i in xrange(int(times)):
				if system is "Windows":
					logging.info("*"*20+"第{}次开始电量、电压、温度采样".encode('gbk').format(times+1)+"*"*20)
				else:
					logging.info("*"*20+"第{}次开始电量、电压、温度采样".format(times+1)+"*"*20)
				_time=self.get_device_currenTime(device_name)
				if system is "Windows":
					logging.info("获取电量、电压、温度时间:{}".encode('gbk').format(_time))
				else:
					logging.info("获取电量、电压、温度时间:{}".format(_time))
				time_list.append(str(_time))

				#获取当前activity
				try:
					current_activity=self.get_device_currentActivity(device_name)
					activity_list.append(current_activity)
				except Exception,e:
						traceback.print_exc()

				battery=os.popen("adb -s {0} shell dumpsys battery | {1} level".format(device_name,find_util)).readline().strip('\n')
				voltage=os.popen("adb -s {0} shell dumpsys battery | {1} voltage".format(device_name,find_util)).readline().strip('\n')
				temperature=os.popen("adb -s {0} shell dumpsys battery | {1} temperature".format(device_name,find_util)).readline().strip('\n')
				usb_powered=os.popen("adb -s {0} shell dumpsys battery | {1} USB".format(device_name,find_util)).readline().strip('\n')
				wifi_powered=os.popen("adb -s {0} shell dumpsys battery | {1} Wireless".format(device_name,find_util)).readline().strip('\n')
				mode=re.compile(r'\d+')

				try:
					battery=mode.findall(battery)[0]
				except IndexError:
					battery=0
				try:
					voltage=mode.findall(voltage)[0]
				except IndexError:
					voltage=0
				try:
					temperature=mode.findall(temperature)[0]
				except IndexError:
					temperature=0

				usb_powered=usb_powered.split(':')[-1].strip()
				wifi_powered=wifi_powered.split(':')[-1].strip()
				battery_list.append(int(battery))
				voltage_list.append(int(voltage))
				temperature_list.append(int(temperature))
				usb_powered_list.append(usb_powered)
				wifi_powered_list.append(wifi_powered)
				if system is "Windows":
					logging.info("当前电量值为:{}".encode('gbk').format(battery))
					logging.info("当前电压值为:{}".encode('gbk').format(voltage))
					logging.info("当前温度值为:{}".encode('gbk').format(temperature))
					logging.info("当前usb供电是否开启:{}".encode('gbk').format(usb_powered))
					logging.info("当前wifi供电是否开启:{}".encode('gbk').format(wifi_powered))
				else:
					logging.info("当前电量值为:{}".format(battery))
					logging.info("当前电压值为:{}".format(voltage))
					logging.info("当前温度值为:{}".format(temperature))
					logging.info("当前usb供电是否开启:{}".format(usb_powered))
					logging.info("当前wifi供电是否开启:{}".format(wifi_powered))
				times=times+1
				continue
		try:
			print battery_list,voltage_list,temperature_list,activity_list,time_list,usb_powered_list,wifi_powered_list,Capacity
			return battery_list,voltage_list,temperature_list,activity_list,time_list,usb_powered_list,wifi_powered_list,Capacity
		except Exception,e:
			traceback.print_exc()



class ResultReport(object):

	def __init__(self,report_name):
		self.android=Android_Permance()
		# global report_name
		#Debug开关用于调试功能时用
		if Debug==False:
			# report_name='android_permance_report.xlsx'
			report_name='{}.xlsx'.format(report_name)
			self.workbook = xlsxwriter.Workbook(report_name)
			self.report_path=os.path.abspath(os.getcwd())
			# print report_path
		else:
			#获取创建报告时间
			creat_time=time.strftime("%Y_%m_%d_%H_%M_%S")
			#创建excel图表
			# report_name='android_permance_report_{}.xlsx'.format(creat_time)
			report_name='{}.xlsx'.format(report_name)
			self.workbook = xlsxwriter.Workbook(report_name)
			self.report_path=os.path.abspath(os.getcwd())
			# print report_path


	def __str__(self):
		print "开始生成图表报告"

	#生成内存资源报告
	def gen_memory_report(self,device_name,packapgename,times):
		device_info=self.android.get_phone_Msg(device_name)   #获取手机信息
		ip=self.android.get_device_IP(device_name)   #获取设备wifi ip
		battery=self.android.get_device_battery(device_name)   #获取当前电量值，因存在usb充电，此值仅供参考
		app_version=self.android.getAppVersion(device_name,packapgename)  #获取软件版本号

		time_list,PSS_total_list,Priv_Dirty_total_list,PSS_Dalvik_list,Priv_Dirty_Dalvik_list,VSS_list,RSS_list,heapgrowthlimit,heapsize,MemTotal,MemFree,\
		Dalvik_Heap_list,Native_Heap_list,Dalvik_Heap_Alloc_list=self.android.get_device_memInfo(device_name,packapgename,times)   #获取内存值消耗

		_time_list=[]
		for time in time_list:

			#分割时间，去掉日期，只取时间
			time=time.split()[-1]
			_time_list.append(time)

		#************判断内存是否存在内存泄露****************
		'''原理： Dalvik 的 Heap 信息中的alloc（即Java层的内存分配情况），如果发现这个值一直增长，则代表程序可能出现了内存泄漏'''
		logging.info('开始分析是否存在内存泄露'.encode(str_encode))
		memory_leak_flag=all(x<y for x, y in zip(Dalvik_Heap_Alloc_list, Dalvik_Heap_Alloc_list[1:]))
		if memory_leak_flag==True and len(Dalvik_Heap_Alloc_list)>=5:
			memory_leak_flag_text='发现内存泄露'
			if system is 'Windows':
				window.printRed('检测到Dalvik_Heap_Alloc内存分配一直在持续增涨，可能存在内存泄露，请检查！\n'.encode(str_encode))
				logging.info('检测到Dalvik_Heap_Alloc内存分配一直在持续增涨，可能存在内存泄露，请检查！'.encode(str_encode))
				window.printWhite('')
				print '*'*25+'Dalvik_Heap_Alloc'+'*'*25
				for i in Dalvik_Heap_Alloc_list:
					print i

			else:
				styles.RED+'检测到Dalvik_Heap_Alloc内存分配一直在持续增涨，可能存在内存泄露，请检查！\n'.encode(str_encode)+styles.ENDC
				logging.info('检测到Dalvik_Heap_Alloc内存分配一直在持续增涨，可能存在内存泄露，请检查！'.encode(str_encode))
				print '*'*25+'Dalvik_Heap_Alloc'+'*'*25
				for i in Dalvik_Heap_Alloc_list:
					print i
		else:
			memory_leak_flag_text='未检查到内存泄露'
			if system is 'Windows':
				window.printGreen('未检测到程序内存泄露!\n'.encode(str_encode))
				logging.info('未检测到程序内存泄露!'.encode(str_encode))
				window.printWhite('')
			else:
				styles.GREEN+'未检测到程序内存泄露!\n'.encode(str_encode)+styles.ENDC
				logging.info('未检测到程序内存泄露!'.encode(str_encode))



		#创建图表	
		# workbook = xlsxwriter.Workbook('android_memory_report.xlsx')
		worksheet = self.workbook.add_worksheet('memory')
		worksheet2 = self.workbook.add_worksheet('memory_details')

		#设置sheet1和sheet2列宽
		worksheet.set_column('A:C', len(device_info[0])+10)  #设置A到C列列宽
		worksheet.set_column('D:D', len(device_info[-2])+7)  #设置D列列宽
		worksheet.set_column('E:E', len(device_info[-1])+4)  #设置E列列宽

		worksheet.set_column('F:H', len(str(PSS_Dalvik_list[-1]))+13)
		worksheet.set_column('F:F', len(str(PSS_Dalvik_list[-1]))+13)
		worksheet.set_column('H:H', len(str(PSS_Dalvik_list[-1]))+16)

		worksheet.set_column('G:G', len('未检查到内存泄露')+2)
		worksheet.set_column('H:H', len('未检查到内存泄露')+5)

		worksheet2.set_column('A:C', len(device_info[0])+10)  #设置A到C列列宽
		worksheet2.set_column('D:D', len(device_info[-2])+7)  #设置D列列宽
		worksheet2.set_column('E:E', len(device_info[-1])+5)  #设置E列列宽
		worksheet2.set_column('F:G', len(str(PSS_Dalvik_list[-1]))+7)
		worksheet2.set_column('H:H', len(str(PSS_Dalvik_list[-1]))+12)
		# bold = workbook.add_format({'bold': 1})

		#创建图表字体样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_merge=self.workbook.add_format()
		format_merge_content=self.workbook.add_format()
		format_merge_head=self.workbook.add_format()
		format_merge_value=self.workbook.add_format()

		format_title_yellew=self.workbook.add_format()    #设置title和content样式
		format_title_red=self.workbook.add_format()    #设置title和content样式

		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc') 
		format_title.set_font(u'微软雅黑')

		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_merge.set_border(1)
		format_merge.set_font_size(15)
		format_merge.set_align('center')
		format_merge.set_bg_color('#cccccc') 
		format_merge.set_font(u'微软雅黑')

		format_merge_content.set_border(1)
		format_merge_content.set_font_size(12)
		format_merge_content.set_align('left')
		format_merge_content.set_font(u'微软雅黑')

		format_merge_head.set_border(1)
		format_merge_head.set_font_size(12)
		format_merge_head.set_bg_color('#cccccc') 
		format_merge_head.set_align('center')
		format_merge_head.set_font(u'微软雅黑')


		format_merge_value.set_font_size(11)
		format_merge_value.set_align('center')
		format_merge_value.set_font(u'微软雅黑')

		format_title_yellew.set_border(1)
		format_title_yellew.set_font_size(12)
		format_title_yellew.set_align('center')
		format_title_yellew.set_bg_color('#FFFF00')   #设置背景色为黄色
		format_title_yellew.set_font(u'微软雅黑')

		format_title_red.set_border(1)
		format_title_red.set_font_size(12)
		format_title_red.set_align('center')
		format_title_red.set_bg_color('#FF0000')   #设置背景色为红色
		format_title_red.set_font(u'微软雅黑')

		#根据条件，当内存泄露单元素中包括发现，则标红色
		worksheet.conditional_format('G6:G6', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '发现',
                                      'format':   format_title_red})

		#当内存溢出单元格值大于0时，则设置背景为红色
		worksheet.conditional_format('E6:E6',
									 {'type':     'cell',
                                       'criteria': 'greater than',
                                       'value':    0,
                                       'format':   format_title_red})

		# 这是个数据table的列
		headings_title = [u'手机名称',u'品牌', u'系统版本', u'分辨率',u'设备序列号']

		headings_result = ['总内存(KB)','Dalvik_Heap最大值','heapsize','Heapgrowthlimit','OOM内存溢出检查','Native_Heap最大值','内存泄露检查','Dalvik_Heap_alloc均值']

		headings_memory = ['PSS_Total最大','PSS_Total最小','PSS_Total均值','PSS_Dalvik最大','PSS_Dalvik最小','PSS_Dalvik均值','NA','NA']

		headings_details = [u'获取时间','PSS_Total','PSS_Dalvik','Dalvik_Heap_alloc','Native_Heap','VSS', 'RSS','Dalvik_Heap']


		worksheet.merge_range('F1:G1',u'设备IP地址',format_merge_head)
		worksheet.merge_range('F2:G2',ip,format_merge_value)
		worksheet.write('H1',u'APP版本号',format_merge_head)
		worksheet.write('H2',app_version,format_merge_value)

		#取pss最大值，最小值，平均值
		PSS_Total_MAX=max(PSS_total_list)
		PSS_Total_MIN=min(PSS_total_list)
		PSS_Total_AVG=sum(PSS_total_list)/len(PSS_total_list)

		PSS_Dalvik_MAX=max(PSS_Dalvik_list)
		PSS_Dalvik_MIN=min(PSS_Dalvik_list)
		PSS_Dalvik_AVG=sum(PSS_Dalvik_list)/len(PSS_Dalvik_list)


		#计算最大内存及平均内存占的百分比
		PSS_AVG_PERCENT='%.3f%%'%(float(PSS_Total_AVG/float(MemTotal)*100))
		PSS_MAX_PERCENT='%.3f%%'%(float(PSS_Total_AVG/float(MemTotal)*100))


		#计算此次获取Dalvik_Heap_Size最大值，并判断是否存在OOM内存溢出
		Dalvik_Heap_MAX=max(Dalvik_Heap_list)

		if int(Dalvik_Heap_MAX)>=int(heapgrowthlimit) or int(Dalvik_Heap_MAX)>=int(heapsize):
			if system is "Windows":
				window.printRed("存在OOM内存溢出！请检查\n".encode('gbk'))
				window.printWhite('')
				logging.info("存在OOM内存溢出！请检查".encode('gbk'))
			else:
				print "存在OOM内存溢出！请检查"
				logging.info("存在OOM内存溢出！请检查")
			#当存在OOM时，将标记设置为最大内存值，主要是为了在图表上能展示出来，如果不存在，则设置为0，图表上不显示
			OOM_Flag=MemTotal+10
		else:
			OOM_Flag=0
			# OOM_Flag=MemTotal+10


		#存放手机各列信息列表
		data_title=[[device_info[1]],[device_info[0]],[device_info[2]],[device_info[3]],[device_info[-1]]]

		#存放总内存，Dalvik_Heap内存值、内存限制等
		data_result=[[MemTotal],[Dalvik_Heap_MAX],[heapsize],[heapgrowthlimit],[OOM_Flag],[max(Native_Heap_list)],[memory_leak_flag_text],[sum(Dalvik_Heap_Alloc_list)/len(Dalvik_Heap_Alloc_list)]]

		#存放PSS、Dalvik最大，最小，均值
		data_memory=[[PSS_Total_MAX],[PSS_Total_MIN],[PSS_Total_AVG],[PSS_Dalvik_MAX],[PSS_Dalvik_MIN],[PSS_Dalvik_AVG]]

		row_num=len(PSS_total_list)

		#原始内存详细数据列表
		data=[_time_list,PSS_total_list,PSS_Dalvik_list,Dalvik_Heap_Alloc_list,Native_Heap_list,VSS_list,RSS_list,Dalvik_Heap_list]

		#*************重新计算内存走势比例划分*************
		temp_dict={}  

		try:
			VSS_MAX=max(VSS_list)
		except Exception as e:
			logging.info(e)
			VSS_MAX=0
		try:
			RSS_MAX=max(RSS_list)
		except Exception as e:
			logging.info(e)
			RSS_MAX=0

		Priv_Dirty_total_MAX=max(Priv_Dirty_total_list)
		Priv_Dirty_Dalvik_MAX=max(Priv_Dirty_Dalvik_list)
		Native_Heap_list_MAX=max(Native_Heap_list)
		Dalvik_Heap_Alloc_MAX=max(Dalvik_Heap_Alloc_list)


		#计算各个列表最大值的位数
		PSS_Total_MAX_LEN=len(str(PSS_Total_MAX))
		PSS_Dalvik_MAX_LEN=len(str(PSS_Dalvik_MAX))
		Dalvik_Heap_MAX_LEN=len(str(Dalvik_Heap_MAX))
		Priv_Dirty_total_MAX_LEN=len(str(Priv_Dirty_total_MAX))
		Priv_Dirty_Dalvik_MAX_LEN=len(str(Priv_Dirty_Dalvik_MAX))
		VSS_MAX_LEN=len(str(VSS_MAX))
		RSS_MAX_LEN=len(str(RSS_MAX))
		Native_Heap_list_MAX_LEN=len(str(Native_Heap_list_MAX))
		Dalvik_Heap_Alloc_MAX_LEN=len(str(Dalvik_Heap_Alloc_MAX))

		temp_dict['PSS_Total']=PSS_Total_MAX_LEN
		temp_dict['PSS_Dalvik']=PSS_Dalvik_MAX_LEN
		temp_dict['Priv_Dirty_total']=Priv_Dirty_total_MAX_LEN
		temp_dict['Priv_Dirty_Dalvik']=Priv_Dirty_Dalvik_MAX_LEN

		temp_dict['Dalvik_Heap_list']=Dalvik_Heap_MAX_LEN
		temp_dict['VSS_list']=VSS_MAX_LEN
		temp_dict['RSS_list']=RSS_MAX_LEN
		temp_dict['Dalvik_Heap_Alloc_list']=Dalvik_Heap_Alloc_MAX_LEN

		if system is "Windows":
			logging.info("各个列表对应的位数长度集合为:{}".encode('gbk').format(temp_dict))
		else:
			logging.info("各个列表对应的位数长度集合为:{}".format(temp_dict))
		values=temp_dict.values()
		min_len=min(list(values))
		if system is "Windows":
			logging.info("最小位数长度为:{}".encode('gbk').format(min_len))
		else:
			logging.info("最小位数长度为:{}".format(min_len))

		_PSS_total_list=[]
		_PSS_Dalvik_list=[]
		_Priv_Dirty_total_list=[]
		_Priv_Dirty_Dalvik_list=[]
		_Native_Heap_list=[]

		_Dalvik_Heap_list=[]
		_VSS_list=[]
		_RSS_list=[]
		_Dalvik_Heap_Alloc_list=[]


		#PSS Total比例换算
		if int(min_len)==int(PSS_Total_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in PSS_total_list:
				_PSS_total_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(PSS_Total_MAX_LEN-min_len)))))
			for i in PSS_total_list:
				_PSS_total_list.append(i/percent)	

		#PSS_Dalvik比例换算
		if int(min_len)==int(PSS_Dalvik_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in PSS_Dalvik_list:
				_PSS_Dalvik_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(PSS_Dalvik_MAX_LEN-min_len)))))
			for i in PSS_Dalvik_list:
				_PSS_Dalvik_list.append(i/percent)	

		#Priv_Dirty_total比例换算
		if int(min_len)==int(Priv_Dirty_total_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in Priv_Dirty_total_list:
				_Priv_Dirty_total_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(Priv_Dirty_total_MAX_LEN-min_len)))))
			for i in Priv_Dirty_total_list:
				_Priv_Dirty_total_list.append(i/percent)	

		#Priv_Dirty_Dalvik比例换算
		if int(min_len)==int(Priv_Dirty_Dalvik_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in Priv_Dirty_Dalvik_list:
				_Priv_Dirty_Dalvik_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(Priv_Dirty_Dalvik_MAX_LEN-min_len)))))
			for i in Priv_Dirty_Dalvik_list:
				_Priv_Dirty_Dalvik_list.append(i/percent)

		#Dalvik_Heap_Alloc比例换算
		if int(min_len)==int(Dalvik_Heap_Alloc_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in Dalvik_Heap_Alloc_list:
				_Dalvik_Heap_Alloc_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(Dalvik_Heap_Alloc_MAX_LEN-min_len)))))
			for i in Dalvik_Heap_Alloc_list:
				_Dalvik_Heap_Alloc_list.append(i/percent)

		#Natvie Heap比例换算
		if int(min_len)==int(Native_Heap_list_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in Native_Heap_list:
				_Native_Heap_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(Native_Heap_list_MAX_LEN-min_len)))))
			for i in Native_Heap_list:
				_Native_Heap_list.append(i/percent)


		#Dalvik Heap比例换算
		if int(min_len)==int(Dalvik_Heap_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in Dalvik_Heap_list:
				_Dalvik_Heap_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(Dalvik_Heap_MAX_LEN-min_len)))))
			for i in Dalvik_Heap_list:
				_Dalvik_Heap_list.append(i/percent)	

		#VSS比例换算
		if int(min_len)==int(VSS_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in VSS_list:
				_VSS_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(VSS_MAX_LEN-min_len)))))
			for i in VSS_list:
				_VSS_list.append(i/percent)	

		#RSS比例换算
		if int(min_len)==int(RSS_MAX_LEN):
			percent=eval(('1{}.0'.format('0'*(min_len-2))))
			for i in RSS_list:
				_RSS_list.append(i/percent)
		else:
			percent=eval(('1{}.0'.format('0'*(min_len-2+int(RSS_MAX_LEN-min_len)))))
			for i in RSS_list:
				_RSS_list.append(i/percent)	


		#倍数放小percent倍后的数据列表
		_data=[_time_list,_PSS_total_list,_PSS_Dalvik_list,_Dalvik_Heap_Alloc_list,_Native_Heap_list,_VSS_list,_RSS_list,_Dalvik_Heap_list]


		#合并单元格，增加内存说明备注信息
		worksheet.write_comment('E6', '检测是否存在内存溢出，值为0则表示不存在，非0则表示存在!')   #添加单元格备注信息
		worksheet.write_comment('G6', '检测是否存在内存泄露，当采样次数大于5次且Dalvik Heap Alloc值持续增涨，则程序可能存在内存泄露')   #添加单元格备注信息
		worksheet.merge_range('I37:P37',u'内存指标说明',format_merge)
		worksheet.merge_range('I38:P38',u'PSS - Proportional Set Size 实际使用的物理内存，系统统计内存时通常按PSS来计算',format_merge_content)
		worksheet.merge_range('I39:P39',u'VSS - Virtual Set Size 虚拟耗用内存（包含共享库占用的内存）',format_merge_content)
		worksheet.merge_range('I40:P40',u'RSS - Resident Set Size 实际使用物理内存（包含共享库占用的内存）',format_merge_content)
		worksheet.merge_range('I41:P41',u'OOM内存溢出 -当E6值为0时，则不存在内存溢出，但E6值>0(总内存+10)，则存在内存溢出，但此值不表示溢出的大小，仅表示存在内存溢出而已!',format_merge_content)

		worksheet.merge_range('R37:X37',u'内存溢出检查说明',format_merge)
		worksheet.merge_range('R38:X38',u'heapgrowthlimit - 单个应用程序最大内存限制',format_merge_content)		
		worksheet.merge_range('R39:X39',u'heapsize - 单个java虚拟机最大的内存限制',format_merge_content)
		worksheet.merge_range('R40:X40',u'dalvik Heap - java堆创建对象分配的内存，当此值达到heapsize时会出现OOM,',format_merge_content)
		worksheet.merge_range('R41:X41',u'Native Heap -C/C++申请的内存空间',format_merge_content)
		worksheet.merge_range('R42:X42',u'Dalvik Heap Alloc --Java层的内存分配情况,如果此值一直增涨，程序可能出现了内存泄漏',format_merge_content)

		#向sheet表中，添加内容
		worksheet.write_row('A1', headings_title, format_title)   #显示手机信息标题
		worksheet.write_column('A2', data_title[0],format_content)   #手机名称
		worksheet.write_column('B2', data_title[2],format_content)   #手机品牌
		worksheet.write_column('C2', data_title[1],format_content)   #手机版本
		worksheet.write_column('D2', data_title[3],format_content)   #分辨率
		worksheet.write_column('E2', data_title[4],format_content)   #设备序列号


		worksheet.write_row('A5', headings_result, format_title)   #显示总内存，Dalvik_Heap_MAX，heapsize内存限制等
		worksheet.write_row('B5', [headings_result[1]], format_title_yellew)
		worksheet.write_row('E5', [headings_result[4]], format_title_yellew)
		worksheet.write_row('G5', [headings_result[6]], format_title_yellew)
		worksheet.write_column('A6', data_result[0],format_content)   
		worksheet.write_column('B6', data_result[1],format_content)   
		worksheet.write_column('C6', data_result[2],format_content)   
		worksheet.write_column('D6', data_result[3],format_content)   
		worksheet.write_column('E6', data_result[4],format_content)
		worksheet.write_column('F6', data_result[5],format_content)
		worksheet.write_column('G6', data_result[6],format_content)
		worksheet.write_column('H6', data_result[7],format_content)
		# worksheet.write_column('H6', data_result[7],format_content)

		worksheet.write_row('A9', headings_memory, format_title)   #显示PSS最大值，最小值，均值
		worksheet.write_row('C9', [headings_memory[2]], format_title_yellew)
		worksheet.write_row('F9', [headings_memory[5]], format_title_yellew)
		worksheet.write_column('A10', data_memory[0],format_content)   
		worksheet.write_column('B10', data_memory[1],format_content)   
		worksheet.write_column('C10', data_memory[2],format_content)   
		worksheet.write_column('D10', data_memory[3],format_content)   
		worksheet.write_column('E10', data_memory[4],format_content)   
		worksheet.write_column('F10', data_memory[5],format_content)   
		# worksheet.write_column('G10', data_memory[6],format_content)
		# worksheet.write_column('H10', data_memory[7],format_content)
		 
		worksheet.write_row('A13', headings_details, format_title)    #显示详细记录数据,比例缩减
		worksheet.write_column('A14', _data[0],format_content)   
		worksheet.write_column('B14', _data[1],format_content)   
		worksheet.write_column('C14', _data[2],format_content)   
		worksheet.write_column('D14', _data[3],format_content)   
		worksheet.write_column('E14', _data[4],format_content)   
		worksheet.write_column('F14', _data[5],format_content)   
		worksheet.write_column('G14', _data[6],format_content)
		worksheet.write_column('H14', _data[7],format_content)   

		worksheet2.write_row('A1', headings_details, format_title)    #在sheet2表中显示内存详细记录数据
		worksheet2.write_column('A2', data[0],format_content)   
		worksheet2.write_column('B2', data[1],format_content)   
		worksheet2.write_column('C2', data[2],format_content)   
		worksheet2.write_column('D2', data[3],format_content)   
		worksheet2.write_column('E2', data[4],format_content)   
		worksheet2.write_column('F2', data[5],format_content)   
		worksheet2.write_column('G2', data[6],format_content)
		worksheet2.write_column('H2', data[7],format_content)   

		############################################
		#创建一个柱形样式和线条样式图表，类型是column、line
		chart1 = self.workbook.add_chart({'type': 'column'})
		chart2 = self.workbook.add_chart({'type': 'line'})

		chart3 = self.workbook.add_chart({'type': 'column'})
		chart4 = self.workbook.add_chart({'type': 'column'})
		 
		# 配置series,这个和前面wordsheet是有关系的。 

		#******************内存占用_柱形图表*****************
		chart1.add_series({
		    'name':       '=memory!$B$13',   #显示名称
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),  #x坐标范围
		    'values':     '=memory!$B$14:$B${}'.format(row_num+14),  #图表数据范围
		})

		chart1.add_series({
		    'name':       '=memory!$C$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$C$14:$C${}'.format(row_num+14),
		})

		chart1.add_series({
		    'name':       '=memory!$F$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$F$14:$F${}'.format(row_num+14),
		})

		chart1.add_series({
		    'name':       '=memory!$G$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$G$14:$G${}'.format(row_num+14),
		})

		chart1.add_series({
		    'name':       '=memory!$H$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$H$14:$H${}'.format(row_num+14),
		})

		#******************内存占用_线形图表*****************
		chart2.set_drop_lines()

		chart2.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart2.add_series({
		    'name':       '=memory!$B$13',   #显示名称
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),  #x坐标范围
		    'values':     '=memory!$B$14:$B${}'.format(row_num+14),  #图表数据范围
		})

		chart2.add_series({
		    'name':       '=memory!$C$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$C$14:$C${}'.format(row_num+14),
		})

		chart2.add_series({
		    'name':       '=memory!$F$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$F$14:$F${}'.format(row_num+14),
		})

		chart2.add_series({
		    'name':       '=memory!$G$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$G$14:$G${}'.format(row_num+14),
		})

		chart2.add_series({
		    'name':       '=memory!$H$13',
		    'categories': '=memory!$A$14:$A${}'.format(row_num+14),
		    'values':     '=memory!$H$14:$H${}'.format(row_num+14),
		})

		#****************最大内存限制绘图数据*****************************
		chart3.add_series({
		    'name':       '=memory!$A$5',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$A$6:$A$6',
		    'line':       {'color': 'black'},
		})
		chart3.add_series({
		    'name':       '=memory!$B$5',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$B$6:$B$6',
		    'line':       {'color': 'blue'},
		})
		chart3.add_series({
		    'name':       '=memory!$C$5',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$C$6:$C$6',
		    'line':       {'color': 'black'},
		})

		chart3.add_series({
		    'name':       '=memory!$D$5',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$D$6:$D$6',
		    'line':       {'color': 'black'},
		})

		chart3.add_series({
		    'name':       '=memory!$E$5',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$E$6:$E$6',
		    'line':       {'color': 'red'},
		    'fill':       {'color': 'red'},
		})

		#****************总体内存概况绘图数据*****************************
		chart4.add_series({
		    'name':       '=memory!$A$9',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$A$10:$A$10',
		    # 'line':       {'color': 'green'},
		})
		chart4.add_series({
		    'name':       '=memory!$B$9',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$B$10:$B$10',
		    # 'line':       {'color': 'green'},
		})
		chart4.add_series({
		    'name':       '=memory!$C$9',
		    # 'categories': '=Sheet1!$A$6:$A${}'.format(row_num+6),
		    'values':     '=memory!$C$10:$C$10',
		    # 'line':       {'color': 'green'},
		})

		chart4.add_series({
		    'name':       '=memory!$D$9',
		    # 'categories': '=Sheet1!$A$6:$A$6',
		    'values':     '=memory!$D$10:$D$10',
		    # 'line':       {'color': 'green'},
		})

		chart4.add_series({
		    'name':       '=memory!$E$9',
		    # 'categories': '=Sheet1!$A$6:$A$6',
		    'values':     '=memory!$E$10:$E$10',
		    # 'line':       {'color': 'green'},
		})

		chart4.add_series({
		    'name':       '=memory!$F$9',
		    # 'categories': '=Sheet1!$A$6:$A$6',
		    'values':     '=memory!$F$10:$F$10',
		    # 'line':       {'color': 'green'},
		})

		# Add a chart title and some axis labels.
		chart1.set_title ({'name': '内存使用_柱形图'})
		chart1.set_x_axis({'name': '时间'})
		chart1.set_y_axis({'name': '内存比例'})

		chart2.set_title ({'name': '内存使用_线形图'})
		chart2.set_x_axis({'name': '时间'})
		chart2.set_y_axis({'name': '内存比例'})	

		chart3.set_title ({'name': 'OOM内存溢出检查'})
		chart3.set_x_axis({'name': 'Out Of Memory\n如果出现红色柱形条，则存在内存溢出！'})
		chart3.set_y_axis({'name': '内存值'})

		chart4.set_title ({'name': 'PSS峰值使用'})
		chart4.set_x_axis({'name': '内存情况(KB)'})
		chart4.set_y_axis({'name': '使用分布'})

		# Set an Excel chart style.
		# chart1.set_style(11)
		 
		# Insert the chart into the worksheet (with an offset).
		worksheet.insert_chart('I2', chart1, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('I20', chart2, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('Q2', chart3, {'x_offset': 20, 'y_offset': 10})
		worksheet.insert_chart('Q20', chart4, {'x_offset': 20, 'y_offset': 10})


		###########内存详细表，图表绘制#####################
		#创建一个柱形样式和线条样式图表，类型是column、line
		chart1 = self.workbook.add_chart({'type': 'line'})  #PSS
		chart2 = self.workbook.add_chart({'type': 'line'})  #Priv_Dirty
		chart3 = self.workbook.add_chart({'type': 'line'})  #Native_Heap
		chart4 = self.workbook.add_chart({'type': 'line'})  #Dalvik_Heap
		chart5 = self.workbook.add_chart({'type': 'line'})  #Native_Heap_alloc

		# 配置series,这个和前面wordsheet是有关系的。
		row_num=len(Native_Heap_list)
		#******************内存占用_柱形图表*****************
		chart1.add_series({
		    'name':       '=memory_details!$B$1',   #显示名称
		    'categories': '=memory_details!$A$2:$A${}'.format(row_num+2),  #x坐标范围
		    'values':     '=memory_details!$B$2:$B${}'.format(row_num+2),  #图表数据范围
		})

		chart2.add_series({
		    'name':       '=memory_details!$D$1',   #显示名称
		    'categories': '=memory_details!$A$2:$A${}'.format(row_num+2),  #x坐标范围
		    'values':     '=memory_details!$D$2:$D${}'.format(row_num+2),  #图表数据范围
		})

		chart3.add_series({
		    'name':       '=memory_details!$E$1',   #显示名称
		    'categories': '=memory_details!$A$2:$A${}'.format(row_num+2),  #x坐标范围
		    'values':     '=memory_details!$E$2:$E${}'.format(row_num+2),  #图表数据范围
		})

		chart4.add_series({
		    'name':       '=memory_details!$H$1',   #显示名称
		    'categories': '=memory_details!$A$2:$A${}'.format(row_num+2),  #x坐标范围
		    'values':     '=memory_details!$H$2:$H${}'.format(row_num+2),  #图表数据范围
		})


		chart5.add_series({
		    'name':       '=memory_details!$D$1',   #显示名称
		    'categories': '=memory_details!$A$2:$A${}'.format(row_num+2),  #x坐标范围
		    'values':     '=memory_details!$D$2:$D${}'.format(row_num+2),  #图表数据范围
		})


		chart1.set_title ({'name': 'PSS_Total内存使用走势图'})
		chart1.set_x_axis({'name': '时间'})
		chart1.set_y_axis({'name': '内存使用'})

		chart2.set_title ({'name': 'Private_Total内存使用走势图'})
		chart2.set_x_axis({'name': '时间'})
		chart2.set_y_axis({'name': '内存使用'})

		chart3.set_title ({'name': 'Native_Heap内存使用走势图'})
		chart3.set_x_axis({'name': '时间'})
		chart3.set_y_axis({'name': '内存使用'})

		chart4.set_title ({'name': 'Dalvik_Heap内存使用走势图'})
		chart4.set_x_axis({'name': '时间'})
		chart4.set_y_axis({'name': '内存使用'})

		chart5.set_title ({'name': 'Dalvik_Heap_alloc内存使用走势图'})
		chart5.set_x_axis({'name': '时间'})
		chart5.set_y_axis({'name': '内存使用'})

		# Insert the chart into the worksheet (with an offset).
		worksheet2.insert_chart('I2', chart1, {'x_offset': 25, 'y_offset': 10})
		worksheet2.insert_chart('I20', chart2, {'x_offset': 25, 'y_offset': 10})
		worksheet2.insert_chart('Q2', chart3, {'x_offset': 20, 'y_offset': 10})
		worksheet2.insert_chart('Q20', chart4, {'x_offset': 20, 'y_offset': 10})
		worksheet2.insert_chart('I38', chart5, {'x_offset': 20, 'y_offset': 10})
		logging.info('Memory表生成绘制完成!'.encode(str_encode))

	#生成CPU资源报告
	def gen_cpu_report(self,device_name,packapgename,times):
		worksheet = self.workbook.add_worksheet("cpu")
		app_version=self.android.getAppVersion(device_name,packapgename)  #获取软件版本号
		cpu_precent_total_list,cpu_precent_user_list,cpu_precent_kernel_list,cpu_precent_v2_list,\
		time_list,activity_list,cpu_temperature_list,cpu_frequency_list=self.android.get_device_cpu(device_name,packapgename,times)

		p=Android_Permance()
		cpu_process=p.get_cpu_kel(device_name)  #获取cpu核数
		if system is 'Windows':
			logging.info('获取当前设备CPU核数:{}'.format(cpu_process).encode('gbk'))
		else:
			logging.info('获取当前设备CPU核数:{}'.format(cpu_process))

		_time_list=[]
		for time in time_list:

			#分割时间，去掉日期，只取时间
			time=time.split()[-1]
			_time_list.append(time)

		#去掉activity前面的包名
		_activity_list=[]
		for activity in activity_list:
			_activity_list.append(activity.split('/')[-1].strip('.'))


		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()

		format_merge=self.workbook.add_format()
		format_merge_content=self.workbook.add_format()
		format_merge_content_red=self.workbook.add_format()

		worksheet.set_column('A:A', len(str(_time_list[-1]))+2)  #设置列宽
		worksheet.set_column('B:B', len(str(_activity_list[0]))+3)  #设置列宽
		worksheet.set_column('C:C', len(str(packapgename))+1)
		worksheet.set_column('D:E', len(str(cpu_precent_total_list[-1]))+13)
		worksheet.set_column('F:I', len(str(cpu_precent_total_list[-1]))+18)
		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc') 
		format_title.set_font(u'微软雅黑')
		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_merge.set_border(1)
		format_merge.set_font_size(15)
		format_merge.set_align('center')
		format_merge.set_bg_color('#cccccc')
		format_merge.set_font(u'微软雅黑')

		format_merge_content.set_border(1)
		format_merge_content.set_font_size(12)
		format_merge_content.set_align('left')
		format_merge_content.set_font(u'微软雅黑')

		format_merge_content_red.set_border(1)
		format_merge_content_red.set_font_size(12)
		format_merge_content_red.set_align('left')
		format_merge_content_red.set_font(u'微软雅黑')
		format_merge_content_red.set_text_wrap()   #自动换行
		format_merge_content_red.set_font_color('#FF0000')

		#生成cpu核数列表
		cpu_process_list=[cpu_process]*len(cpu_precent_total_list)
		print cpu_process_list

		# 这是个数据table的列
		headings_info = [u'获取时间','采样当前界面activity',u'CPU使用率%',u'用户使用率%', u'内核使用率%', u'CPU占用率%(Top)',u'CPU核数',u'CPU实时温度℃',u'CPU当前频率mHZ']

		# headings_result = [u'APP版本号',u'采样时间(s)','进程名',u'采样次数',u'CPU最大值%', u'CPU平均值%', u'CPU最小值%']
		headings_result = [u'APP版本号',u'采样时间(s)','进程名',u'采样次数',u'CPU使用均值%', u'CPU用户使用均值%', u'CPU占用均值(Top)%',u'CPU温度变化℃',u'CPU平均频率mHZ']
		data_info=[_time_list,_activity_list,cpu_precent_total_list,cpu_precent_user_list,cpu_precent_kernel_list,cpu_precent_v2_list,cpu_process_list,
		           cpu_temperature_list,cpu_frequency_list]




		#计算采样时间，用最后一次获取时间减去第一次采样获取时间
		time_a = datetime.strptime(_time_list[0],'%H:%M:%S')
		time_b = datetime.strptime(_time_list[-1],'%H:%M:%S')
		consum_times=(time_b - time_a).seconds

		CPU_MAX=max(cpu_precent_total_list)
		CPU_MIN=min(cpu_precent_total_list)

		CPU_AVG=sum(cpu_precent_total_list)/len(cpu_precent_total_list)
		CPU_USER_AVG=sum(cpu_precent_user_list)/len(cpu_precent_user_list)
		CPU_TOP_AVG=sum(cpu_precent_v2_list)/len(cpu_precent_v2_list)



		#CPU温度上升情况
		if isinstance(cpu_temperature_list[-1],str):
			cpu_status=eval(cpu_temperature_list[-1])-eval(cpu_temperature_list[0])
		else:
			cpu_status=cpu_temperature_list[-1]-cpu_temperature_list[0]

		#cpu平均使用频率
		cpu_frequency_avg=sum(cpu_frequency_list)/len(cpu_frequency_list)

		data_result=[[app_version],[consum_times],[packapgename],[len(cpu_precent_total_list)],[CPU_AVG],[CPU_USER_AVG],[CPU_TOP_AVG],[cpu_status],[cpu_frequency_avg]]

		worksheet.write_row('A1', headings_result, format_title)   #显示CPU标题
		worksheet.write_column('A2', data_result[0],format_content)   
		worksheet.write_column('B2', data_result[1],format_content)   
		worksheet.write_column('C2', data_result[2],format_content)   
		worksheet.write_column('D2', data_result[3],format_content)   
		worksheet.write_column('E2', data_result[4],format_content)   
		worksheet.write_column('F2', data_result[5],format_content)
		worksheet.write_column('G2', data_result[6],format_content)
		worksheet.write_column('H2', data_result[7],format_content)
		worksheet.write_column('I2', data_result[8],format_content)

		worksheet.write_row('A5', headings_info, format_title)   #显示CPU详细
		worksheet.write_column('A6', data_info[0],format_content)   
		worksheet.write_column('B6', data_info[1],format_content)   
		worksheet.write_column('C6', data_info[2],format_content)   
		worksheet.write_column('D6', data_info[3],format_content)   
		worksheet.write_column('E6', data_info[4],format_content)   
		worksheet.write_column('F6', data_info[5],format_content)
		worksheet.write_column('G6', data_info[6],format_content)
		worksheet.write_column('H6', data_info[7],format_content)
		worksheet.write_column('I6', data_info[8],format_content)

		#合并单元格，增加CPU说明备注信息
		worksheet.write_comment('H5',"CPU实时温度为0时，则说明当前设备获取CPU温度提示Permission denied，故赋默认值0")
		worksheet.merge_range('J37:Q37',u'CPU指标说明',format_merge)
		worksheet.merge_range('J38:Q38',u'C列中CPU使用率% - 采用adb shell dumpsys cpuinfo方式执行采样',format_merge_content)
		worksheet.merge_range('J39:Q39',u'C列中CPU使用率% - 等于D列用户占用率+E列内核占用率',format_merge_content)
		worksheet.merge_range('J40:Q40',u'F列中CPU占用率%(Top) - 采用adb shell top -n 3方式执行采样',format_merge_content)
		worksheet.merge_range('J41:Q41',u'建议:以F列中CPU占用率%（Top）获取的数据为准，CPU使用率总数计算方式cpu核数*100%',format_merge_content_red)

		row_num=len(cpu_precent_total_list)
		#创建一个柱形样式和线条样式图表，类型是column、line
		chart1 = self.workbook.add_chart({'type': 'line'})
		chart2 = self.workbook.add_chart({'type': 'column'})
		chart3 = self.workbook.add_chart({'type': 'line'})
		chart4 = self.workbook.add_chart({'type': 'line'})



		#******************CPU占用_条形图表*****************
		chart1.set_drop_lines()
		chart1.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart3.set_drop_lines()
		chart3.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart4.set_drop_lines()
		chart4.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		# chart1.set_high_low_lines()
		# chart1.set_high_low_lines({
		#     'line': {
		#         'color': 'red',
		#         'dash_type': 'square_dot'
		#     }
		# })


		chart1.add_series({
		    'name':       '=cpu!$C$5',   #显示名称
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),  #x坐标范围
		    'values':     '=cpu!$C$6:$C${}'.format(row_num+5),  #图表数据范围
		})

		chart1.add_series({
		    'name':       '=cpu!$D$5',
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),
		    'values':     '=cpu!$D$6:$D${}'.format(row_num+5),
		})

		chart1.add_series({
		    'name':       '=cpu!$E$5',
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),
		    'values':     '=cpu!$E$6:$E${}'.format(row_num+5),
		})

		chart1.add_series({
		    'name':       '=cpu!$F$5',
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),
		    'values':     '=cpu!$F$6:$F${}'.format(row_num+5),
		})

		chart2.add_series({
		    'name':       '=cpu!$C$5',   #显示名称
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),  #x坐标范围
		    'values':     '=cpu!$C$6:$C${}'.format(row_num+5),  #图表数据范围
		})

		chart2.add_series({
		    'name':       '=cpu!$D$5',
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),
		    'values':     '=cpu!$D$6:$D${}'.format(row_num+5),
		})

		chart2.add_series({
		    'name':       '=cpu!$E$5',
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),
		    'values':     '=cpu!$E$6:$E${}'.format(row_num+5),
		})

		chart2.add_series({
		    'name':       '=cpu!$F$5',
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),
		    'values':     '=cpu!$F$6:$F${}'.format(row_num+5),
		})
		#cpu温度线型走势图
		chart3.add_series({
		    'name':       '=cpu!$H$5',   #显示名称
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),  #x坐标范围
		    'values':     '=cpu!$H$6:$H${}'.format(row_num+5),  #图表数据范围
		})
		#cpu频率线型走势图
		chart4.add_series({
		    'name':       '=cpu!$I$5',   #显示名称
		    'categories': '=cpu!$A$6:$A${}'.format(row_num+5),  #x坐标范围
		    'values':     '=cpu!$I$6:$I${}'.format(row_num+5),  #图表数据范围
		})
		# Add a chart title and some axis labels.
		chart1.set_title ({'name': '进程:{}\nCPU使用_线形图'.format(packapgename)})
		chart1.set_x_axis({'name': '时间分布'})
		chart1.set_y_axis({'name': 'CPU百分比(%)'})

		chart2.set_title ({'name': '进程:{}\nCPU使用_柱形图'.format(packapgename)})
		chart2.set_x_axis({'name': '时间分布'})
		chart2.set_y_axis({'name': 'CPU百分比(%)'})

		chart3.set_title ({'name': '进程:{}\nCPU温度_线形图'.format(packapgename)})
		chart3.set_x_axis({'name': '时间分布'})
		chart3.set_y_axis({'name': 'CPU温度(℃)'})

		chart4.set_title ({'name': '进程:{}\nCPU使用频率_线形图'.format(packapgename)})
		chart4.set_x_axis({'name': '时间分布'})
		chart4.set_y_axis({'name': 'CPU使用频率(MHZ)'})


		worksheet.insert_chart('J2', chart2, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('J20', chart1, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('R2', chart3, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('R20', chart4, {'x_offset': 25, 'y_offset': 10})
		# self.workbook.close()
		logging.info('CPU表生成绘制完成!'.encode(str_encode))

	#生成网络流量报告
	def gen_net_report(self,device_name,packapgename,times):
		worksheet = self.workbook.add_worksheet("net")
		app_version=self.android.getAppVersion(device_name,packapgename)  #获取软件版本号
		time_list,net_wifi_rcv_list,net_wifi_send_list,net_wifi_rcv_packets_list,net_wifi_send_packets_list,net2_rx_bytes_list,net2_tx_bytes_list=self.android.get_device_net(device_name,packapgename,times)

		_time_list=[]
		for time in time_list:

			#分割时间，去掉日期，只取时间
			time=time.split()[-1]
			_time_list.append(time)

		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_title_yellew=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_merge=self.workbook.add_format()
		format_merge_content=self.workbook.add_format()
		format_merge_content_red=self.workbook.add_format()

		worksheet.set_column('A:A', len(str(_time_list[-1]))+2)  #设置列宽
		worksheet.set_column('B:E', len(str(_time_list[-1]))+10)  #设置列宽
		worksheet.set_column('D:D', len(str(packapgename))+2)  #设置列宽
		worksheet.set_column('E:H', len(str(net_wifi_rcv_list[-1]))+14)

		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')    #设置背景色为浅灰色
		format_title.set_font(u'微软雅黑')

		format_title_yellew.set_border(1)
		format_title_yellew.set_font_size(12)
		format_title_yellew.set_align('center')
		format_title_yellew.set_bg_color('#FFFF00')   #设置背景色为黄色
		format_title_yellew.set_font(u'微软雅黑')

		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_merge.set_border(1)
		format_merge.set_font_size(15)
		format_merge.set_align('center')
		format_merge.set_bg_color('#cccccc')
		format_merge.set_font(u'微软雅黑')

		format_merge_content.set_border(1)
		format_merge_content.set_font_size(12)
		format_merge_content.set_align('left')
		format_merge_content.set_font(u'微软雅黑')

		format_merge_content_red.set_border(1)
		format_merge_content_red.set_font_size(12)
		format_merge_content_red.set_align('left')
		format_merge_content_red.set_font(u'微软雅黑')
		format_merge_content_red.set_text_wrap()   #自动换行
		format_merge_content_red.set_font_color('#FF0000')

		# 这是个数据table的列
		headings_info = [u'获取时间',u'TCP接收字节数KB',u'TCP发送字节数KB',u'接收数据包', u'发送数据包', u'NET总接收字节KB',u'NET总发送字节KB','NA']

		# headings_result = [u'APP版本号',u'采样时间(s)',u'采样次数',u'采样进程',u'TCP接收总字节数',u'TCP发送总字节数', u'NET接收总数据', u'NET发送总数据']
		headings_result = [u'APP版本号',u'采样时间(s)',u'采样次数',u'采样进程',u'TCP接收字节数总和',u'TCP发送字节数总和', u'TCP接收字节消耗', u'TCP发送字节消耗']

		#计算采样时间，用最后一次获取时间减去第一次采样获取时间
		time_a = datetime.strptime(_time_list[0],'%H:%M:%S')
		time_b = datetime.strptime(_time_list[-1],'%H:%M:%S')
		consum_times=(time_b - time_a).seconds		

		data_info=[_time_list,net_wifi_rcv_list,net_wifi_send_list,net_wifi_rcv_packets_list,net_wifi_send_packets_list,net2_rx_bytes_list,net2_tx_bytes_list]	

		# data_result=[[app_version],[consum_times],[len(_time_list)],[packapgename],[sum(net_wifi_rcv_list)],[sum(net_wifi_send_list)],[sum(net2_rx_bytes_list)],[sum(net2_tx_bytes_list)]]
		data_result=[[app_version],[consum_times],[len(_time_list)],[packapgename],[sum(net_wifi_rcv_list)],[sum(net_wifi_send_list)],[net_wifi_rcv_list[-1]],[net_wifi_send_list[-1]]]

		worksheet.write_row('A5', headings_info, format_title)   #显示网络流量标题
		worksheet.write_row('B5', [headings_info[1]], format_title_yellew)
		worksheet.write_row('C5', [headings_info[2]], format_title_yellew)
		worksheet.write_column('A6', data_info[0],format_content)   
		worksheet.write_column('B6', data_info[1],format_content)   
		worksheet.write_column('C6', data_info[2],format_content)   
		worksheet.write_column('D6', data_info[3],format_content)   
		worksheet.write_column('E6', data_info[4],format_content)   
		worksheet.write_column('F6', data_info[5],format_content)   
		worksheet.write_column('G6', data_info[6],format_content)
		# worksheet.write_column('H6', data_info[7],format_content)

		worksheet.write_row('A1', headings_result, format_title)   #显示网络流量标题
		worksheet.write_row('G1', [headings_result[-2]], format_title_yellew)
		worksheet.write_row('H1', [headings_result[-1]], format_title_yellew)
		worksheet.write_column('A2', data_result[0],format_content)   
		worksheet.write_column('B2', data_result[1],format_content)   
		worksheet.write_column('C2', data_result[2],format_content)   
		worksheet.write_column('D2', data_result[3],format_content)   
		worksheet.write_column('E2', data_result[4],format_content)   
		worksheet.write_column('F2', data_result[5],format_content)   
		worksheet.write_column('G2', data_result[6],format_content)
		worksheet.write_column('H2', data_result[7],format_content)


		#合并单元格，增加内存说明备注信息
		worksheet.merge_range('I37:P37',u'流量指标说明',format_merge)
		worksheet.merge_range('I38:P38',u'接收字节数KB - 统计wifi模式下，此次TCP接收到字节数',format_merge_content)
		worksheet.merge_range('I39:P39',u'发送节数KB - 统计wifi模式下，此次TCP发送的字节数',format_merge_content)
		worksheet.merge_range('I40:P40',u'NET接收数据 - 统计开机之后所有的接收总字节数，包含TCP、UDP',format_merge_content)
		worksheet.merge_range('I41:P41',u'NET发送数据 - 统计开机之后所有的发送总字节数，包含TCP、UDP',format_merge_content)
		worksheet.merge_range('I41:P41',u'NET发送数据 - 统计开机之后所有的发送总字节数，包含TCP、UDP',format_merge_content)
		worksheet.merge_range('I42:P44',u'建议:流量采集，以TCP接收字节数B(列)、与TCP发送字节数C(列)数据为主，\nG和H两列值为此次场景接收和发送消耗的字节数',format_merge_content_red)

		row_num=len(net_wifi_rcv_list)
		#创建一个柱形样式和线条样式图表，类型是column、line
		chart1 = self.workbook.add_chart({'type': 'line'})
		chart2 = self.workbook.add_chart({'type': 'line'})
		chart3 = self.workbook.add_chart({'type': 'line'})
		chart4 = self.workbook.add_chart({'type': 'line'})
		#******************流量占用_图表*****************
		#线形图

		chart1.set_drop_lines()
		chart1.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart2.set_drop_lines()
		chart2.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart3.set_drop_lines()
		chart3.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})
		chart4.set_drop_lines()
		chart4.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})


		# chart1.add_series({
		#     'name':       '=net!$B$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$B$6:$B${}'.format(row_num+5),
		# })

		# chart1.add_series({
		#     'name':       '=net!$C$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$C$6:$C${}'.format(row_num+5),
		# })
		#
		# chart1.add_series({
		#     'name':       '=net!$D$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$D$6:$D${}'.format(row_num+5),
		# })
		#
		# chart1.add_series({
		#     'name':       '=net!$E$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$E$6:$E${}'.format(row_num+5),
		# })
		#
		chart1.add_series({
		    'name':       '=net!$B$5',
		    'categories': '=net!$A$6:$A${}'.format(row_num+5),
		    'values':     '=net!$B$6:$B${}'.format(row_num+5),
		})
		chart3.add_series({
		    'name':       '=net!$C$5',
		    'categories': '=net!$A$6:$A${}'.format(row_num+5),
		    'values':     '=net!$C$6:$C${}'.format(row_num+5),
		})
		# chart1.add_series({
		#     'name':       '=net!$G$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$G$6:$G${}'.format(row_num+5),
		# })

		#柱形图表
		# chart2.add_series({
		#     'name':       '=net!$B$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$B$6:$B${}'.format(row_num+5),
		# })
		#
		# chart2.add_series({
		#     'name':       '=net!$C$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$C$6:$C${}'.format(row_num+5),
		# })
		#
		# chart2.add_series({
		#     'name':       '=net!$D$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$D$6:$D${}'.format(row_num+5),
		# })
		#
		# chart2.add_series({
		#     'name':       '=net!$E$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$E$6:$E${}'.format(row_num+5),
		# })
		#
		# chart2.add_series({
		#     'name':       '=net!$F$5',
		#     'categories': '=net!$A$6:$A${}'.format(row_num+5),
		#     'values':     '=net!$F$6:$F${}'.format(row_num+5),
		# })
		chart2.add_series({
		    'name':       '=net!$F$5',
		    'categories': '=net!$A$6:$A${}'.format(row_num+5),
		    'values':     '=net!$F$6:$F${}'.format(row_num+5),
		})
		chart4.add_series({
		    'name':       '=net!$G$5',
		    'categories': '=net!$A$6:$A${}'.format(row_num+5),
		    'values':     '=net!$G$6:$G${}'.format(row_num+5),
		})

		# Add a chart title and some axis labels.
		chart1.set_title ({'name': '进程:{}\n接收字节数KB_线形图'.format(packapgename)})
		chart1.set_x_axis({'name': '时间分布'})
		chart1.set_y_axis({'name': '流量使用(KB)'})

		chart3.set_title ({'name': '进程:{}\n发送字节数KB_线形图'.format(packapgename)})
		chart3.set_x_axis({'name': '时间分布'})
		chart3.set_y_axis({'name': '流量使用(KB)'})

		# Add a chart title and some axis labels.
		chart2.set_title ({'name': '进程:{}\nNET接收数据_线形图'.format(packapgename)})
		chart2.set_x_axis({'name': '时间分布'})
		chart2.set_y_axis({'name': '流量使用(KB)'})

		chart4.set_title ({'name': '进程:{}\nNET发送数据_线形图'.format(packapgename)})
		chart4.set_x_axis({'name': '时间分布'})
		chart4.set_y_axis({'name': '流量使用(KB)'})

		worksheet.insert_chart('I2', chart1, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('I20', chart3, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('Q2', chart2, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('Q20', chart4, {'x_offset': 25, 'y_offset': 10})
		# self.workbook.close()
		logging.info('NET表生成绘制完成!'.encode(str_encode))

	#生成帧率报告
	def gen_fps_report(self,device_name,packapgename,times):
		worksheet = self.workbook.add_worksheet("fps")
		app_version=self.android.getAppVersion(device_name,packapgename)  #获取软件版本号
		time_list,frames_list,seconds_list,fps_list,activity_list,times_list,Draw_list,Prepare_list,Process_list,Execute_list,sum_time_line_list,\
		flag_list,time_list2,fps_per_list=self.android.get_device_fps(device_name,packapgename,times)

		_time_list=[]
		for time in time_list:

			#分割时间，去掉日期，只取时间
			time=time.split()[-1]
			_time_list.append(time)

		#去掉activity前面的包名
		_activity_list=[]
		for activity in activity_list:
			_activity_list.append(activity.split('/')[-1].strip('.'))

		_time_list2=[]
		for time in time_list2:

			#分割时间，去掉日期，只取时间
			time=time.split()[-1]
			_time_list2.append(time)

		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_merge=self.workbook.add_format()
		format_merge_value=self.workbook.add_format()
		format_title_yellew=self.workbook.add_format()    #设置title和content样式

		format3=self.workbook.add_format()

		format_merge.set_border(1)
		format_merge.set_font_size(12)
		format_merge.set_align('center')
		format_merge.set_bg_color('#cccccc')
		format_merge.set_font(u'微软雅黑')

		# format_merge_value.set_border(1)
		format_merge_value.set_font_size(11)
		format_merge_value.set_align('center')
		format_merge_value.set_font(u'微软雅黑')

		format3.set_font_size(11)
		format3.set_align('center')
		format3.set_font(u'微软雅黑')
		format3.set_bg_color('#808080')  #背景色深灰色


		format_title_yellew.set_border(1)
		format_title_yellew.set_font_size(12)
		format_title_yellew.set_align('center')
		format_title_yellew.set_bg_color('#FFFF00')   #设置背景色为黄色
		format_title_yellew.set_font(u'微软雅黑')

		#设置条件格式,当大于G6单元格列中包含Fail文本时，设置背景色为黄色，字体颜色为红色。
		format1 = self.workbook.add_format({'bg_color':   '#FFFF00',
                               'font_color': '#FF0000'})
		format2 = self.workbook.add_format({
                               'font_color': '#FF0000'})
		worksheet.conditional_format('I6:I${}'.format(len(Draw_list)+6),
									 {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    'Fail',
                                       'format':   format2})
		try:
			worksheet.set_column('A:B', len(str(_time_list[-1]))+4)  #设置列宽
			worksheet.set_column('C:C', len(str(packapgename))+2)
			worksheet.set_column('D:E', len(str(fps_list[-1]))+12)
			worksheet.set_column('F:H', len(str(flag_list[-1]))+12)
			worksheet.set_column('I:K', len(str(flag_list[-1]))+15)
		except:
			if system is "Windows":
				logging.info("当前帧率获取为空，请滑动页面，重新获取帧率!!!".encode('gbk'))
				pass
			else:
				logging.info("当前帧率获取为空，请滑动页面，重新获取帧率!!!")
		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc') 
		format_title.set_font(u'微软雅黑')
		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format1.set_border(1)
		format1.set_font_size(11)
		format1.set_align('center')
		format1.set_font(u'微软雅黑')

		if str(flag_list[0]).isupper():  #判断字符是否是大写
			#计算大于16.6帧数
			exceed=Counter(flag_list)['FAIL']
		else:
			#计算大于16.6帧数
			exceed=Counter(flag_list)['Fail']

		#大于16.6占比
		exceed_percent='%.3f%%'%float(float(exceed)/len(Draw_list)*100)
		exceed_percent_value=exceed_percent.strip('%')


		#获取95%的帧图像耗时（采集的全部数据排序倒数5%的时间）,reverse=False为升序
		seconds_95_=int(len(sum_time_line_list)*0.95)
		seconds_95_value=sorted(sum_time_line_list,reverse=False)[seconds_95_-1]
		if system is "Windows":
			print "95%帧图像耗时在索引号为:{0},列表对应的值为:{1}".format(seconds_95_,seconds_95_value).encode('gbk')
			logging.info("95%帧图像耗时在索引号为:{0},列表对应的值为:{1}".format(seconds_95_,seconds_95_value).encode(str_encode))
		else:
			print "95%帧图像耗时在索引号为:{0},列表对应的值为:{1}".format(seconds_95_,seconds_95_value)
			logging.info("95%帧图像耗时在索引号为:{0},列表对应的值为:{1}".format(seconds_95_,seconds_95_value).encode(str_encode))

		# 这是个数据table的列
		headings_info = [u'采集序号',u'采集时间',u'平均帧率',u'Draw','Prepare','Process','Execute',u'每帧耗时(ms)',u'是否大于16.0']

		headings_result = ['APP版本号',u'采样时间(s)',u'进程名','采样总帧数','大于16.0帧数','大于16.0占比','95%的帧耗时','','',u'平均帧数量',u'平均总帧率',]

		#计算采样时间，用最后一次获取时间减去第一次采样获取时间
		time_a = datetime.strptime(_time_list[0],'%H:%M:%S')
		time_b = datetime.strptime(_time_list[-1],'%H:%M:%S')
		consum_times=(time_b - time_a).seconds

		frames_list_len=len(frames_list)
		seconds_list_len=len(seconds_list)
		fps_list_len=len(fps_list)
		if frames_list_len==0:
			frames_list_len=1
		if seconds_list_len==0:
			seconds_list_len=1
		if fps_list_len==0:
			fps_list_len=1
		frames_avg=sum(frames_list)/frames_list_len
		seconds_avg=sum(seconds_list)/seconds_list_len
		fps_avg=sum(fps_list)/fps_list_len


		data_info=[times_list,_time_list2,fps_per_list,Draw_list,Prepare_list,Process_list,Execute_list,sum_time_line_list,flag_list,sorted(sum_time_line_list,reverse=False)]

		data_result=[[app_version],[consum_times],[packapgename],[len(Draw_list)],[int(exceed)],[exceed_percent],[seconds_95_value],[frames_avg],[fps_avg]]

		worksheet.write_row('A1', headings_result, format_title)   #显示fps汇总帧率标题
		worksheet.write_row('E1', [headings_result[4]], format_title_yellew)
		worksheet.write_row('F1', [headings_result[5]], format_title_yellew)
		worksheet.write_row('G1', [headings_result[6]], format_title_yellew)
		worksheet.write_column('A2', data_result[0],format_content)   
		worksheet.write_column('B2', data_result[1],format_content)   
		worksheet.write_column('C2', data_result[2],format_content)   
		worksheet.write_column('D2', data_result[3],format_content)   
		worksheet.write_column('E2', data_result[4],format_content)
		worksheet.write_column('F2', data_result[5],format_content)
		worksheet.write_column('G2', data_result[6],format_content)
		worksheet.write_column('J2', data_result[7],format3)
		worksheet.write_column('K2', data_result[8],format3)

		worksheet.write_row('A5', headings_info, format_title)   #显示fps记录详细信息
		worksheet.write_column('A6', data_info[0],format_content)   
		worksheet.write_column('B6', data_info[1],format_content)   
		worksheet.write_column('C6', data_info[2],format_content)   
		worksheet.write_column('D6', data_info[3],format_content)   
		worksheet.write_column('E6', data_info[4],format_content)  
		worksheet.write_column('F6', data_info[5],format_content)
		worksheet.write_column('G6', data_info[6],format_content)
		worksheet.write_column('H6', data_info[7],format_content)
		worksheet.write_column('I6', data_info[8],format_content)

		#合并H列至I列单元格数据
		worksheet.merge_range('H1:I1',u'NA',format_merge)
		worksheet.merge_range('M36:O36','每次有效采集平均帧率',format_merge)
		for i in range(len(fps_list)):
			worksheet.merge_range('M{}:O{}'.format(37+i,37+i),fps_list[i],format_content)



		worksheet.merge_range('J5:K5',u'每帧耗时升序(ms)排列',format_merge)
		for i in xrange(len(data_info[9])):
			worksheet.merge_range('J{}:K{}'.format(6+i,6+i),data_info[9][i],format_merge_value)

		#如果大于16.0的占比超过50%时，则将对应的单元格设置成黄色背景，红色字体样式

		if int(eval(exceed_percent_value))>=50:
			if system is "Windows":
				window.printRed("每帧耗时大于16.0占比为{}%，超过预定义峰值[50%]\n".format(exceed_percent_value).encode('gbk'))
				logging.info("每帧耗时大于16.0占比为{}%，超过预定义峰值[50%]".format(exceed_percent_value).encode('gbk'))
			else:
				print styles.RED+"每帧耗时大于16.0占比为{}%，超过预定义峰值[50%]\n".format(exceed_percent_value)+styles.ENDC
				logging.info("每帧耗时大于16.0占比为{}%，超过预定义峰值[50%]")
			worksheet.write_column('E2',data_result[4],format1)
		else:
			if system is "Windows":
				logging.info("每帧耗时大于16.0占比为{}%".format(exceed_percent_value).encode('gbk'))
			else:
				logging.info("每帧耗时大于16.0占比为{}%".format(exceed_percent_value))

			worksheet.write_column('E2', data_result[4],format_content)

		row_num=len(sum_time_line_list)
		#创建一个柱形样式和线条样式图表，类型是column、line
		chart1 = self.workbook.add_chart({'type': 'line'})
		chart2 = self.workbook.add_chart({'type': 'column'})

		chart3 = self.workbook.add_chart({'type': 'line'})
		chart4 = self.workbook.add_chart({'type': 'column'})

		#******************内存占用_图表*****************
		chart1.set_drop_lines()
		chart1.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})
		#绘制Draw\Prepare\Process\Execute线形图
		chart1.add_series({
		    'name':       '=fps!$B$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$B$6:$C${}'.format(row_num+5),
		})

		chart1.add_series({
		    'name':       '=fps!$C$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$C$6:$C${}'.format(row_num+5),
		})

		chart1.add_series({
		    'name':       '=fps!$D$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$D$6:$D${}'.format(row_num+5),
		})

		chart1.add_series({
		    'name':       '=fps!$E$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$E$6:$E${}'.format(row_num+5),
		})

		#绘制Draw\Prepare\Process\Execute柱形图
		chart2.add_series({
		    'name':       '=fps!$B$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$B$6:$C${}'.format(row_num+5),
		})

		chart2.add_series({
		    'name':       '=fps!$C$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$C$6:$C${}'.format(row_num+5),
		})

		chart2.add_series({
		    'name':       '=fps!$D$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$D$6:$D${}'.format(row_num+5),
		})

		chart2.add_series({
		    'name':       '=fps!$E$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$E$6:$E${}'.format(row_num+5),
		})


		#绘制每帧耗时ms柱形、线形图
		chart3.add_series({
		    'name':       '=fps!$F$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$F$6:$F${}'.format(row_num+5),
		})


		chart4.add_series({
		    'name':       '=fps!$F$5',
		    'categories': '=fps!$A$6:$A${}'.format(row_num+5),
		    'values':     '=fps!$F$6:$F${}'.format(row_num+5),
		})


		# Add a chart title and some axis labels.
		chart1.set_title ({'name': '进程名:{}\nDraw\Prepare\Process\Execute_柱形图'.format(packapgename)})
		chart1.set_x_axis({'name': '采集序号'})
		chart1.set_y_axis({'name': '消耗时间'})

		chart2.set_title ({'name': '进程名:{}\nDraw\Prepare\Process\Execute_线形图'.format(packapgename)})
		chart2.set_x_axis({'name': '采集序号'})
		chart2.set_y_axis({'name': '消耗时间'})

		chart3.set_title ({'name': '进程名:{}\nFPS每帧时间消耗(ms)_柱形图'.format(packapgename)})
		chart3.set_x_axis({'name': '采集序号'})
		chart3.set_y_axis({'name': '消耗时间'})

		chart4.set_title ({'name': '进程名:{}\nFPS每帧时间消耗(ms)_线形图'.format(packapgename)})
		chart4.set_x_axis({'name': '采集序号'})
		chart4.set_y_axis({'name': '消耗时间'})

		worksheet.insert_chart('L2', chart2, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('L20', chart1, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('T2', chart4, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('T20', chart3, {'x_offset': 25, 'y_offset': 10})


		#计算5%帧图像耗时所对应的行，H列对应单元格的值
		cell_value_95= worksheet._get_range_data(int(seconds_95_+5-1),7,int(seconds_95_+5-1),7)

		if system is "Windows":
			print "95%帧图像耗时在行号为:{0},单元格获取到的值为:{1}".format(int(seconds_95_+5-1),cell_value_95).encode('gbk')
		else:
			print "95%帧图像耗时在行号为:{0},单元格获取到的值为:{1}".format(int(seconds_95_+5-1),cell_value_95)
		# self.workbook.close()
		logging.info('FPS表生成绘制完成!'.encode(str_encode))

	#电压、温度、电量图表生成
	def gen_battery_report(self,device_name,packapgename,delay_time):
		worksheet = self.workbook.add_worksheet("battery")
		app_version=self.android.getAppVersion(device_name,packapgename)  #获取软件版本号

		battery_list,voltage_list,temperature_list,activity_list,time_list,usb_powered_list,\
		wifi_powered_list,Capacity=self.android.get_device_battery_info(device_name,delay_time)

		_time_list=[]
		for time in time_list:

			#分割时间，去掉日期，只取时间
			time=time.split()[-1]
			_time_list.append(time)

		#去掉activity前面的包名
		_activity_list=[]
		for activity in activity_list:
			_activity_list.append(activity.split('/')[-1].strip('.'))


		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_title_yellew=self.workbook.add_format()    #设置title和content样式

		worksheet.set_column('A:A', len(str(_time_list[-1]))+3)  #设置列宽
		worksheet.set_column('B:B', len(str(_activity_list[-1]))+2)
		worksheet.set_column('C:D', len(str(voltage_list[-1]))+13)
		worksheet.set_column('E:E', len(str(voltage_list[-1]))+16)
		worksheet.set_column('F:H', len(str(voltage_list[-1]))+13)
		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')
		format_title.set_font(u'微软雅黑')
		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_title_yellew.set_border(1)
		format_title_yellew.set_font_size(12)
		format_title_yellew.set_align('center')
		format_title_yellew.set_bg_color('#FFFF00')   #设置背景色为黄色
		format_title_yellew.set_font(u'微软雅黑')


		# 这是个数据table的列
		headings_info = [u'获取时间',U'当前界面activity',u'电量(%)',u'电压(mV)',u'温度(0.1度)',u'USB供电状态',u'WIFI供电状态','NA']

		headings_result = [u'APP版本号',u'采样次数',u'开始电量%',u'结束电量%',u'开始电压(mV)','结束电压(mV)','开始温度(0.1度)','结束温度(0.1度)']

		headings_result_v2 = [u'采样时间(s)',u'总电量mAh值',u'电量消耗百分比%',u'电量消耗mAh值',u'平均每秒消耗mAh值','电池升温0.1℃','平均每秒升温0.1℃','NA']

		#计算采样时间，用最后一次获取时间减去第一次采样获取时间
		time_a = datetime.strptime(_time_list[0],'%H:%M:%S')
		time_b = datetime.strptime(_time_list[-1],'%H:%M:%S')
		consum_times=(time_b - time_a).seconds

		#电量消耗百分比
		battery_percent=int(battery_list[0])-int(battery_list[-1])
		# battery_percent=100-85
		#电量消耗mAh值
		if Capacity=='NA':
			battery_Capacity='NA'
		else:
			battery_Capacity=int(Capacity)*battery_percent/100

		#平均每秒消耗mAh值
		if Capacity=='NA':
			battery_Capacity_avg='NA'
		else:
			battery_Capacity_avg='%.3f'%float(float(battery_Capacity)/consum_times)

		#CPU升温
		temperature_up=int(temperature_list[-1])-int(temperature_list[0])
		# temperature_up='%.1f'%float(370-359)
		#平均每秒升温
		temperature_up_avg='%.3f'%float(float(temperature_up)/consum_times)


		data_info=[_time_list,_activity_list,battery_list,voltage_list,temperature_list,usb_powered_list,wifi_powered_list]

		data_result=[[app_version],[len(_time_list)],[battery_list[0]],[battery_list[-1]],[voltage_list[0]],[voltage_list[-1]],[temperature_list[0]],[temperature_list[-1]]]

		data_result_v2=[[consum_times],[Capacity],[battery_percent],[battery_Capacity],[battery_Capacity_avg],[temperature_up],[eval(temperature_up_avg)]]


		worksheet.write_row('A1', headings_result, format_title)   #显示电量，电压，温度汇总信息
		worksheet.write_column('A2', data_result[0],format_content)
		worksheet.write_column('B2', data_result[1],format_content)
		worksheet.write_column('C2', data_result[2],format_content)
		worksheet.write_column('D2', data_result[3],format_content)
		worksheet.write_column('E2', data_result[4],format_content)
		worksheet.write_column('F2', data_result[5],format_content)
		worksheet.write_column('G2', data_result[6],format_content)
		worksheet.write_column('H2', data_result[7],format_content)


		worksheet.write_row('A5', headings_result_v2, format_title)   #显示具体电量mAh值、平均消耗电量mAh值，CPU温升占比等汇总信息
		worksheet.write_row('C5', [headings_result_v2[2]], format_title_yellew)
		worksheet.write_row('D5', [headings_result_v2[3]], format_title_yellew)
		worksheet.write_row('E5', [headings_result_v2[4]], format_title_yellew)
		worksheet.write_row('F5', [headings_result_v2[5]], format_title_yellew)
		worksheet.write_column('A6', data_result_v2[0],format_content)
		worksheet.write_column('B6', data_result_v2[1],format_content)
		worksheet.write_column('C6', data_result_v2[2],format_content)
		worksheet.write_column('D6', data_result_v2[3],format_content)
		worksheet.write_column('E6', data_result_v2[4],format_content)
		worksheet.write_column('F6', data_result_v2[5],format_content)
		worksheet.write_column('G6', data_result_v2[6],format_content)


		worksheet.write_row('A9', headings_info, format_title)   #显示电量，电压，温度详细数据
		worksheet.write_column('A10', data_info[0],format_content)
		worksheet.write_column('B10', data_info[1],format_content)
		worksheet.write_column('C10', data_info[2],format_content)
		worksheet.write_column('D10', data_info[3],format_content)
		worksheet.write_column('E10', data_info[4],format_content)
		worksheet.write_column('F10', data_info[5],format_content)
		worksheet.write_column('G10', data_info[6],format_content)



		row_num=len(battery_list)
		#创建一个柱形样式和线条样式图表，类型是column、line
		chart1 = self.workbook.add_chart({'type': 'line'})
		chart2 = self.workbook.add_chart({'type': 'line'})
		chart3 = self.workbook.add_chart({'type': 'line'})
		chart4 = self.workbook.add_chart({'type': 'column'})
		chart5 = self.workbook.add_chart({'type': 'column'})
		chart6 = self.workbook.add_chart({'type': 'column'})
		#******************电量，温度，电压占用_图表*****************
		chart1.set_drop_lines()
		chart1.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart2.set_drop_lines()
		chart2.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart3.set_drop_lines()
		chart3.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})


		#电量线形图
		chart1.add_series({
		    'name':       '=battery!$C$9',
		    'categories': '=battery!$A$10:$A${}'.format(row_num+9),
		    'values':     '=battery!$C$10:$C${}'.format(row_num+9),
		})
		#电量柱形图
		chart4.add_series({
		    'name':       '=battery!$C$9',
		    'categories': '=battery!$A$10:$A${}'.format(row_num+9),
		    'values':     '=battery!$C$10:$C${}'.format(row_num+9),
		})

		#电压线形图
		chart2.add_series({
		    'name':       '=battery!$D$9',
		    'categories': '=battery!$A$10:$A${}'.format(row_num+9),
		    'values':     '=battery!$D$10:$D${}'.format(row_num+9),
		})
		#电压柱形图
		chart5.add_series({
		    'name':       '=battery!$D$9',
		    'categories': '=battery!$A$10:$A${}'.format(row_num+9),
		    'values':     '=battery!$D$10:$D${}'.format(row_num+9),
		})
		#温度线形图
		chart3.add_series({
		    'name':       '=battery!$E$9',
		    'categories': '=battery!$A$10:$A${}'.format(row_num+9),
		    'values':     '=battery!$E$10:$E${}'.format(row_num+9),
		})
		#温度柱形图
		chart6.add_series({
		    'name':       '=battery!$E$9',
		    'categories': '=battery!$A$10:$A${}'.format(row_num+9),
		    'values':     '=battery!$E$10:$E${}'.format(row_num+9),
		})



		# Add a chart title and some axis labels.
		chart1.set_title ({'name': '电量_线形图'})
		chart1.set_x_axis({'name': '时间分布'})
		chart1.set_y_axis({'name': '类别'})
		# chart1.set_size({'width':720,'height':576})

		chart2.set_title ({'name': '电压_线形图'})
		chart2.set_x_axis({'name': '时间分布'})
		chart2.set_y_axis({'name': '类别'})

		chart3.set_title ({'name': '温度_线形图'})
		chart3.set_x_axis({'name': '时间分布'})
		chart3.set_y_axis({'name': '类别'})

		chart4.set_title ({'name': '电量_柱形图'})
		chart4.set_x_axis({'name': '时间分布'})
		chart4.set_y_axis({'name': '类别'})

		chart5.set_title ({'name': '电压_柱形图'})
		chart5.set_x_axis({'name': '时间分布'})
		chart5.set_y_axis({'name': '类别'})

		chart6.set_title ({'name': '温度_柱形图'})
		chart6.set_x_axis({'name': '时间分布'})
		chart6.set_y_axis({'name': '类别'})


		# chart2.set_size({'width':720,'height':576})

		worksheet.insert_chart('I2', chart1, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('Q2', chart4, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('I20', chart2, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('Q20', chart5, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('I38', chart3, {'x_offset': 25, 'y_offset': 10})
		worksheet.insert_chart('Q38', chart6, {'x_offset': 25, 'y_offset': 10})
		logging.info('Battery表生成绘制完成!'.encode(str_encode))

class MegerResultReport(object):

	def __init__(self):
		global report_merge_name
		#Debug开关用于调试功能时用
		if Debug==False:
			report_merge_name='android_permance_merge_report.xlsx'
			self.workbook = xlsxwriter.Workbook(report_merge_name)
			self.report_path=os.path.abspath(os.getcwd())
		else:
			#获取创建报告时间
			creat_time=time.strftime("%Y_%m_%d_%H_%M_%S")
			#创建excel图表
			report_merge_name='android_permance_merge_report_{}.xlsx'.format(creat_time)
			self.workbook = xlsxwriter.Workbook(report_merge_name)
			self.report_path=os.path.abspath(os.getcwd())



	def __str__(self):
		print "开始生成图表分析合并报告"

	#汇总帧率报告
	def merge_fps_report(self,xlsfile1,xlsfile2):
		worksheet = self.workbook.add_worksheet("fps")
		p1=ReadExcel()
		xlsfile1_fps_row_data,xlsfile2_fps_row_data=p1.readExcelFPS(xlsfile1,xlsfile2)
		print xlsfile1_fps_row_data
		print xlsfile2_fps_row_data


		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_content_red=self.workbook.add_format()

		format_result_title=self.workbook.add_format()

		format_result = self.workbook.add_format()
		format_result.set_text_wrap()   #自动换行
		format_result.set_align('center')  #水平居中
		format_result.set_align('vcenter')  #垂直居中


		worksheet.set_column('A:A',9)  #设置列宽
		worksheet.set_column('B:B', len(str(os.path.basename(xlsfile1)))+2)
		worksheet.set_column('C:D', len(str(xlsfile1_fps_row_data[0]))+13)
		worksheet.set_column('E:E', len(str(xlsfile1_fps_row_data[2]))+5)
		worksheet.set_column('F:K', len(str(xlsfile1_fps_row_data[2]))+3)

		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')
		format_title.set_font(u'微软雅黑')

		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_content_red.set_align('center')
		format_content_red.set_font(u'微软雅黑')
		format_content_red.set_font_size(11)
		format_content_red.set_font_color('#FF0000')


		#根据条件，如包括高、大则标红色
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '高',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '多',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '长',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '大',
                                      'format':   format_content_red})


		format_result_title.set_bold()  #字体加粗
		format_result_title.set_border(1)
		format_result_title.set_font_size(12)
		format_result_title.set_align('center')
		format_result_title.set_bg_color('#cccccc')
		format_result_title.set_font(u'微软雅黑')

		format_result.set_align('center')
		format_result.set_font(u'微软雅黑')
		format_result.set_font_size(11)


		# 这是个数据table的列
		headings_info_1 = ['报告序号','报表名称','APP版本号',u'采样时间(s)',u'进程名','采样总帧数','大于16.0帧数','大于16.0占比','95%的帧耗时',u'平均帧数量',u'平均帧率']

		headings_info_2 = ['报告序号','报表名称','APP版本号',u'采样时间(s)',u'进程名','采样总帧数','大于16.0帧数','大于16.0占比','95%的帧耗时',u'平均帧数量',u'平均帧率']

		headings_result = ['报告汇总','比较方式','APP版本号【比较】','采样时间(s)【比较】',u'进程名【比较】','采样总帧数【比较】','大于16.0帧数【比较】','大于16.0占比【比较】','95%的帧耗时【比较】',u'平均帧数量【比较】',u'平均帧率【比较】']

		data_info_1=[['基线版本'],[os.path.basename(xlsfile1.decode('gbk'))],[xlsfile1_fps_row_data[0]],[xlsfile1_fps_row_data[1]],[xlsfile1_fps_row_data[2]],[xlsfile1_fps_row_data[3]],[xlsfile1_fps_row_data[4]],
		[xlsfile1_fps_row_data[5]],[xlsfile1_fps_row_data[6]],[xlsfile1_fps_row_data[7]],[xlsfile1_fps_row_data[8]]]

		data_info_2=[['测试版本'],[os.path.basename(xlsfile2.decode('gbk'))],[xlsfile2_fps_row_data[0]],[xlsfile2_fps_row_data[1]],[xlsfile2_fps_row_data[2]],[xlsfile2_fps_row_data[3]],[xlsfile2_fps_row_data[4]],
		[xlsfile2_fps_row_data[5]],[xlsfile2_fps_row_data[6]],[xlsfile2_fps_row_data[7]],[xlsfile2_fps_row_data[8]]]


		#版本号比较
		if eval(repr(xlsfile1_fps_row_data[0].encode('utf-8')))==eval(repr(xlsfile2_fps_row_data[0].encode('utf-8'))):
			version_cmp='版本号相等'
		elif eval(repr(xlsfile1_fps_row_data[0].encode('utf-8')))<eval(repr(xlsfile2_fps_row_data[0].encode('utf-8'))):
			version_cmp='版本号高'
		else:
			version_cmp='版本号低'

		if version_cmp=='版本号相等':
			version1='基线版本'
			version2='测试版本'
		else:
			version1='{}版本'.format(eval(repr(xlsfile1_fps_row_data[0].encode('utf-8'))))
			version2='{}版本'.format(eval(repr(xlsfile2_fps_row_data[0].encode('utf-8'))))

		#采样时间比较
		if eval(repr(xlsfile1_fps_row_data[1]))==eval(repr(xlsfile2_fps_row_data[1])):
			time_cmp='采样时间相等'
		elif eval(repr(xlsfile1_fps_row_data[1]))<eval(repr(xlsfile2_fps_row_data[1])):
			out=eval(repr(xlsfile2_fps_row_data[1]))-eval(repr(xlsfile1_fps_row_data[1]))
			time_cmp='【{0}】长{1}s'.format(version2,out)
		else:
			out=eval(repr(xlsfile1_fps_row_data[1]))-eval(repr(xlsfile2_fps_row_data[1]))
			time_cmp='【{0}】短{1}s'.format(version2,out)

		#进程名比较
		if xlsfile1_fps_row_data[2]==xlsfile2_fps_row_data[2]:
			process_cmp='采样进程相同'
		else:
			process_cmp='采样进程不相同'

		#采样总帧数比较
		if xlsfile1_fps_row_data[3]==xlsfile2_fps_row_data[3]:
			frames_cmp='采样总帧数相同'
		elif xlsfile1_fps_row_data[3]<xlsfile2_fps_row_data[3]:
			frames_cmp='【{0}】多{1}帧数'.format(version2,xlsfile2_fps_row_data[3]-xlsfile1_fps_row_data[3])
		else:
			frames_cmp='【{0}】少{1}帧数'.format(version2,xlsfile1_fps_row_data[3]-xlsfile2_fps_row_data[3])

		#大于16.0帧数比较
		if xlsfile1_fps_row_data[4]==xlsfile2_fps_row_data[4]:
			frames_more_cmp='大于16.0的帧数相同'
		elif xlsfile1_fps_row_data[4]<xlsfile2_fps_row_data[4]:
			frames_more_cmp='【{0}】多{1}帧'.format(version2,xlsfile2_fps_row_data[4]-xlsfile1_fps_row_data[4])
		else:
			frames_more_cmp='【{0}】少{1}帧'.format(version2,xlsfile1_fps_row_data[4]-xlsfile2_fps_row_data[4])

		#大于16.0帧数占比比较
		if eval(xlsfile1_fps_row_data[5].strip('%'))==eval(xlsfile2_fps_row_data[5].strip('%')):
			frames_precent_cmp='大于16.0的帧数占比相同'
		elif eval(xlsfile1_fps_row_data[5].strip('%'))<eval(xlsfile2_fps_row_data[5].strip('%')):
			frames_precent_cmp='【{0}】高{1}%'.format(version2,eval(xlsfile2_fps_row_data[5].strip('%'))-eval(xlsfile1_fps_row_data[5].strip('%')))
		else:
			frames_precent_cmp='【{0}】少{1}%'.format(version2,eval(xlsfile1_fps_row_data[5].strip('%'))-eval(xlsfile2_fps_row_data[5].strip('%')))

		#95%的帧耗时比较
		if xlsfile1_fps_row_data[6]==xlsfile2_fps_row_data[6]:
			frames_time_cmp='95%的帧耗时相同'
		elif xlsfile1_fps_row_data[6]<xlsfile2_fps_row_data[6]:
			frames_time_cmp='【{0}】多{1}s'.format(version2,xlsfile2_fps_row_data[6]-xlsfile1_fps_row_data[6])
		else:
			frames_time_cmp='【{0}】少{1}s'.format(version2,xlsfile1_fps_row_data[6]-xlsfile2_fps_row_data[6])

		#平均帧数量比较
		if xlsfile1_fps_row_data[7]==xlsfile2_fps_row_data[7]:
			frames_avg_cmp='平均帧数量相同'
		elif xlsfile1_fps_row_data[7]<xlsfile2_fps_row_data[7]:
			frames_avg_cmp='【{0}】多{1}帧'.format(version2,xlsfile2_fps_row_data[7]-xlsfile1_fps_row_data[7])
		else:
			frames_avg_cmp='【{0}】少{1}帧'.format(version2,xlsfile1_fps_row_data[7]-xlsfile2_fps_row_data[7])

		#平均帧率比较
		if xlsfile1_fps_row_data[8]==xlsfile2_fps_row_data[8]:
			frames_fps_cmp='平均帧率相同'
		elif xlsfile1_fps_row_data[8]<xlsfile2_fps_row_data[8]:
			frames_fps_cmp='【{0}】多{1}帧'.format(version2,xlsfile2_fps_row_data[8]-xlsfile1_fps_row_data[8])
		else:
			frames_fps_cmp='【{0}】少{1}帧'.format(version2,xlsfile1_fps_row_data[8]-xlsfile2_fps_row_data[8])


		data_result=[['结论'],['【测试版本】 vs 【基线版本】'],[version_cmp],[time_cmp],[process_cmp],[frames_cmp],[frames_more_cmp],[frames_precent_cmp],[frames_time_cmp],
					 [frames_avg_cmp],[frames_fps_cmp]]

		worksheet.write_row('A1', headings_info_1, format_title)   #fps表1
		worksheet.write_column('A2', data_info_1[0],format_content)
		worksheet.write_column('B2', data_info_1[1],format_content)
		worksheet.write_column('C2', data_info_1[2],format_content)
		worksheet.write_column('D2', data_info_1[3],format_content)
		worksheet.write_column('E2', data_info_1[4],format_content)
		worksheet.write_column('F2', data_info_1[5],format_content)
		worksheet.write_column('G2', data_info_1[6],format_content)
		worksheet.write_column('H2', data_info_1[7],format_content)
		worksheet.write_column('I2', data_info_1[8],format_content)
		worksheet.write_column('J2', data_info_1[9],format_content)
		worksheet.write_column('K2', data_info_1[10],format_content)


		# worksheet.write_row('A5', headings_info_2, format_title)   #fps表二
		worksheet.write_column('A3', data_info_2[0],format_content)
		worksheet.write_column('B3', data_info_2[1],format_content)
		worksheet.write_column('C3', data_info_2[2],format_content)
		worksheet.write_column('D3', data_info_2[3],format_content)
		worksheet.write_column('E3', data_info_2[4],format_content)
		worksheet.write_column('F3', data_info_2[5],format_content)
		worksheet.write_column('G3', data_info_2[6],format_content)
		worksheet.write_column('H3', data_info_2[7],format_content)
		worksheet.write_column('I3', data_info_2[8],format_content)
		worksheet.write_column('J3', data_info_2[9],format_content)
		worksheet.write_column('K3', data_info_2[10],format_content)

		worksheet.write_row('A7', headings_result, format_result_title)   #fps汇总表
		worksheet.write_column('A8', data_result[0],format_result)
		worksheet.write_column('B8', data_result[1],format_result)
		worksheet.write_column('C8', data_result[2],format_result)
		worksheet.write_column('D8', data_result[3],format_result)
		worksheet.write_column('E8', data_result[4],format_result)
		worksheet.write_column('F8', data_result[5],format_result)
		worksheet.write_column('G8', data_result[6],format_result)
		worksheet.write_column('H8', data_result[7],format_result)
		worksheet.write_column('I8', data_result[8],format_result)
		worksheet.write_column('J8', data_result[9],format_result)
		worksheet.write_column('K8', data_result[10],format_result)
		print "执行结束".encode('gbk')




	#汇总cpu报告
	def merge_cpu_report(self,xlsfile1,xlsfile2):
		worksheet = self.workbook.add_worksheet("cpu")
		p1=ReadExcel()
		xlsfile1_cpu_row_data,xlsfile2_cpu_row_data=p1.readExcelCPU(xlsfile1,xlsfile2)
		print xlsfile1_cpu_row_data
		print xlsfile2_cpu_row_data

		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()

		format_content_red=self.workbook.add_format()

		format_result_title=self.workbook.add_format()

		format_result = self.workbook.add_format()
		format_result.set_text_wrap()   #自动换行
		format_result.set_align('center')  #水平居中
		format_result.set_align('vcenter')  #垂直居中


		worksheet.set_column('A:A',9)  #设置列宽
		worksheet.set_column('B:B', len(str(os.path.basename(xlsfile1)))+2)
		worksheet.set_column('C:I', len(str(xlsfile1_cpu_row_data[2]))+10)


		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')
		format_title.set_font(u'微软雅黑')

		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_content_red.set_align('center')
		format_content_red.set_font(u'微软雅黑')
		format_content_red.set_font_size(11)
		format_content_red.set_font_color('#FF0000')

		#根据条件，如包括高、大则标红色
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '高',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '多',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '长',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '大',
                                      'format':   format_content_red})
		format_result_title.set_bold()  #字体加粗
		format_result_title.set_border(1)
		format_result_title.set_font_size(12)
		format_result_title.set_align('center')
		format_result_title.set_bg_color('#cccccc')
		format_result_title.set_font(u'微软雅黑')

		format_result.set_align('center')
		format_result.set_font(u'微软雅黑')
		format_result.set_font_size(11)


		# 这是个数据table的列
		headings_info_1 = ['报告序号','报表名称','APP版本号',u'采样时间(s)',u'进程名','采样次数','CPU使用均值%','CPU用户占用均值%','CPU占用均值(Top)%']

		# headings_info_2 = ['报告序号','报表名称','APP版本号',u'采样时间(s)',u'进程名','采样次数','CPU最大值%','CPU平均值%','CPU最小值%']

		headings_result = ['报告汇总','比较方式','APP版本号【比较】','采样时间(s)【比较】',u'进程名【比较】','采样次数【比较】','CPU使用均值【比较】','CPU用户均值【比较】','CPU占用均值(Top)【比较】']


		data_info_1=[['基线版本'],[os.path.basename(xlsfile1.decode('gbk'))],[xlsfile1_cpu_row_data[0]],[xlsfile1_cpu_row_data[1]],[xlsfile1_cpu_row_data[2]],[xlsfile1_cpu_row_data[3]],[xlsfile1_cpu_row_data[4]],
		[xlsfile1_cpu_row_data[5]],[xlsfile1_cpu_row_data[6]]]

		data_info_2=[['测试版本'],[os.path.basename(xlsfile2.decode('gbk'))],[xlsfile2_cpu_row_data[0]],[xlsfile2_cpu_row_data[1]],[xlsfile2_cpu_row_data[2]],[xlsfile2_cpu_row_data[3]],[xlsfile2_cpu_row_data[4]],
		[xlsfile2_cpu_row_data[5]],[xlsfile2_cpu_row_data[6]]]


		#版本号比较
		if eval(repr(xlsfile1_cpu_row_data[0].encode('utf-8')))==eval(repr(xlsfile2_cpu_row_data[0].encode('utf-8'))):
			version_cmp='版本号相等'
		elif eval(repr(xlsfile1_cpu_row_data[0].encode('utf-8')))<eval(repr(xlsfile2_cpu_row_data[0].encode('utf-8'))):
			version_cmp='版本号高'
		else:
			version_cmp='版本号低'

		if version_cmp=='版本号相等':
			version1='基线版本'
			version2='测试版本'
		else:
			version1='{}版本'.format(eval(repr(xlsfile1_cpu_row_data[0].encode('utf-8'))))
			version2='{}版本'.format(eval(repr(xlsfile2_cpu_row_data[0].encode('utf-8'))))

		#采样时间比较
		if eval(repr(xlsfile1_cpu_row_data[1]))==eval(repr(xlsfile2_cpu_row_data[1])):
			time_cmp='采样时间相等'
		elif eval(repr(xlsfile1_cpu_row_data[1]))<eval(repr(xlsfile2_cpu_row_data[1])):
			out=eval(repr(xlsfile2_cpu_row_data[1]))-eval(repr(xlsfile1_cpu_row_data[1]))
			time_cmp='【{0}】长{1}s'.format(version2,out)
		else:
			out=eval(repr(xlsfile1_cpu_row_data[1]))-eval(repr(xlsfile2_cpu_row_data[1]))
			time_cmp='【{0}】短{1}s'.format(version2,out)


		#进程名比较
		if xlsfile1_cpu_row_data[2]==xlsfile2_cpu_row_data[2]:
			process_cmp='采样进程相同'
		else:
			process_cmp='采样进程不相同'

		#采样次数比较
		if xlsfile1_cpu_row_data[3]==xlsfile2_cpu_row_data[3]:
			times_cmp='采样次数相同'.format(version1,version2)
		elif xlsfile1_cpu_row_data[3]<xlsfile2_cpu_row_data[3]:
			times_cmp='【{0}】多{1}次'.format(version2,xlsfile2_cpu_row_data[3]-xlsfile1_cpu_row_data[3])

		else:
			times_cmp='【{0}】少{1}次'.format(version2,xlsfile1_cpu_row_data[3]-xlsfile2_cpu_row_data[3])


		#CPU使用均值%比较
		if xlsfile1_cpu_row_data[4]==xlsfile2_cpu_row_data[4]:
			cpu_avg_cmp='CPU使用均值相同'
		elif xlsfile1_cpu_row_data[4]<xlsfile2_cpu_row_data[4]:
			cpu_avg_cmp='【{0}】高{1}%'.format(version2,xlsfile2_cpu_row_data[4]-xlsfile1_cpu_row_data[4])

		else:
			cpu_avg_cmp='【{0}】低{1}%'.format(version2,xlsfile1_cpu_row_data[4]-xlsfile2_cpu_row_data[4])


		#CPU用户占用均值%
		if xlsfile1_cpu_row_data[5]==xlsfile2_cpu_row_data[5]:
			cpu_avg_user_cmp='CPU用户占用均值相同'
		elif xlsfile1_cpu_row_data[5]<xlsfile2_cpu_row_data[5]:
			cpu_avg_user_cmp='【{0}】高{1}%'.format(version2,xlsfile2_cpu_row_data[5]-xlsfile1_cpu_row_data[5])

		else:
			cpu_avg_user_cmp='【{0}】少{1}%'.format(version2,xlsfile1_cpu_row_data[5]-xlsfile2_cpu_row_data[5])


		#CPU占用均值(Top)%
		if xlsfile1_cpu_row_data[6]==xlsfile2_cpu_row_data[6]:
			cpu_avg_cmp_top='CPU占用均值(Top)相同'
		elif xlsfile1_cpu_row_data[6]<xlsfile2_cpu_row_data[6]:
			cpu_avg_cmp_top='【{0}】高{1}%'.format(version2,xlsfile2_cpu_row_data[6]-xlsfile1_cpu_row_data[6])

		else:
			cpu_avg_cmp_top='【{0}】少{1}%'.format(version2,xlsfile1_cpu_row_data[6]-xlsfile2_cpu_row_data[6])




		data_result=[['结论'],['【测试版本】 vs 【基线版本】'],[version_cmp],[time_cmp],[process_cmp],[times_cmp],[cpu_avg_cmp],[cpu_avg_user_cmp],[cpu_avg_cmp_top]]

		worksheet.write_row('A1', headings_info_1, format_title)   #cpu表1
		worksheet.write_column('A2', data_info_1[0],format_content)
		worksheet.write_column('B2', data_info_1[1],format_content)
		worksheet.write_column('C2', data_info_1[2],format_content)
		worksheet.write_column('D2', data_info_1[3],format_content)
		worksheet.write_column('E2', data_info_1[4],format_content)
		worksheet.write_column('F2', data_info_1[5],format_content)
		worksheet.write_column('G2', data_info_1[6],format_content)
		worksheet.write_column('H2', data_info_1[7],format_content)
		worksheet.write_column('I2', data_info_1[8],format_content)


		# worksheet.write_row('A5', headings_info_2, format_title)   #cpu表二
		worksheet.write_column('A3', data_info_2[0],format_content)
		worksheet.write_column('B3', data_info_2[1],format_content)
		worksheet.write_column('C3', data_info_2[2],format_content)
		worksheet.write_column('D3', data_info_2[3],format_content)
		worksheet.write_column('E3', data_info_2[4],format_content)
		worksheet.write_column('F3', data_info_2[5],format_content)
		worksheet.write_column('G3', data_info_2[6],format_content)
		worksheet.write_column('H3', data_info_2[7],format_content)
		worksheet.write_column('I3', data_info_2[8],format_content)


		worksheet.write_row('A7', headings_result, format_result_title)   #cpu汇总表
		worksheet.write_column('A8', data_result[0],format_result)
		worksheet.write_column('B8', data_result[1],format_result)
		worksheet.write_column('C8', data_result[2],format_result)
		worksheet.write_column('D8', data_result[3],format_result)
		worksheet.write_column('E8', data_result[4],format_result)
		worksheet.write_column('F8', data_result[5],format_result)
		worksheet.write_column('G8', data_result[6],format_result)
		worksheet.write_column('H8', data_result[7],format_result)
		worksheet.write_column('I8', data_result[8],format_result)


	#汇总net报告
	def merge_net_report(self,xlsfile1,xlsfile2):
		worksheet = self.workbook.add_worksheet("net")
		p1=ReadExcel()
		xlsfile1_net_row_data,xlsfile2_net_row_data=p1.readExcelNET(xlsfile1,xlsfile2)
		print xlsfile1_net_row_data
		print xlsfile2_net_row_data

		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_content_red=self.workbook.add_format()

		format_result_title=self.workbook.add_format()

		format_result = self.workbook.add_format()
		format_result.set_text_wrap()   #自动换行
		format_result.set_align('center')  #水平居中
		format_result.set_align('vcenter')  #垂直居中


		worksheet.set_column('A:A',9)  #设置列宽
		worksheet.set_column('B:B', len(str(os.path.basename(xlsfile1)))+2)
		worksheet.set_column('C:J', len(str(xlsfile1_net_row_data[3]))+8)


		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')
		format_title.set_font(u'微软雅黑')

		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_content_red.set_align('center')
		format_content_red.set_font(u'微软雅黑')
		format_content_red.set_font_size(11)
		format_content_red.set_font_color('#FF0000')

		#根据条件，如包括高、大则标红色
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '高',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '多',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '长',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '大',
                                      'format':   format_content_red})

		format_result_title.set_bold()  #字体加粗
		format_result_title.set_border(1)
		format_result_title.set_font_size(12)
		format_result_title.set_align('center')
		format_result_title.set_bg_color('#cccccc')
		format_result_title.set_font(u'微软雅黑')

		format_result.set_align('center')
		format_result.set_font(u'微软雅黑')
		format_result.set_font_size(11)


		# 这是个数据table的列
		headings_info_1 = ['报告序号','报表名称','APP版本号',u'采样时间(s)','采样次数',u'进程名','接收字节数总和','发送总字节数总和','TCP接收字节消耗','TCP发送字节消耗']

		headings_info_2 = ['报告序号','报表名称','APP版本号',u'采样时间(s)','采样次数',u'进程名','接收字节数总和','发送总字节数总和','TCP接收字节消耗','TCP发送字节消耗']

		headings_result = ['报告汇总','比较方式','APP版本号【比较】',u'采样时间(s)【比较】',u'采样次数【比较】',u'进程名【比较】','接收字节数总和【比较】','发送总字节数总和【比较】','TCP接收字节消耗【比较】','TCP发送字节消耗【比较】']


		data_info_1=[['基线版本'],[os.path.basename(xlsfile1.decode('gbk'))],[xlsfile1_net_row_data[0]],[xlsfile1_net_row_data[1]],[xlsfile1_net_row_data[2]],[xlsfile1_net_row_data[3]],[xlsfile1_net_row_data[4]],
		[xlsfile1_net_row_data[5]],[xlsfile1_net_row_data[6]],[xlsfile1_net_row_data[7]]]

		data_info_2=[['测试版本'],[os.path.basename(xlsfile2.decode('gbk'))],[xlsfile2_net_row_data[0]],[xlsfile2_net_row_data[1]],[xlsfile2_net_row_data[2]],[xlsfile2_net_row_data[3]],[xlsfile2_net_row_data[4]],
		[xlsfile2_net_row_data[5]],[xlsfile2_net_row_data[6]],[xlsfile2_net_row_data[7]]]


		#版本号比较
		if eval(repr(xlsfile1_net_row_data[0].encode('utf-8')))==eval(repr(xlsfile2_net_row_data[0].encode('utf-8'))):
			version_cmp='版本号相等'
		elif eval(repr(xlsfile1_net_row_data[0].encode('utf-8')))<eval(repr(xlsfile2_net_row_data[0].encode('utf-8'))):
			version_cmp='版本号高'
		else:
			version_cmp='版本号低'

		if version_cmp=='版本号相等':
			version1='基线版本'
			version2='测试版本'
		else:
			version1='{}版本'.format(eval(repr(xlsfile1_net_row_data[0].encode('utf-8'))))
			version2='{}版本'.format(eval(repr(xlsfile2_net_row_data[0].encode('utf-8'))))

		#采样时间比较
		if eval(repr(xlsfile1_net_row_data[1]))==eval(repr(xlsfile2_net_row_data[1])):
			time_cmp='采样时间相等'
		elif eval(repr(xlsfile1_net_row_data[1]))<eval(repr(xlsfile2_net_row_data[1])):
			out=eval(repr(xlsfile2_net_row_data[1]))-eval(repr(xlsfile1_net_row_data[1]))
			time_cmp='【{0}】长{1}s'.format(version2,out)
		else:
			out=eval(repr(xlsfile1_net_row_data[1]))-eval(repr(xlsfile2_net_row_data[1]))
			time_cmp='【{0}】短{1}s'.format(version2,out)

		#进程名比较
		if xlsfile1_net_row_data[3]==xlsfile2_net_row_data[3]:
			process_cmp='采样进程相同'
		else:
			process_cmp='采样进程不相同'

		#采样次数比较
		if xlsfile1_net_row_data[2]==xlsfile2_net_row_data[2]:
			times_cmp='采样次数相同'.format(version1,version2)
		elif xlsfile1_net_row_data[2]<xlsfile2_net_row_data[2]:
			times_cmp='【{0}】多{1}次'.format(version2,xlsfile2_net_row_data[2]-xlsfile1_net_row_data[2])
		else:
			times_cmp='【{0}】少{1}次'.format(version2,xlsfile1_net_row_data[2]-xlsfile2_net_row_data[2])

		#接收总字节数比较
		if xlsfile1_net_row_data[4]==xlsfile2_net_row_data[4]:
			cpu_rec_cmp='接收总字节数相同'
		elif xlsfile1_net_row_data[4]<xlsfile2_net_row_data[4]:
			cpu_rec_cmp='【{0}】多{1}KB'.format(version2,xlsfile2_net_row_data[4]-xlsfile1_net_row_data[4])
		else:
			cpu_rec_cmp='【{0}】少{1}KB'.format(version2,xlsfile1_net_row_data[4]-xlsfile2_net_row_data[4])

		#发送总字节数比较
		if xlsfile1_net_row_data[5]==xlsfile2_net_row_data[5]:
			cpu_send_cmp='发送总字节数相同'
		elif xlsfile1_net_row_data[5]<xlsfile2_net_row_data[5]:
			cpu_send_cmp='【{0}】高{1}KB'.format(version2,xlsfile2_net_row_data[5]-xlsfile1_net_row_data[5])
		else:
			cpu_send_cmp='【{0}】少{1}KB'.format(version2,xlsfile1_net_row_data[5]-xlsfile2_net_row_data[5])

		#NET接收总数据比较
		if xlsfile1_net_row_data[6]==xlsfile2_net_row_data[6]:
			cpu_rec_net_cmp='NET接收总数据相同'
		elif xlsfile1_net_row_data[6]<xlsfile2_net_row_data[6]:
			cpu_rec_net_cmp='【{0}】高{1}KB'.format(version2,xlsfile2_net_row_data[6]-xlsfile1_net_row_data[6])
		else:
			cpu_rec_net_cmp='【{0}】少{1}KB'.format(version2,xlsfile1_net_row_data[6]-xlsfile2_net_row_data[6])

		#NET发送总数据比较
		if xlsfile1_net_row_data[7]==xlsfile2_net_row_data[7]:
			cpu_send_net_cmp='NET发送总数据相同'
		elif xlsfile1_net_row_data[7]<xlsfile2_net_row_data[7]:
			cpu_send_net_cmp='【{0}】高{1}KB'.format(version2,xlsfile2_net_row_data[7]-xlsfile1_net_row_data[7])
		else:
			cpu_send_net_cmp='【{0}】少{1}KB'.format(version2,xlsfile1_net_row_data[7]-xlsfile2_net_row_data[7])


		data_result=[['结论'],['【测试版本】 vs 【基线版本】'],[version_cmp],[time_cmp],[times_cmp],[process_cmp],[cpu_rec_cmp],[cpu_send_cmp],[cpu_rec_net_cmp],[cpu_send_net_cmp]]

		worksheet.write_row('A1', headings_info_1, format_title)   #net表1
		worksheet.write_column('A2', data_info_1[0],format_content)
		worksheet.write_column('B2', data_info_1[1],format_content)
		worksheet.write_column('C2', data_info_1[2],format_content)
		worksheet.write_column('D2', data_info_1[3],format_content)
		worksheet.write_column('E2', data_info_1[4],format_content)
		worksheet.write_column('F2', data_info_1[5],format_content)
		worksheet.write_column('G2', data_info_1[6],format_content)
		worksheet.write_column('H2', data_info_1[7],format_content)
		worksheet.write_column('I2', data_info_1[8],format_content)
		worksheet.write_column('J2', data_info_1[9],format_content)

		# worksheet.write_row('A5', headings_info_2, format_title)   #net表二
		worksheet.write_column('A3', data_info_2[0],format_content)
		worksheet.write_column('B3', data_info_2[1],format_content)
		worksheet.write_column('C3', data_info_2[2],format_content)
		worksheet.write_column('D3', data_info_2[3],format_content)
		worksheet.write_column('E3', data_info_2[4],format_content)
		worksheet.write_column('F3', data_info_2[5],format_content)
		worksheet.write_column('G3', data_info_2[6],format_content)
		worksheet.write_column('H3', data_info_2[7],format_content)
		worksheet.write_column('I3', data_info_2[8],format_content)
		worksheet.write_column('J3', data_info_2[9],format_content)


		worksheet.write_row('A7', headings_result, format_result_title)   #net汇总表
		worksheet.write_column('A8', data_result[0],format_result)
		worksheet.write_column('B8', data_result[1],format_result)
		worksheet.write_column('C8', data_result[2],format_result)
		worksheet.write_column('D8', data_result[3],format_result)
		worksheet.write_column('E8', data_result[4],format_result)
		worksheet.write_column('F8', data_result[5],format_result)
		worksheet.write_column('G8', data_result[6],format_result)
		worksheet.write_column('H8', data_result[7],format_result)
		worksheet.write_column('I8', data_result[8],format_result)
		worksheet.write_column('J8', data_result[9],format_result)

	#汇总battery报告
	def merge_battery_report(self,xlsfile1,xlsfile2):
		worksheet = self.workbook.add_worksheet("battery")
		p1=ReadExcel()
		xlsfile1_battery_row_data,xlsfile1_battery_row6_data,xlsfile2_battery_row_data,xlsfile2_battery_row6_data=p1.readExcelBattery(xlsfile1,xlsfile2)
		print xlsfile1_battery_row_data
		print xlsfile1_battery_row6_data
		print xlsfile2_battery_row_data
		print xlsfile2_battery_row6_data

		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_content_red=self.workbook.add_format()

		format_result_title=self.workbook.add_format()

		format_result = self.workbook.add_format()
		format_result.set_text_wrap()   #自动换行
		format_result.set_align('center')  #水平居中
		format_result.set_align('vcenter')  #垂直居中


		worksheet.set_column('A:A',9)  #设置列宽
		worksheet.set_column('B:B', len(str(os.path.basename(xlsfile1)))+2)
		worksheet.set_column('C:C', len(str(xlsfile1_battery_row_data[3]))+15)
		worksheet.set_column('D:J', len(str(xlsfile1_battery_row_data[3]))+19)
		worksheet.set_column('G:G', len(str(xlsfile1_battery_row_data[3]))+22)

		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')
		format_title.set_font(u'微软雅黑')

		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_content_red.set_align('center')
		format_content_red.set_font(u'微软雅黑')
		format_content_red.set_font_size(11)
		format_content_red.set_font_color('#FF0000')

		#根据条件，如包括高、大则标红色
		worksheet.conditional_format('A14:M14', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '高',
                                      'format':   format_content_red})
		worksheet.conditional_format('A14:M14', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '多',
                                      'format':   format_content_red})
		worksheet.conditional_format('A14:M14', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '长',
                                      'format':   format_content_red})
		worksheet.conditional_format('A14:M14', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '大',
                                      'format':   format_content_red})

		worksheet.conditional_format('A17:M17', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '高',
                                      'format':   format_content_red})
		worksheet.conditional_format('A17:M17', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '多',
                                      'format':   format_content_red})
		worksheet.conditional_format('A17:M17', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '长',
                                      'format':   format_content_red})
		worksheet.conditional_format('A17:M17', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '大',
                                      'format':   format_content_red})
		format_result_title.set_bold()  #字体加粗
		format_result_title.set_border(1)
		format_result_title.set_font_size(12)
		format_result_title.set_align('center')
		format_result_title.set_bg_color('#cccccc')
		format_result_title.set_font(u'微软雅黑')

		format_result.set_align('center')
		format_result.set_font(u'微软雅黑')
		format_result.set_font_size(11)
		#
		#
		# 这是个数据table的列
		headings_info_1_1 = ['报告序号','报表名称','APP版本号','采样次数',u'开始电量%','结束电量%','开始电压(mV)','结束电压(mV)','开始温度(0.1度)','结束温度(0.1度)']
		headings_info_1_2 = ['报告序号','报表名称','采样时间(s)','总电量mAh值',u'电量消耗百分比%','电量消耗mAh值','平均每秒消耗mAh值','CPU升温℃','平均每秒升温℃','NA']

		headings_info_2_1 = ['报告序号','报表名称','APP版本号','采样次数',u'开始电量%','结束电量%','开始电压(mV)','结束电压(mV)','开始温度(0.1度)','结束温度(0.1度)']
		headings_info_2_2 = ['报告序号','报表名称','采样时间(s)','总电量mAh值',u'电量消耗百分比%','电量消耗mAh值','平均每秒消耗mAh值','CPU升温℃','平均每秒升温℃','NA']

		headings_result_1 = ['报告汇总','比较方式','APP版本号【比较】','采样次数【比较】',u'开始电量%【比较】','结束电量%【比较】','开始电压(mV)【比较】','结束电压(mV)【比较】','开始温度(0.1度)【比较】','结束温度(0.1度)【比较】']
		headings_result_2 = ['报告汇总','比较方式','采样时间(s)【比较】','总电量mAh值【比较】',u'电量消耗百分比%【比较】','电量消耗mAh值【比较】','平均每秒消耗mAh值【比较】','CPU升温℃【比较】','平均每秒升温℃【比较】','NA']


		data_info_1_1=[['基线版本'],[os.path.basename(xlsfile1.decode('gbk'))],[xlsfile1_battery_row_data[0]],[xlsfile1_battery_row_data[1]],[xlsfile1_battery_row_data[2]],[xlsfile1_battery_row_data[3]],[xlsfile1_battery_row_data[4]],
		[xlsfile1_battery_row_data[5]],[xlsfile1_battery_row_data[6]],[xlsfile1_battery_row_data[7]]]

		data_info_1_2=[['基线版本'],[os.path.basename(xlsfile1.decode('gbk'))],[xlsfile1_battery_row6_data[0]],[xlsfile1_battery_row6_data[1]],[xlsfile1_battery_row6_data[2]],[xlsfile1_battery_row6_data[3]],[xlsfile1_battery_row6_data[4]],
		[xlsfile1_battery_row6_data[5]],[xlsfile1_battery_row6_data[6]],[xlsfile1_battery_row6_data[7]]]

		data_info_2_1=[['测试版本'],[os.path.basename(xlsfile2.decode('gbk'))],[xlsfile2_battery_row_data[0]],[xlsfile2_battery_row_data[1]],[xlsfile2_battery_row_data[2]],[xlsfile2_battery_row_data[3]],[xlsfile2_battery_row_data[4]],
		[xlsfile2_battery_row_data[5]],[xlsfile2_battery_row_data[6]],[xlsfile2_battery_row_data[7]]]

		data_info_2_2=[['测试版本'],[os.path.basename(xlsfile2.decode('gbk'))],[xlsfile2_battery_row6_data[0]],[xlsfile2_battery_row6_data[1]],[xlsfile2_battery_row6_data[2]],[xlsfile2_battery_row6_data[3]],[xlsfile2_battery_row6_data[4]],
		[xlsfile2_battery_row6_data[5]],[xlsfile2_battery_row6_data[6]],[xlsfile2_battery_row6_data[7]]]




		#版本号比较
		if eval(repr(xlsfile1_battery_row_data[0].encode('utf-8')))==eval(repr(xlsfile2_battery_row_data[0].encode('utf-8'))):
			version_cmp='版本号相等'
		elif eval(repr(xlsfile1_battery_row_data[0].encode('utf-8')))<eval(repr(xlsfile2_battery_row_data[0].encode('utf-8'))):
			version_cmp='版本号高'
		else:
			version_cmp='版本号低'

		if version_cmp=='版本号相等':
			version1='基线版本'
			version2='测试版本'
		else:
			version1='{}版本'.format(eval(repr(xlsfile1_battery_row_data[0].encode('utf-8'))))
			version2='{}版本'.format(eval(repr(xlsfile2_battery_row_data[0].encode('utf-8'))))

		#采样次数比较
		if xlsfile1_battery_row_data[1]==xlsfile2_battery_row_data[1]:
			times_cmp='采样次数相等'
		elif xlsfile1_battery_row_data[1]<xlsfile2_battery_row_data[1]:
			out=xlsfile2_battery_row_data[1]-xlsfile1_battery_row_data[1]
			times_cmp='【{0}】多{1}次'.format(version2,out)
		else:
			out=xlsfile1_battery_row_data[1]-xlsfile2_battery_row_data[1]
			times_cmp='【{0}】少{1}次'.format(version2,out)

		#开始电量比较
		if xlsfile1_battery_row_data[2]==xlsfile2_battery_row_data[2]:
			start_battery_cmp='开始电量相等'
		elif xlsfile1_battery_row_data[2]<xlsfile2_battery_row_data[2]:
			out=xlsfile2_battery_row_data[2]-xlsfile1_battery_row_data[2]
			start_battery_cmp='【{0}】多{1}%'.format(version2,out)
		else:
			out=xlsfile1_battery_row_data[2]-xlsfile2_battery_row_data[2]
			start_battery_cmp='【{0}】少{1}%'.format(version2,out)

		#结束电量比较
		if xlsfile1_battery_row_data[3]==xlsfile2_battery_row_data[3]:
			end_battery_cmp='结束电量相等'
		elif xlsfile1_battery_row_data[3]<xlsfile2_battery_row_data[3]:
			out=xlsfile2_battery_row_data[3]-xlsfile1_battery_row_data[3]
			end_battery_cmp='【{0}】多{1}%'.format(version2,out)
		else:
			out=xlsfile1_battery_row_data[3]-xlsfile2_battery_row_data[3]
			end_battery_cmp='【{0}】少{1}%'.format(version2,out)

		#开始电压比较
		if xlsfile1_battery_row_data[4]==xlsfile2_battery_row_data[4]:
			start_vol_cmp='开始电压相等'
		elif xlsfile1_battery_row_data[4]<xlsfile2_battery_row_data[4]:
			out=xlsfile2_battery_row_data[4]-xlsfile1_battery_row_data[4]
			start_vol_cmp='【{0}】高{1}mV'.format(version2,out)
		else:
			out=xlsfile1_battery_row_data[4]-xlsfile2_battery_row_data[4]
			start_vol_cmp='【{0}】低{1}mV'.format(version2,out)

		#结束电压比较
		if xlsfile1_battery_row_data[5]==xlsfile2_battery_row_data[5]:
			end_vol_cmp='结束电压相等'
		elif xlsfile1_battery_row_data[5]<xlsfile2_battery_row_data[5]:
			out=xlsfile2_battery_row_data[5]-xlsfile1_battery_row_data[5]
			end_vol_cmp='【{0}】高{1}mV'.format(version2,out)
		else:
			out=xlsfile1_battery_row_data[5]-xlsfile2_battery_row_data[5]
			end_vol_cmp='【{0}】低{1}mV'.format(version2,out)

		#开始温度比较
		if xlsfile1_battery_row_data[6]==xlsfile2_battery_row_data[6]:
			start_temp_cmp='开始温度相等'
		elif xlsfile1_battery_row_data[6]<xlsfile2_battery_row_data[6]:
			out=xlsfile2_battery_row_data[6]-xlsfile1_battery_row_data[6]
			start_temp_cmp='【{0}】高{1}℃'.format(version2,out*0.1)
		else:
			out=xlsfile1_battery_row_data[6]-xlsfile2_battery_row_data[6]
			start_temp_cmp='【{0}】低{1}℃'.format(version2,out*0.1)


		#结束温度比较
		if xlsfile1_battery_row_data[7]==xlsfile2_battery_row_data[7]:
			end_temp_cmp='结束温度相等'
		elif xlsfile1_battery_row_data[7]<xlsfile2_battery_row_data[7]:
			out=xlsfile2_battery_row_data[7]-xlsfile1_battery_row_data[7]
			end_temp_cmp='【{0}】高{1}℃'.format(version2,out*0.1)
		else:
			out=xlsfile1_battery_row_data[7]-xlsfile2_battery_row_data[7]
			end_temp_cmp='【{0}】低{1}℃'.format(version2,out*0.1)


		#采样时间比较
		if xlsfile1_battery_row6_data[0]==xlsfile2_battery_row6_data[0]:
			time_cmp='采样时间相等'
		elif xlsfile1_battery_row6_data[0]<xlsfile2_battery_row6_data[0]:
			out=xlsfile2_battery_row6_data[0]-xlsfile1_battery_row6_data[0]
			time_cmp='【{0}】长{1}s'.format(version2,out)
		else:
			out=xlsfile1_battery_row6_data[0]-xlsfile2_battery_row6_data[0]
			time_cmp='【{0}】短{1}s'.format(version2,out)

		#总电量mAh值比较
		if xlsfile1_battery_row6_data[1]=='NA' and xlsfile2_battery_row6_data[1]=='NA':
			battery_total='NA'
			battery_per_total='NA'
			battery_use_percent='NA'

		elif xlsfile1_battery_row6_data[1]=='NA' and xlsfile2_battery_row6_data[1]!='NA':
			battery_total='{0}不支持获取电量值,{1}总电量毫安值为{2}mAh'.format(version1,version2,xlsfile2_battery_row6_data[1])
			battery_per_total='{0}不支持获取电量值,{1}电量消耗mAh值为{2}'.format(version1,version2,xlsfile2_battery_row6_data[3])
			battery_use_percent='{0}不支持获取电量值,{1}平均每秒消耗mAh值为{2}'.format(version1,version2,xlsfile2_battery_row6_data[4])

		elif xlsfile1_battery_row6_data[1]!='NA' and xlsfile2_battery_row6_data[1]=='NA':
			battery_total='{0}不支持获取电量值,{1}总电量毫安值为{2}'.format(version2,version1,xlsfile1_battery_row6_data[1])
			battery_per_total='{0}不支持获取电量值,{1}电量消耗mAh值为{2}'.format(version2,version1,xlsfile1_battery_row6_data[3])
			battery_use_percent='{0}不支持获取电量值,{1}平均每秒消耗mAh值为{2}'.format(version2,version1,xlsfile1_battery_row6_data[4])

		else:
			# battery_total='{0}总电量毫安值为{1},{2}总电量毫安值为{3}'.format(version1,xlsfile1_battery_row6_data[1],version2,xlsfile2_battery_row6_data[1])
			# battery_per_total='{0}电量消耗mAh值为{1},{2}电量消耗mAh值为{3}'.format(version1,xlsfile1_battery_row6_data[3],version2,xlsfile2_battery_row6_data[3])
			# battery_use_percent='{0}平均每秒消耗mAh值为{1},{2}平均每秒消耗mAh值为{3}'.format(version1,xlsfile1_battery_row6_data[4],version2,xlsfile2_battery_row6_data[4])
			if xlsfile1_battery_row6_data[1]==xlsfile2_battery_row6_data[1]:
				battery_total='总电量毫安值相等'
			elif xlsfile1_battery_row6_data[1]<xlsfile2_battery_row6_data[1]:
				battery_total='{0}总电量毫安值,大{1}'.format(version2,xlsfile2_battery_row6_data[1]-xlsfile1_battery_row6_data[1])
			else:
				battery_total='{0}总电量毫安值,小{1}'.format(version2,xlsfile1_battery_row6_data[1]-xlsfile2_battery_row6_data[1])

			if xlsfile1_battery_row6_data[3]==xlsfile2_battery_row6_data[3]:
				battery_per_total='电量消耗mAh值相等'
			elif xlsfile1_battery_row6_data[3]<xlsfile2_battery_row6_data[3]:
				battery_per_total='{0}电量消耗mAh值,大{1}'.format(version2,xlsfile2_battery_row6_data[3]-xlsfile1_battery_row6_data[3])
			else:
				battery_per_total='{0}电量消耗mAh值,小{1}'.format(version2,xlsfile1_battery_row6_data[3]-xlsfile2_battery_row6_data[3])

			if eval(xlsfile1_battery_row6_data[4])==eval(xlsfile2_battery_row6_data[4]):
				battery_use_percent='平均每秒消耗mAh值相等'
			elif eval(xlsfile1_battery_row6_data[4])<eval(xlsfile2_battery_row6_data[4]):
				battery_use_percent='{0}平均每秒消耗mAh值,大{1}'.format(version2,eval(xlsfile2_battery_row6_data[4])-eval(xlsfile1_battery_row6_data[4]))
			else:
				battery_use_percent='{0}平均每秒消耗mAh值,小{1}'.format(version2,eval(xlsfile1_battery_row6_data[4])-eval(xlsfile2_battery_row6_data[4]))


		#电量消耗百分比比较
		if xlsfile1_battery_row6_data[2]==xlsfile2_battery_row6_data[2]:
			battery_percent='电量消耗百分比相同'
		elif xlsfile1_battery_row6_data[2]<xlsfile2_battery_row6_data[2]:
			battery_percent='{0}大{1}%'.format(version2,xlsfile2_battery_row6_data[2]-xlsfile1_battery_row6_data[2])
		else:
			battery_percent='{0}小{1}%'.format(version1,xlsfile1_battery_row6_data[2]-xlsfile2_battery_row6_data[2])

		#CPU升温℃比较
		if xlsfile1_battery_row6_data[5]==xlsfile2_battery_row6_data[5]:
			cpu_up='CPU升温相同'
		elif xlsfile1_battery_row6_data[5]<xlsfile2_battery_row6_data[5]:
			cpu_up='{0}高{1}℃'.format(version2,xlsfile2_battery_row6_data[5]-xlsfile1_battery_row6_data[5])
		else:
			cpu_up='{0}低{1}℃'.format(version1,xlsfile1_battery_row6_data[5]-xlsfile2_battery_row6_data[5])

		#平均每秒升温℃比较
		if xlsfile1_battery_row6_data[6]==xlsfile2_battery_row6_data[6]:
			cpu_per_up='平均每秒升温℃相同'
		elif xlsfile1_battery_row6_data[6]<xlsfile2_battery_row6_data[6]:
			cpu_per_up='{0}高{1}℃'.format(version2,xlsfile2_battery_row6_data[6]-xlsfile1_battery_row6_data[6])
		else:
			cpu_per_up='{0}低{1}℃'.format(version1,xlsfile1_battery_row6_data[6]-xlsfile2_battery_row6_data[6])

		data_result_1=[['结论'],['【测试版本】 vs 【基线版本】'],[version_cmp],[times_cmp],[start_battery_cmp],[end_battery_cmp],
					 [start_vol_cmp],[end_vol_cmp],[start_temp_cmp],[end_temp_cmp]]

		data_result_2=[['结论'],['【测试版本】 vs 【基线版本】'],[time_cmp],[battery_total],[battery_percent],[battery_per_total],
					 [battery_use_percent],[cpu_up],[cpu_per_up],['NA']]

		worksheet.write_row('A1', headings_info_1_1, format_title)   #battery表1-1
		worksheet.write_column('A2', data_info_1_1[0],format_content)
		worksheet.write_column('B2', data_info_1_1[1],format_content)
		worksheet.write_column('C2', data_info_1_1[2],format_content)
		worksheet.write_column('D2', data_info_1_1[3],format_content)
		worksheet.write_column('E2', data_info_1_1[4],format_content)
		worksheet.write_column('F2', data_info_1_1[5],format_content)
		worksheet.write_column('G2', data_info_1_1[6],format_content)
		worksheet.write_column('H2', data_info_1_1[7],format_content)
		worksheet.write_column('I2', data_info_1_1[8],format_content)
		worksheet.write_column('J2', data_info_1_1[9],format_content)

		# worksheet.write_row('A3', headings_info_1_2, format_title)   #battery表1-2
		worksheet.write_column('A3', data_info_2_1[0],format_content)
		worksheet.write_column('B3', data_info_2_1[1],format_content)
		worksheet.write_column('C3', data_info_2_1[2],format_content)
		worksheet.write_column('D3', data_info_2_1[3],format_content)
		worksheet.write_column('E3', data_info_2_1[4],format_content)
		worksheet.write_column('F3', data_info_2_1[5],format_content)
		worksheet.write_column('G3', data_info_2_1[6],format_content)
		worksheet.write_column('H3', data_info_2_1[7],format_content)
		worksheet.write_column('I3', data_info_2_1[8],format_content)
		worksheet.write_column('J3', data_info_2_1[9],format_content)

		worksheet.write_row('A7', headings_info_1_2, format_title)   #battery表2-1
		worksheet.write_column('A8', data_info_1_2[0],format_content)
		worksheet.write_column('B8', data_info_1_2[1],format_content)
		worksheet.write_column('C8', data_info_1_2[2],format_content)
		worksheet.write_column('D8', data_info_1_2[3],format_content)
		worksheet.write_column('E8', data_info_1_2[4],format_content)
		worksheet.write_column('F8', data_info_1_2[5],format_content)
		worksheet.write_column('G8', data_info_1_2[6],format_content)
		worksheet.write_column('H8', data_info_1_2[7],format_content)
		worksheet.write_column('I8', data_info_1_2[8],format_content)
		worksheet.write_column('J8', data_info_1_2[9],format_content)


		# worksheet.write_row('A9', headings_info_2_2, format_title)   #battery表2-2
		worksheet.write_column('A9', data_info_2_2[0],format_content)
		worksheet.write_column('B9', data_info_2_2[1],format_content)
		worksheet.write_column('C9', data_info_2_2[2],format_content)
		worksheet.write_column('D9', data_info_2_2[3],format_content)
		worksheet.write_column('E9', data_info_2_2[4],format_content)
		worksheet.write_column('F9', data_info_2_2[5],format_content)
		worksheet.write_column('G9', data_info_2_2[6],format_content)
		worksheet.write_column('H9', data_info_2_2[7],format_content)
		worksheet.write_column('I9', data_info_2_2[8],format_content)
		worksheet.write_column('J9', data_info_2_2[9],format_content)
		#
		worksheet.write_row('A13', headings_result_1, format_result_title)   #battery汇总表1
		worksheet.write_column('A14', data_result_1[0],format_result)
		worksheet.write_column('B14', data_result_1[1],format_result)
		worksheet.write_column('C14', data_result_1[2],format_result)
		worksheet.write_column('D14', data_result_1[3],format_result)
		worksheet.write_column('E14', data_result_1[4],format_result)
		worksheet.write_column('F14', data_result_1[5],format_result)
		worksheet.write_column('G14', data_result_1[6],format_result)
		worksheet.write_column('H14', data_result_1[7],format_result)
		worksheet.write_column('I14', data_result_1[8],format_result)
		worksheet.write_column('J14', data_result_1[9],format_result)

		worksheet.write_row('A17', headings_result_2, format_result_title)   #battery汇总表2
		worksheet.write_column('A18', data_result_2[0],format_result)
		worksheet.write_column('B18', data_result_2[1],format_result)
		worksheet.write_column('C18', data_result_2[2],format_result)
		worksheet.write_column('D18', data_result_2[3],format_result)
		worksheet.write_column('E18', data_result_2[4],format_result)
		worksheet.write_column('F18', data_result_2[5],format_result)
		worksheet.write_column('G18', data_result_2[6],format_result)
		worksheet.write_column('H18', data_result_2[7],format_result)
		worksheet.write_column('I18', data_result_2[8],format_result)
		worksheet.write_column('J18', data_result_2[9],format_result)


	def merge_memory_report(self,xlsfile1,xlsfile2):
		worksheet = self.workbook.add_worksheet("memory")
		p1=ReadExcel()
		xlsfile1_memory_row2_data,xlsfile1_memory_row6_data,xlsfile1_memory_row10_data,xlsfile2_memory_row2_data,xlsfile2_memory_row6_data,xlsfile2_memory_row10_data=p1.readExcelMemory(xlsfile1,xlsfile2)
		print xlsfile1_memory_row2_data
		print xlsfile1_memory_row6_data
		print xlsfile1_memory_row10_data
		print xlsfile2_memory_row2_data
		print xlsfile2_memory_row6_data
		print xlsfile2_memory_row10_data

		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_content_red=self.workbook.add_format()

		format_result_title=self.workbook.add_format()

		format_result = self.workbook.add_format()
		format_result.set_text_wrap()   #自动换行
		format_result.set_align('center')  #水平居中
		format_result.set_align('vcenter')  #垂直居中


		worksheet.set_column('A:A',9)  #设置列宽
		worksheet.set_column('B:B', len(str(os.path.basename(xlsfile1)))+2)
		worksheet.set_column('C:C', len(str(xlsfile1_memory_row6_data[3]))+12)
		worksheet.set_column('D:M', len(str(xlsfile1_memory_row6_data[3]))+15)
		worksheet.set_column('G:G', len(str(xlsfile1_memory_row6_data[3]))+18)

		format_title.set_border(1)
		format_title.set_font_size(12)
		format_title.set_align('center')
		format_title.set_bg_color('#cccccc')
		format_title.set_font(u'微软雅黑')

		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)

		format_content_red.set_align('center')
		format_content_red.set_font(u'微软雅黑')
		format_content_red.set_font_size(11)
		format_content_red.set_font_color('#FF0000')

		#根据条件，如包括高、大则标红色
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '高',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '多',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '长',
                                      'format':   format_content_red})
		worksheet.conditional_format('A8:M8', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '大',
                                      'format':   format_content_red})

		format_result_title.set_bold()  #字体加粗
		format_result_title.set_border(1)
		format_result_title.set_font_size(12)
		format_result_title.set_align('center')
		format_result_title.set_bg_color('#cccccc')
		format_result_title.set_font(u'微软雅黑')

		format_result.set_align('center')
		format_result.set_font(u'微软雅黑')
		format_result.set_font_size(11)

		# # 这是个数据table的列
		headings_info_1 = ['报告序号','报表名称','APP版本号','系统版本','Dalvik_Heap(KB)',
						   'heapsize(KB)','Heapgrowthlimit(KB)','PSS_Total均值(KB)','PSS_Dalvik均值(KB)','PSS_Total最大(KB)','PSS_Total最小(KB)','PSS_Dalvik最大(KB)','PSS_Dalvik最小(KB)']

		# headings_info_2 = ['报告序号','报表名称','APP版本号','系统版本','Dalvik_Heap(KB)','heapsize(KB)','Heapgrowthlimit(KB)','PSS_Total最大(KB)','PSS_Total最小(KB)','PSS_Total均值(KB)','PSS_Dalvik最大(KB)','PSS_Dalvik最小(KB)','PSS_Dalvik均值(KB)']

		headings_result = ['报告汇总','比较方式','APP版本号【比较】','系统版本【比较】','Dalvik_Heap【比较】','heapsize【比较】','Heapgrowthlimit【比较】','PSS_Total均值【比较】','PSS_Dalvik均值【比较】','PSS_Total最大【比较】','PSS_Total最小【比较】','PSS_Dalvik最大【比较】','PSS_Dalvik最小【比较】']

		data_info_1=[['基线版本'],[os.path.basename(xlsfile1.decode('gbk'))],[xlsfile1_memory_row2_data[7]],[xlsfile1_memory_row2_data[2]],[xlsfile1_memory_row6_data[1]],
					 [xlsfile1_memory_row6_data[2]],[xlsfile1_memory_row6_data[3]],[xlsfile1_memory_row10_data[2]],
		[xlsfile1_memory_row10_data[5]],[xlsfile1_memory_row10_data[0]],[xlsfile1_memory_row10_data[1]],[xlsfile1_memory_row10_data[3]],[xlsfile1_memory_row10_data[4]]]

		data_info_2=[['测试版本'],[os.path.basename(xlsfile2.decode('gbk'))],[xlsfile2_memory_row2_data[7]],[xlsfile2_memory_row2_data[2]],[xlsfile2_memory_row6_data[1]],
					 [xlsfile2_memory_row6_data[2]],[xlsfile2_memory_row6_data[3]],[xlsfile2_memory_row10_data[2]],
		[xlsfile2_memory_row10_data[5]],[xlsfile2_memory_row10_data[0]],[xlsfile2_memory_row10_data[1]],[xlsfile2_memory_row10_data[3]],[xlsfile2_memory_row10_data[4]]]

		#版本号比较
		if eval(repr(data_info_2[2][0].encode('utf-8')))==eval(repr(data_info_1[2][0].encode('utf-8'))):
			version_cmp='版本号相等'
		elif eval(repr(data_info_1[2][0].encode('utf-8')))<eval(repr(data_info_2[2][0].encode('utf-8'))):
			version_cmp='版本号高'
		else:
			version_cmp='版本号低'

		if version_cmp=='版本号相等':
			version1='基线版本'
			version2='测试版本'
		else:
			version1='{}版本'.format(eval(repr(data_info_1[2][0].encode('utf-8'))))
			version2='{}版本'.format(eval(repr(data_info_2[2][0].encode('utf-8'))))

		#系统版本号比较
		if eval(repr(data_info_2[3][0].encode('utf-8')))==eval(repr(data_info_1[3][0].encode('utf-8'))):
			sys_version_cmp='系统版本号相等'
		elif eval(repr(data_info_1[3][0].encode('utf-8')))<eval(repr(data_info_2[3][0].encode('utf-8'))):
			sys_version_cmp='系统版本号高'
		else:
			sys_version_cmp='系统版本号低'


		#Dalvik_Heap【比较】
		if data_info_2[4][0]==data_info_1[4][0]:
			Dalvik_Heap_cmp='Dalvik_Heap消耗相等'
		elif data_info_1[4][0]<data_info_2[4][0]:
			Dalvik_Heap_cmp='{0}大{1}KB'.format(version2,data_info_2[4][0]-data_info_1[4][0])
		else:
			Dalvik_Heap_cmp='{0}小{1}KB'.format(version2,data_info_1[4][0]-data_info_2[4][0])

		#heapsize【比较】
		if data_info_2[5][0]==data_info_1[5][0]:
			heapsize_cmp='heapsize内存限制值相同'
		elif data_info_1[5][0]<data_info_2[5][0]:
			heapsize_cmp='{0}大{1}KB'.format(version2,data_info_2[5][0]-data_info_1[5][0])
		else:
			heapsize_cmp='{0}小{1}KB'.format(version2,data_info_1[5][0]-data_info_2[5][0])

		#Heapgrowthlimit【比较】
		if data_info_2[6][0]==data_info_1[6][0]:
			Heapgrowthlimit_cmp='Heapgrowthlimit内存限制值相同'
		elif data_info_1[6][0]<data_info_2[6][0]:
			Heapgrowthlimit_cmp='{0}大{1}KB'.format(version2,data_info_2[6][0]-data_info_1[6][0])
		else:
			Heapgrowthlimit_cmp='{0}小{1}KB'.format(version2,data_info_1[6][0]-data_info_2[6][0])

		#PSS_Total最大【比较】
		if data_info_2[9][0]==data_info_1[9][0]:
			PSS_Total_Max_cmp='PSS_Total最大值消耗相同'
		elif data_info_1[9][0]<data_info_2[9][0]:
			PSS_Total_Max_cmp='{0}大{1}KB'.format(version2,data_info_2[9][0]-data_info_1[9][0])
		else:
			PSS_Total_Max_cmp='{0}小{1}KB'.format(version2,data_info_1[9][0]-data_info_2[9][0])


		#PSS_Total最小【比较】
		if data_info_2[10][0]==data_info_1[10][0]:
			PSS_Total_Min_cmp='PSS_Total最小消耗相同'
		elif data_info_1[10][0]<data_info_2[10][0]:
			PSS_Total_Min_cmp='{0}大{1}KB'.format(version2,data_info_2[10][0]-data_info_1[10][0])
		else:
			PSS_Total_Min_cmp='{0}小{1}KB'.format(version2,data_info_1[10][0]-data_info_2[10][0])


		#PSS_Total均值【比较】
		if data_info_2[7][0]==data_info_1[7][0]:
			PSS_Total_avg_cmp='PSS_Total均值消耗相同'
		elif data_info_1[7][0]<data_info_2[7][0]:
			PSS_Total_avg_cmp='{0}大{1}KB'.format(version2,data_info_2[7][0]-data_info_1[7][0])
		else:
			PSS_Total_avg_cmp='{0}小{1}KB'.format(version2,data_info_1[7][0]-data_info_2[7][0])


		#PSS_Dalvik最大【比较】
		if data_info_2[11][0]==data_info_1[11][0]:
			PSS_Dalvik_Max_cmp='PSS_Dalvik最大值消耗相同'
		elif data_info_1[11][0]<data_info_2[11][0]:
			PSS_Dalvik_Max_cmp='{0}大{1}KB'.format(version2,data_info_2[11][0]-data_info_1[11][0])
		else:
			PSS_Dalvik_Max_cmp='{0}小{1}KB'.format(version2,data_info_1[11][0]-data_info_2[11][0])


		#PSS_Dalvik最小【比较】
		if data_info_2[12][0]==data_info_1[12][0]:
			PSS_Dalvik_Min_cmp='PSS_Dalvik最小值消耗相同'
		elif data_info_1[12][0]<data_info_2[12][0]:
			PSS_Dalvik_Min_cmp='{0}大{1}KB'.format(version2,data_info_2[12][0]-data_info_1[12][0])
		else:
			PSS_Dalvik_Min_cmp='{0}小{1}KB'.format(version2,data_info_1[12][0]-data_info_2[12][0])

		#PSS_Dalvik均值【比较】
		if data_info_2[8][0]==data_info_1[8][0]:
			PSS_Dalvik_avg_cmp='PSS_Dalvik均值消耗相同'
		elif data_info_1[8][0]<data_info_2[8][0]:
			PSS_Dalvik_avg_cmp='{0}大{1}KB'.format(version2,data_info_2[8][0]-data_info_1[8][0])
		else:
			PSS_Dalvik_avg_cmp='{0}小{1}KB'.format(version2,data_info_1[8][0]-data_info_2[8][0])




		data_result=[['结论'],['【测试版本】 vs 【基线版本】'],[version_cmp],[sys_version_cmp],[Dalvik_Heap_cmp],[heapsize_cmp],[Heapgrowthlimit_cmp],[PSS_Total_avg_cmp],[PSS_Dalvik_avg_cmp],[PSS_Total_Max_cmp],
					 [PSS_Total_Min_cmp],[PSS_Dalvik_Max_cmp],[PSS_Dalvik_Min_cmp]]


		worksheet.write_row('A1', headings_info_1, format_title)   #memory表1
		worksheet.write_column('A2', data_info_1[0],format_content)
		worksheet.write_column('B2', data_info_1[1],format_content)
		worksheet.write_column('C2', data_info_1[2],format_content)
		worksheet.write_column('D2', data_info_1[3],format_content)
		worksheet.write_column('E2', data_info_1[4],format_content)
		worksheet.write_column('F2', data_info_1[5],format_content)
		worksheet.write_column('G2', data_info_1[6],format_content)
		worksheet.write_column('H2', data_info_1[7],format_content)
		worksheet.write_column('I2', data_info_1[8],format_content)
		worksheet.write_column('J2', data_info_1[9],format_content)
		worksheet.write_column('K2', data_info_1[10],format_content)
		worksheet.write_column('L2', data_info_1[11],format_content)
		worksheet.write_column('M2', data_info_1[12],format_content)

		# worksheet.write_row('A3', headings_info_2, format_title)   #memory表2
		worksheet.write_column('A3', data_info_2[0],format_content)
		worksheet.write_column('B3', data_info_2[1],format_content)
		worksheet.write_column('C3', data_info_2[2],format_content)
		worksheet.write_column('D3', data_info_2[3],format_content)
		worksheet.write_column('E3', data_info_2[4],format_content)
		worksheet.write_column('F3', data_info_2[5],format_content)
		worksheet.write_column('G3', data_info_2[6],format_content)
		worksheet.write_column('H3', data_info_2[7],format_content)
		worksheet.write_column('I3', data_info_2[8],format_content)
		worksheet.write_column('J3', data_info_2[9],format_content)
		worksheet.write_column('K3', data_info_2[10],format_content)
		worksheet.write_column('L3', data_info_2[11],format_content)
		worksheet.write_column('M3', data_info_2[12],format_content)


		worksheet.write_row('A7', headings_result, format_result_title)   #memory汇总表1
		worksheet.write_column('A8', data_result[0],format_result)
		worksheet.write_column('B8', data_result[1],format_result)
		worksheet.write_column('C8', data_result[2],format_result)
		worksheet.write_column('D8', data_result[3],format_result)
		worksheet.write_column('E8', data_result[4],format_result)
		worksheet.write_column('F8', data_result[5],format_result)
		worksheet.write_column('G8', data_result[6],format_result)
		worksheet.write_column('H8', data_result[7],format_result)
		worksheet.write_column('I8', data_result[8],format_result)
		worksheet.write_column('J8', data_result[9],format_result)
		worksheet.write_column('K8', data_result[10],format_result)
		worksheet.write_column('L8', data_result[11],format_result)
		worksheet.write_column('M8', data_result[12],format_result)


class MegerResultReportFX(object):

	def __init__(self):
		global report_merge_name
		#Debug开关用于调试功能时用
		if Debug==False:
			report_merge_name='android_permance_merge_report.xlsx'
			self.workbook = xlsxwriter.Workbook(report_merge_name)
			self.report_path=os.path.abspath(os.getcwd())
		else:
			#获取创建报告时间
			creat_time=time.strftime("%Y_%m_%d_%H_%M_%S")
			#创建excel图表
			report_merge_name='android_permance_merge_report_{}.xlsx'.format(creat_time)
			self.workbook = xlsxwriter.Workbook(report_merge_name)
			self.report_path=os.path.abspath(os.getcwd())



	def __str__(self):
		print "开始生成图表分析合并报告"

	#将列表中空值删除掉
	def handler_list(self,list):
		while '' in list:
			list.remove('')
		return  list


	def merge_All_report_fx(self,xlsfile1,xlsfile2):
		worksheet = self.workbook.add_worksheet("性能测试报告")
		worksheet2 = self.workbook.add_worksheet("数据图表展示")
		p1=ReadExcelFX()

		#读取内存表数据
		self.memory_excel_1_row2_data,self.memory_excel_1_row6_data,self.memory_excel_1_row10_data,\
		self.memory_excel_2_row2_data,self.memory_excel_2_row6_data,self.memory_excel_2_row10_data,\
		self.memory_excel_1_col2_data,self.memory_excel_1_col3_data,self.memory_excel_2_col2_data,self.memory_excel_2_col3_data,self.memory_excel_1_col8_data,self.memory_excel_2_col8_data=\
			p1.readExcelMemory(xlsfile1,xlsfile2)

		base_PSS_Total_list=self.memory_excel_1_col2_data[1:]   #PSS_Total基线版本详细数据列表
		test_PSS_Total_list=self.memory_excel_2_col2_data[1:]

		base_PSS_Dalvik_list=self.memory_excel_1_col3_data[1:]   #PSS_Dalvik基线版本详细数据列表
		test_PSS_Dalvik_list=self.memory_excel_2_col3_data[1:]

		base_Dalvik_Heap_list=self.memory_excel_1_col8_data[1:]   #Dalvik_Heap基线版本详细数据列表
		test_Dalvik_Heap_list=self.memory_excel_2_col8_data[1:]

		#通过map函数将列表中内存各值由KB转换成MB

		base_PSS_Total_list=map(lambda x: float('%.2f'%(x/1024)), base_PSS_Total_list)
		test_PSS_Total_list=map(lambda x: float('%.2f'%(x/1024)), test_PSS_Total_list)
		base_PSS_Dalvik_list=map(lambda x: float('%.2f'%(x/1024)), base_PSS_Dalvik_list)
		test_PSS_Dalvik_list=map(lambda x: float('%.2f'%(x/1024)), test_PSS_Dalvik_list)
		base_Dalvik_Heap_list=map(lambda x: float('%.2f'%(x/1024)), base_Dalvik_Heap_list)
		test_Dalvik_Heap_list=map(lambda x: float('%.2f'%(x/1024)), test_Dalvik_Heap_list)
		print '*'*25+'memory内存数据打印'.encode(str_encode)+'*'*25+'\n'
		print self.memory_excel_1_row2_data,self.memory_excel_1_row6_data,self.memory_excel_1_row10_data,\
		self.memory_excel_2_row2_data,self.memory_excel_2_row6_data,self.memory_excel_2_row10_data


		#读取CPU内存表数据
		self.cpu_excel_1_row_data,self.cpu_excel_2_row_data,self.cpu_excel_1_col6_data,self.cpu_excel_2_col6_data,\
			self.cpu_excel_1_col8_data,self.cpu_excel_2_col8_data=p1.readExcelCPU(xlsfile1,xlsfile2)

		base_cpu_detail_list=self.cpu_excel_1_col6_data[5:]   #切片，获取CPU占用率详细列数据,基线版本CPU详细数据
		test_cpu_detail_list=self.cpu_excel_2_col6_data[5:]    #切片，测试版本CPU详细数据

		base_cpu_temperature_detail_list=self.cpu_excel_1_col8_data[5:]   #基线版本，CPU温度详细
		test_cpu_temperature_detail_list=self.cpu_excel_2_col8_data[5:]    #测试版本，CPU温度详细

		#去掉列表中空值
		base_cpu_detail_list=self.handler_list(base_cpu_detail_list)
		test_cpu_detail_list=self.handler_list(test_cpu_detail_list)
		base_cpu_temperature_detail_list=self.handler_list(base_cpu_temperature_detail_list)
		test_cpu_temperature_detail_list=self.handler_list(test_cpu_temperature_detail_list)

		print '\n'+'*'*25+'CPU数据打印'.encode(str_encode)+'*'*25+'\n'
		print self.cpu_excel_1_row_data,self.cpu_excel_2_row_data,self.cpu_excel_1_col6_data,self.cpu_excel_2_col6_data

		#读取FPS表数据
		self.fps_excel_1_row_data,self.fps_excel_2_row_data,self.fps_excel_1_col6_data,self.fps_excel_2_col6_data=p1.readExcelFPS(xlsfile1,xlsfile2)

		base_fps_detail_list=self.fps_excel_1_col6_data[5:]   #基线版本，fps每帧耗时详细数据
		test_fps_detail_list=self.fps_excel_2_col6_data[5:]   #测试版本，fps每帧耗时详细数据

		print '\n'+'*'*25+'FPS数据打印'.encode(str_encode)+'*'*25+'\n'
		print self.fps_excel_1_row_data,self.fps_excel_2_row_data


		#读取battery表数据
		self.battery_excel_1_row_data,self.battery_excel_1_row6_data,\
		self.battery_excel_2_row_data,self.battery_excel_2_row6_data,self.battery_excel_1_col3_data,self.battery_excel_2_col3_data=p1.readExcelBattery(xlsfile1,xlsfile2)
		print '\n'+'*'*25+'Battery数据打印'.encode(str_encode)+'*'*25+'\n'
		print self.battery_excel_1_row_data,self.battery_excel_1_row6_data,\
		self.battery_excel_2_row_data,self.battery_excel_2_row6_data

		base_battery_detail_list=self.battery_excel_1_col3_data[9:]   #基线版本电量消耗百分比
		test_battery_detail_list=self.battery_excel_2_col3_data[9:]   #测试版本电量消耗百分比

		#去掉列表空值
		base_battery_detail_list=self.handler_list(base_battery_detail_list)
		test_battery_detail_list=self.handler_list(test_battery_detail_list)

		#读取net表数据
		self.net_excel_1_row_data,self.net_excel_2_row_data,\
			self.net_excel_1_col2_data,self.net_excel_1_col3_data,self.net_excel_2_col2_data,self.net_excel_2_col3_data=p1.readExcelNET(xlsfile1,xlsfile2)

		base_net_revc_list=self.net_excel_1_col2_data[5:]
		test_net_revc_list=self.net_excel_2_col2_data[5:]

		base_net_send_list=self.net_excel_1_col3_data[5:]
		test_net_send_list=self.net_excel_2_col3_data[5:]

		#先通过函数删除掉列表中空值，再通过map函数将列表中NET各值，再由KB转换成MB


		base_net_revc_list=self.handler_list(base_net_revc_list)
		test_net_revc_list=self.handler_list(test_net_revc_list)
		base_net_send_list=self.handler_list(base_net_send_list)
		test_net_send_list=self.handler_list(test_net_send_list)

		base_net_revc_list=map(lambda x: float('%.2f'%(x/1024.0)), base_net_revc_list)
		test_net_revc_list=map(lambda x: float('%.2f'%(x/1024.0)), test_net_revc_list)
		base_net_send_list=map(lambda x: float('%.2f'%(x/1024.0)), base_net_send_list)
		test_net_send_list=map(lambda x: float('%.2f'%(x/1024.0)), test_net_send_list)


		print '\n'+'*'*25+'NET数据打印'.encode(str_encode)+'*'*25+'\n'
		print self.net_excel_1_row_data,self.net_excel_2_row_data


		#*********取采样次数，取内存、电量、流量、CPU列表最大长度为准*************
		test_PSS_Total_list_len=len(test_PSS_Total_list)
		test_cpu_detail_list_len=len(test_cpu_detail_list)
		test_battery_detail_list_len=len(test_battery_detail_list)
		test_net_revc_list_len=len(test_net_revc_list)

		#采样次数取最大列表长度值
		sampling_times=max(test_PSS_Total_list_len,test_cpu_detail_list_len,test_battery_detail_list_len,test_net_revc_list_len)
		sampling_times_list=[]

		#生成数据踩点列表
		for i in range(sampling_times):
			sampling_times_list.append('{}#'.format(i+1))

		#每帧耗时列表转换，转换一下，将获取到的帧数长度与采样次数长度保持一致

		base_fps_detail_list=base_fps_detail_list[:sampling_times]
		test_fps_detail_list=test_fps_detail_list[:sampling_times]

		#测试机型、基线版本、测试版本
		try:
			models=self.memory_excel_2_row2_data[0]  #手机名称
			models_version=self.memory_excel_2_row2_data[2]  #手机系统版本
			test_devices_models='设备机型:%s 【系统版本】:%s'%(models.strip(),models_version.strip())

			test_app_version=self.memory_excel_2_row2_data[7]   #测试版本app版本号
			base_app_version=self.memory_excel_1_row2_data[7]   #基线版本app版本号
		except Exception:
			pass

		#CPU
		try:
			base_cpu_avg=self.cpu_excel_1_row_data[6] #基线版本cpu(TOP)均值
			test_cpu_avg=self.cpu_excel_2_row_data[6]  #测试版本cpu(TOP)均值

			base_cpu_temperature_up=self.cpu_excel_1_row_data[7]   #CPU温度
			test_cpu_temperature_up=self.cpu_excel_2_row_data[7]

			base_cpu_frequency_avg=self.cpu_excel_1_row_data[8]   #CPU平均频率
			test_cpu_frequency_avg=self.cpu_excel_2_row_data[8]

			if test_cpu_avg>base_cpu_avg:
				result_cpu_avg='增涨{}%'.format(test_cpu_avg-base_cpu_avg)
			elif test_cpu_avg<base_cpu_avg:
				result_cpu_avg='下降{}%'.format(base_cpu_avg-test_cpu_avg)
			else:
				result_cpu_avg='相同'

			if test_cpu_temperature_up>base_cpu_temperature_up:
				result_cpu_temperature_up='增涨{}℃'.format(test_cpu_temperature_up-base_cpu_temperature_up)
			elif test_cpu_temperature_up<base_cpu_temperature_up:
				result_cpu_temperature_up='下降{}℃'.format(base_cpu_temperature_up-test_cpu_temperature_up)
			else:
				result_cpu_temperature_up='相同'

			if test_cpu_frequency_avg>base_cpu_frequency_avg:
				result_cpu_frequency_avg='增涨{}mHZ'.format(test_cpu_frequency_avg-base_cpu_frequency_avg)
			elif test_cpu_frequency_avg<base_cpu_frequency_avg:
				result_cpu_frequency_avg='下降{}mHZ'.format(base_cpu_frequency_avg-test_cpu_frequency_avg)
			else:
				result_cpu_frequency_avg='相同'

		except Exception:
			pass

		#内存
		try:
			base_PSS_Total_avg=self.memory_excel_1_row10_data[2]   #基线版本PSS_Total均值
			test_PSS_Total_avg=self.memory_excel_2_row10_data[2]

			base_PSS_Dalvik_avg=self.memory_excel_1_row10_data[5]  #基线版本PSS_Dalivk均值
			test_PSS_Dalvik_avg=self.memory_excel_2_row10_data[5]

			base_Dalvik_Heap=self.memory_excel_1_row6_data[1]      #基线版本Dalik Heap最大使用值
			test_Dalvik_Heap=self.memory_excel_2_row6_data[1]


			base_heapgrowthlimit=self.memory_excel_1_row6_data[3]
			test_heapgrowthlimit=self.memory_excel_2_row6_data[3]

			base_heapsize=self.memory_excel_1_row6_data[2]
			test_heapsize=self.memory_excel_2_row6_data[2]


			#由KB换算成MB,保留小数点三位
			base_PSS_Total_avg=float('%.2f'%(base_PSS_Total_avg/1024.0))
			test_PSS_Total_avg=float('%.2f'%(test_PSS_Total_avg/1024.0))
			base_PSS_Dalvik_avg=float('%.2f'%(base_PSS_Dalvik_avg/1024.0))
			test_PSS_Dalvik_avg=float('%.2f'%(test_PSS_Dalvik_avg/1024.0))
			base_Dalvik_Heap=float('%.2f'%(base_Dalvik_Heap/1024.0))
			test_Dalvik_Heap=float('%.2f'%(test_Dalvik_Heap/1024.0))

			base_heapgrowthlimit=float('%.2f'%(test_heapgrowthlimit/1024.0))
			test_heapgrowthlimit=float('%.2f'%(test_heapgrowthlimit/1024.0))

			base_heapsize=float('%.2f'%(base_heapsize/1024.0))
			test_heapsize=float('%.2f'%(test_heapsize/1024.0))

			base_Dalvik_Heap_text='{}/{}'.format(base_Dalvik_Heap,base_heapgrowthlimit)
			test_Dalvik_Heap_text='{}/{}'.format(test_Dalvik_Heap,test_heapgrowthlimit)


			if float(test_PSS_Total_avg)>float(base_PSS_Total_avg):
				result_PSS_Total_avg='增涨{}MB'.format(float(test_PSS_Total_avg)-float(base_PSS_Total_avg))
			elif float(test_PSS_Total_avg)<float(base_PSS_Total_avg):
				result_PSS_Total_avg='下降{}MB'.format(float(base_PSS_Total_avg)-float(test_PSS_Total_avg))
			else:
				result_PSS_Total_avg='相同'

			if float(test_PSS_Dalvik_avg)>float(base_PSS_Dalvik_avg):
				result_PSS_Dalvik_avg='增涨{}MB'.format(float(test_PSS_Dalvik_avg)-float(base_PSS_Dalvik_avg))
			elif float(test_PSS_Dalvik_avg)<float(base_PSS_Dalvik_avg):
				result_PSS_Dalvik_avg='下降{}MB'.format(float(base_PSS_Dalvik_avg)-float(test_PSS_Dalvik_avg))
			else:
				result_PSS_Dalvik_avg='相同'


			if float(test_Dalvik_Heap)>float(base_Dalvik_Heap):
				result_Dalvik_Heap='增涨{}MB'.format(float(test_Dalvik_Heap)-float(base_Dalvik_Heap))
			elif float(test_Dalvik_Heap)<float(base_PSS_Dalvik_avg):
				result_Dalvik_Heap='下降{}MB'.format(float(base_Dalvik_Heap)-float(test_Dalvik_Heap))
			else:
				result_Dalvik_Heap='相同'

		except Exception:
			pass


		#FPS
		try:
			base_fps_16_count=self.fps_excel_1_row_data[4]   #大于16.0帧数
			test_fps_16_count=self.fps_excel_2_row_data[4]

			base_fps_16_percent=self.fps_excel_1_row_data[5]
			test_fps_16_percent=self.fps_excel_2_row_data[5]
			base_fps_16_percent=float(base_fps_16_percent.strip('%'))
			test_fps_16_percent=float(test_fps_16_percent.strip('%'))

			base_fps_95_ms=self.fps_excel_1_row_data[6]
			test_fps_95_ms=self.fps_excel_2_row_data[6]

			if float(test_fps_16_count)>float(base_fps_16_count):
				result_fps_16_count='增涨{}帧'.format(float(test_fps_16_count)-float(base_fps_16_count))
			elif float(test_fps_16_count)<float(base_fps_16_count):
				result_fps_16_count='下降{}帧'.format(float(base_fps_16_count)-float(test_fps_16_count))
			else:
				result_fps_16_count='相同'

			if float(test_fps_16_percent)>float(base_fps_16_percent):
				result_fps_16_percent='增涨{}%'.format(float(test_fps_16_percent)-float(base_fps_16_percent))
			elif float(test_fps_16_percent)<float(base_fps_16_percent):
				result_fps_16_percent='下降{}%'.format(float(base_fps_16_percent)-float(test_fps_16_percent))
			else:
				result_fps_16_percent='相同'

			if float(test_fps_95_ms)>float(base_fps_95_ms):
				result_fps_95_ms='增涨{}ms'.format(float(test_fps_95_ms)-float(base_fps_95_ms))
			elif float(test_fps_95_ms)<float(base_fps_95_ms):
				result_fps_95_ms='下降{}ms'.format(float(base_fps_95_ms)-float(test_fps_95_ms))
			else:
				result_fps_95_ms='相同'
		except Exception:
			pass

		#Battery
		try:
			base_battery_consume_percent=self.battery_excel_1_row6_data[2]
			test_battery_consume_percent=self.battery_excel_2_row6_data[2]
			base_battery_consume_mAh=self.battery_excel_1_row6_data[3]
			test_battery_consume_mAh=self.battery_excel_2_row6_data[3]
			base_battery_consume_mAh_per=self.battery_excel_1_row6_data[4]
			test_battery_consume_mAh_per=self.battery_excel_2_row6_data[4]

			if self.battery_excel_1_row6_data[4]!='NA' or self.battery_excel_2_row6_data[4]!='NA':
				base_battery_consume_mAh_per=float(self.battery_excel_1_row6_data[4])
				test_battery_consume_mAh_per=float(self.battery_excel_2_row6_data[4])

			base_battery_temperature_up=self.battery_excel_1_row6_data[5]
			test_battery_temperature_up=self.battery_excel_2_row6_data[5]

			base_battery_temperature_up_per=float(self.battery_excel_1_row6_data[6])
			test_battery_temperature_up_per=float(self.battery_excel_2_row6_data[6])


			if float(test_battery_temperature_up)>float(base_battery_temperature_up):
				result_battery_temperature_up='增涨{}℃'.format((float(test_battery_temperature_up)-float(base_battery_temperature_up))/10)
			elif float(test_battery_temperature_up)<float(base_battery_temperature_up):
				result_battery_temperature_up='下降{}℃'.format((float(base_battery_temperature_up)-float(test_battery_temperature_up))/10)
			else:
				result_battery_temperature_up='相同'

			if float(test_battery_temperature_up_per)>float(base_battery_temperature_up_per):
				result_battery_temperature_up_per='增涨{}℃'.format((float(test_battery_temperature_up_per)-float(base_battery_temperature_up_per))/10)
			elif float(test_battery_temperature_up_per)<float(base_battery_temperature_up_per):
				result_battery_temperature_up_per='下降{}℃'.format((float(base_battery_temperature_up_per)-float(test_battery_temperature_up_per))/10)
			else:
				result_battery_temperature_up_per='相同'

			if float(test_battery_consume_percent)>float(base_battery_consume_percent):
				result_battery_consume_percent='增涨{}%'.format(float(test_battery_consume_percent)-float(base_battery_consume_percent))
			elif float(test_battery_consume_percent)<float(base_battery_consume_percent):
				result_battery_consume_percent='下降{}%'.format(float(base_battery_consume_percent)-float(test_battery_consume_percent))
			else:
				result_battery_consume_percent='相同'

			if test_battery_consume_mAh!='NA' and base_battery_consume_mAh!='NA':
				if float(test_battery_consume_mAh)>float(base_battery_consume_mAh):
					result_battery_consume_mAh='增涨{}mAh'.format(float(test_battery_consume_mAh)-float(base_battery_consume_mAh))
				elif float(test_battery_consume_mAh)<float(base_battery_consume_mAh):
					result_battery_consume_mAh='下降{}mAh'.format(float(base_battery_consume_mAh)-float(test_battery_consume_mAh))
				else:
					result_battery_consume_mAh='相同'
			else:
				result_battery_consume_mAh='NA'

			if test_battery_consume_mAh_per!='NA' and base_battery_consume_mAh_per!='NA':
				if float(test_battery_consume_mAh_per)>float(base_battery_consume_mAh_per):
					result_battery_consume_mAh_per='增涨{}mAh'.format(float(test_battery_consume_mAh_per)-float(base_battery_consume_mAh_per))
				elif float(test_battery_consume_mAh_per)<float(base_battery_consume_mAh_per):
					result_battery_consume_mAh_per='下降{}mAh'.format(float(base_battery_consume_mAh_per)-float(test_battery_consume_mAh_per))
				else:
					result_battery_consume_mAh_per='相同'
			else:
				result_battery_consume_mAh_per='NA'

		except Exception as e:
			print e

		#NET
		try:
			base_net_revc=self.net_excel_1_row_data[6]
			test_net_revc=self.net_excel_2_row_data[6]
			base_net_send=self.net_excel_1_row_data[7]
			test_net_send=self.net_excel_2_row_data[7]

			#由KB转换为MB
			base_net_revc=float('%.1f'%float(base_net_revc/1024.0))
			test_net_revc=float('%.1f'%float(test_net_revc/1024.0))
			base_net_send=float('%.1f'%float(base_net_send/1024.0))
			test_net_send=float('%.1f'%float(test_net_send/1024.0))

			if float(test_net_revc)>float(base_net_revc):
				result_net_revc='增涨{}MB'.format(float(test_net_revc)-float(base_net_revc))
			elif float(test_net_revc)<float(base_net_revc):
				result_net_revc='下降{}MB'.format(float(base_net_revc)-float(test_net_revc))
			else:
				result_net_revc='相同'

			if float(test_net_send)>float(base_net_send):
				result_net_send='增涨{}MB'.format(float(test_net_send)-float(base_net_send))
			elif float(test_net_send)<float(base_net_send):
				result_net_send='下降{}MB'.format(float(base_net_send)-float(test_net_send))
			else:
				result_net_send='相同'
		except Exception:
			pass

		##********************样式区***************************************
		#创建图表样式
		format_title=self.workbook.add_format()    #设置title和content样式
		format_head=self.workbook.add_format()    #设置title和content样式
		format_content=self.workbook.add_format()
		format_title_noBold=self.workbook.add_format()   #未加边框
		format_title_LightSkyBlue=self.workbook.add_format()   #数据踩点列标题样式
		format_title_Orange=self.workbook.add_format()         #基线版本列标题样式
		format_title_LightYellow=self.workbook.add_format()    #测试版本列标题样式
		format_title_bold_yellow=self.workbook.add_format()   #浅绿色
		format_content_red=self.workbook.add_format()
		format_result = self.workbook.add_format()

		format_title_LightSkyBlue_data=self.workbook.add_format()   #数据踩点列数据详细样式
		format_title_Orange_data=self.workbook.add_format()         #基线版本列数据详细样式
		format_title_LightYellow_data=self.workbook.add_format()    #测试版本列数据详细样式

		format_result.set_text_wrap()   #自动换行
		format_result.set_align('center')  #水平居中
		format_result.set_align('vcenter')  #垂直居中


		worksheet.set_column('A:A',12)  #设置列宽
		worksheet.set_column('B:E',len('CPU占用率%（Top）')-1)  #设置列宽
		worksheet.set_column('F:S',len('CPU占用率%（Top）')-8)  #设置列宽


		#根据条件，如包括增涨、大则标红色
		worksheet.conditional_format('A14:Q14', {'type':     'text',
                                       'criteria': 'containing',
                                       'value':    '增涨',
                                      'format':   format_content_red})

		##***********设置行高***********
		for i in xrange(7):
			worksheet.set_row(i,18)   #设置第1行到第8行，行高为18像素

		worksheet.set_row(8,90)   #设置第9行，行高为90像素

		worksheet.set_row(11,36)   #设置第12行，行高为36像素
		worksheet.set_row(12,36)   #设置第13行，行高为36像素
		worksheet.set_row(13,36)   #设置第14行，行高为36像素

		worksheet.set_row(14,18)   #设置第15行，行高为18像素
		worksheet.set_row(15,18)   #设置第16行，行高为18像素

		format_head.set_align('center')
		format_head.set_font(u'微软雅黑')
		format_head.set_font_size(14)
		format_head.set_text_wrap()   #自动换行
		format_head.set_align('center')  #水平居中
		format_head.set_align('vcenter')  #垂直居中
		format_head.set_border(1)   #加边框
		format_head.set_bold(True)  #加粗
		format_head.set_bg_color('#DCDCDC')

		format_title.set_align('center')
		format_title.set_font(u'微软雅黑')
		format_title.set_font_size(12)
		format_title.set_text_wrap()   #自动换行
		format_title.set_align('center')  #水平居中
		format_title.set_align('vcenter')  #垂直居中
		format_title.set_border(1)   #加边框
		format_title.set_bold(True)  #加粗
		format_title.set_bg_color('#C0C0C0')


		format_title_noBold.set_align('center')
		format_title_noBold.set_font(u'微软雅黑')
		format_title_noBold.set_font_size(12)
		format_title_noBold.set_text_wrap()   #自动换行
		format_title_noBold.set_align('center')  #水平居中
		format_title_noBold.set_align('vcenter')  #垂直居中
		format_title_noBold.set_border(1)   #加边框
		format_title_noBold.set_bg_color('#C0C0C0')


		format_title_LightSkyBlue.set_align('center')
		format_title_LightSkyBlue.set_font(u'微软雅黑')
		format_title_LightSkyBlue.set_font_size(11)
		format_title_LightSkyBlue.set_text_wrap()   #自动换行
		format_title_LightSkyBlue.set_align('center')  #水平居中
		format_title_LightSkyBlue.set_align('vcenter')  #垂直居中
		format_title_LightSkyBlue.set_border(1)   #加边框
		format_title_LightSkyBlue.set_bg_color('#D8BFD8')   #蓟


		format_title_LightSkyBlue_data.set_align('center')
		format_title_LightSkyBlue_data.set_font(u'微软雅黑')
		format_title_LightSkyBlue_data.set_font_size(10)
		format_title_LightSkyBlue_data.set_text_wrap()   #自动换行
		format_title_LightSkyBlue_data.set_align('center')  #水平居中
		format_title_LightSkyBlue_data.set_align('vcenter')  #垂直居中
		format_title_LightSkyBlue_data.set_border(1)   #加边框
		format_title_LightSkyBlue_data.set_bg_color('#D8BFD8')   #蓟

		format_title_Orange.set_align('center')
		format_title_Orange.set_font(u'微软雅黑')
		format_title_Orange.set_font_size(11)
		format_title_Orange.set_text_wrap()   #自动换行
		format_title_Orange.set_align('center')  #水平居中
		format_title_Orange.set_align('vcenter')  #垂直居中
		format_title_Orange.set_border(1)   #加边框
		format_title_Orange.set_bg_color('#B0C4DE')   #淡钢蓝

		format_title_Orange_data.set_align('center')
		format_title_Orange_data.set_font(u'微软雅黑')
		format_title_Orange_data.set_font_size(10)
		format_title_Orange_data.set_text_wrap()   #自动换行
		format_title_Orange_data.set_align('center')  #水平居中
		format_title_Orange_data.set_align('vcenter')  #垂直居中
		format_title_Orange_data.set_border(1)   #加边框
		format_title_Orange_data.set_bg_color('#B0C4DE')   #淡钢蓝

		format_title_LightYellow.set_align('center')
		format_title_LightYellow.set_font(u'微软雅黑')
		format_title_LightYellow.set_font_size(11)
		format_title_LightYellow.set_text_wrap()   #自动换行
		format_title_LightYellow.set_align('center')  #水平居中
		format_title_LightYellow.set_align('vcenter')  #垂直居中
		format_title_LightYellow.set_border(1)   #加边框
		format_title_LightYellow.set_bg_color('#FDF5E6')   #老饰带


		format_title_LightYellow_data.set_align('center')
		format_title_LightYellow_data.set_font(u'微软雅黑')
		format_title_LightYellow_data.set_font_size(10)
		format_title_LightYellow_data.set_text_wrap()   #自动换行
		format_title_LightYellow_data.set_align('center')  #水平居中
		format_title_LightYellow_data.set_align('vcenter')  #垂直居中
		format_title_LightYellow_data.set_border(1)   #加边框
		format_title_LightYellow_data.set_bg_color('#FDF5E6')   #老饰带

		format_title_bold_yellow.set_align('center')
		format_title_bold_yellow.set_font(u'微软雅黑')
		format_title_bold_yellow.set_font_size(11)
		format_title_bold_yellow.set_text_wrap()   #自动换行
		format_title_bold_yellow.set_align('center')  #水平居中
		format_title_bold_yellow.set_align('vcenter')  #垂直居中
		format_title_bold_yellow.set_border(1)   #加边框
		format_title_bold_yellow.set_bg_color('#EBF1DE')   #浅绿色


		format_content.set_align('center')
		format_content.set_font(u'微软雅黑')
		format_content.set_font_size(11)
		format_content.set_text_wrap()   #自动换行
		format_content.set_align('center')  #水平居中
		format_content.set_align('vcenter')  #垂直居中

		format_content_red.set_align('center')
		format_content_red.set_font(u'微软雅黑')
		format_content_red.set_font_size(11)
		format_content_red.set_text_wrap()   #自动换行
		format_content_red.set_align('center')  #水平居中
		format_content_red.set_align('vcenter')  #垂直居中
		format_content_red.set_font_color('#FF0000')  #红色



		##*******************基本情况区****************************

		worksheet.merge_range('A1:S1',u'基本情况区',format_head)
		worksheet.write('A2','测试机型',format_title)
		worksheet.merge_range('B2:G2',test_devices_models,format_content)
		worksheet.merge_range('H2:L2',u'测试环境\网络',format_title)
		worksheet.merge_range('M2:S2',u'',format_content)

		worksheet.write('A3','基线版本',format_title)
		worksheet.merge_range('B3:G3',base_app_version,format_content)
		worksheet.merge_range('H3:L3',u'测试人员',format_title)
		worksheet.merge_range('M3:S3',u'',format_content)

		worksheet.write('A4','测试版本',format_title)
		worksheet.merge_range('B4:G4',test_app_version,format_content)
		worksheet.merge_range('H4:L4',u'测试时间',format_title)
		worksheet.merge_range('M4:S4',u'',format_content)

		worksheet.merge_range('A5:A8',u'测试前置',format_title)
		worksheet.merge_range('B5:S8',u'',format_title_bold_yellow)
		worksheet.write('A9',u'测试步骤',format_title)
		worksheet.merge_range('B9:S9',u'',format_title_bold_yellow)


		##*******************测试对比区***********************
		worksheet.merge_range('A10:S10',u'测试对比区',format_head)
		comment_text='当Dalvik_Heap最大值大于【heapgrowthlimit - 单个应用程序最大内存限制】或【heapsize：{}MB - 单个java虚拟机最大的内存限制】则可能存在内存溢出!'.format(test_heapsize)
		worksheet.write_comment('E11',comment_text)

		data_result_title=['数据对比','CPU使用均值%（Top）','PSS_Total均值(MB)','PSS_Dalvik均值(MB)','Dalvik_Heap最大值/HeapGrowthLimit(MB)','大于16.0的帧数','大于16.0的帧数占比(%)','95%的帧耗时(ms)','电量消耗百分比%','电量消耗mAh值','平均每秒消耗mAh值'
		             ,'CPU升温℃','CPU平均频率mHZ','电池升温℃','平均每秒电池升温℃','流量发送消耗(MB)','流量接收消耗(MB)']

		base_data_list=[base_cpu_avg,base_PSS_Total_avg,base_PSS_Dalvik_avg,base_Dalvik_Heap_text,base_fps_16_count,base_fps_16_percent,base_fps_95_ms,
		                base_battery_consume_percent,base_battery_consume_mAh,base_battery_consume_mAh_per,base_cpu_temperature_up,base_cpu_frequency_avg,base_battery_temperature_up/10,
		                base_battery_temperature_up_per/10,base_net_revc,base_net_send]

		test_data_list=[test_cpu_avg,test_PSS_Total_avg,test_PSS_Dalvik_avg,test_Dalvik_Heap_text,test_fps_16_count,test_fps_16_percent,test_fps_95_ms,
		                test_battery_consume_percent,test_battery_consume_mAh,test_battery_consume_mAh_per,test_cpu_temperature_up,test_cpu_frequency_avg,
		                test_battery_temperature_up/10,test_battery_temperature_up_per/10,test_net_revc,test_net_send]

		result_data_list=[result_cpu_avg,result_PSS_Total_avg,result_PSS_Dalvik_avg,result_Dalvik_Heap,result_fps_16_count,result_fps_16_percent,result_fps_95_ms,
		                  result_battery_consume_percent,result_battery_consume_mAh,result_battery_consume_mAh_per,result_cpu_temperature_up,result_cpu_frequency_avg,
		                  result_battery_temperature_up,result_battery_temperature_up_per,result_net_revc,result_net_send]


		worksheet.write_row('A11',data_result_title,format_title_noBold)
		worksheet.write('A11','数据对比',format_title)
		worksheet.write('A12', '基线版本', format_title)
		worksheet.write('A13', '测试版本', format_title)
		worksheet.write('A14', '对比结果', format_title)

		worksheet.write_row('B12',base_data_list,format_content)
		worksheet.write_row('B13',test_data_list,format_content)
		worksheet.write_row('B14',result_data_list,format_content)

		worksheet.merge_range('H11:I11','95%的帧耗时(ms)',format_title_noBold)
		worksheet.write_comment('H11:I11','计算方法：将所有每帧耗时按升序排序，从列表中取95%对应位置，帧耗时所花费的时间')
		worksheet.merge_range('H12:I12',base_fps_95_ms,format_content)
		worksheet.merge_range('H13:I13',test_fps_95_ms,format_content)
		worksheet.merge_range('H14:I14',result_fps_95_ms,format_content)

		##**********************数据详细区****************
		worksheet.merge_range('A15:S15',u'数据详细区',format_head)

		data_detail_title1=['数据踩点','测试版本【CPU】','基线版本【CPU】','测试版本【GPU流畅度】','基线版本【GPU流畅度】']
		data_detail_title2=['','CPU占用率%(Top)','CPU占用率%(Top)','每帧耗时(ms)','每帧耗时(ms)','Dalvik_Heap值','PSS_Total值','PSS_Dalvik值','Dalvik_Heap值','PSS_Total值','PSS_Dalvik值','TCP接收字节数KB',
		                    "TCP发送字节数KB",'TCP接收字节数KB','TCP发送字节数KB','电量实时百分比','CPU温度℃','电量实时百分比','CPU温度℃']


		worksheet.write_row('A16',data_detail_title1,format_title_noBold)
		worksheet.write_row('A17',data_detail_title2,format_title_noBold)

		worksheet.merge_range('F16:H16',u'测试版本【内存】',format_title_LightYellow)
		worksheet.merge_range('I16:K16',u'基线版本【内存】',format_title_Orange)

		worksheet.merge_range('L16:M16',u'测试版本【流量】',format_title_LightYellow)
		worksheet.merge_range('N16:O16',u'基线版本【流量】',format_title_Orange)

		worksheet.merge_range('P16:Q16',u'测试版本【耗电量、温度】',format_title_LightYellow)
		worksheet.merge_range('R16:S16',u'基线版本【耗电量、温度】',format_title_Orange)

		worksheet.write('A16','数据踩点',format_title_LightSkyBlue)
		worksheet.write('A17','',format_title_LightSkyBlue)

		worksheet.write('B16','测试版本【CPU】',format_title_LightYellow)
		worksheet.write('B17','CPU占用率%(Top)',format_title_LightYellow)
		worksheet.write('C16','基线版本【CPU】',format_title_Orange)
		worksheet.write('C17','CPU占用率%(Top)',format_title_Orange)

		worksheet.write('D16','测试版本【GPU流畅度】',format_title_LightYellow)
		worksheet.write('D17','每帧耗时(ms)',format_title_LightYellow)
		worksheet.write('E16','基线版本【GPU流畅度】',format_title_Orange)
		worksheet.write('E17','每帧耗时(ms)',format_title_Orange)

		worksheet.write('F17','Dalvik_Heap值(MB)',format_title_LightYellow)
		worksheet.write('G17','PSS_Total值(MB)',format_title_LightYellow)
		worksheet.write('H17','PSS_Dalvik值(MB)',format_title_LightYellow)

		worksheet.write('I17','Dalvik_Heap值(MB)',format_title_Orange)
		worksheet.write('J17','PSS_Total值(MB)',format_title_Orange)
		worksheet.write('K17','PSS_Dalvik值(MB)',format_title_Orange)

		worksheet.write('L17','TCP接收字节数(MB)',format_title_LightYellow)
		worksheet.write('M17','TCP发送字节数(MB)',format_title_LightYellow)
		worksheet.write('N17','TCP接收字节数(MB)',format_title_Orange)
		worksheet.write('O17','TCP发送字节数(MB)',format_title_Orange)

		worksheet.write('P17','电量实时百分比%',format_title_LightYellow)
		worksheet.write('Q17','CPU实时温度℃',format_title_LightYellow)
		worksheet.write('R17','电量实时百分比%',format_title_Orange)
		worksheet.write('S17','CPU实时温度℃',format_title_Orange)

		#显示详细数据

		#数据踩点详细
		worksheet.write_column('A18',sampling_times_list,format_title_LightSkyBlue_data)


		##CPU详细列表
		worksheet.write_column('B18',test_cpu_detail_list,format_title_LightYellow_data)
		worksheet.write_column('C18',base_cpu_detail_list,format_title_Orange_data)

		##FPS详细列表
		worksheet.write_column('D18',test_fps_detail_list,format_title_LightYellow_data)
		worksheet.write_column('E18',base_fps_detail_list,format_title_Orange_data)

		##Memory内存详细列表
		worksheet.write_column('F18',test_Dalvik_Heap_list,format_title_LightYellow_data)
		worksheet.write_column('G18',test_PSS_Total_list,format_title_LightYellow_data)
		worksheet.write_column('H18',test_PSS_Dalvik_list,format_title_LightYellow_data)
		worksheet.write_column('I18',base_Dalvik_Heap_list,format_title_Orange_data)
		worksheet.write_column('J18',base_PSS_Total_list,format_title_Orange_data)
		worksheet.write_column('K18',base_PSS_Dalvik_list,format_title_Orange_data)

		##NET流量详细列表
		worksheet.write_column('L18',test_net_revc_list,format_title_LightYellow_data)
		worksheet.write_column('M18',test_net_send_list,format_title_LightYellow_data)
		worksheet.write_column('N18',base_net_revc_list,format_title_Orange_data)
		worksheet.write_column('O18',base_net_send_list,format_title_Orange_data)

		##Battery电量详细列表
		worksheet.write_column('P18',test_battery_detail_list,format_title_LightYellow_data)
		worksheet.write_column('Q18',test_cpu_temperature_detail_list
		                       ,format_title_LightYellow_data)
		worksheet.write_column('R18',base_battery_detail_list,format_title_Orange_data)
		worksheet.write_column('S18',base_cpu_temperature_detail_list,format_title_Orange_data)



		##***************图表展示sheet****************

		###########CPU图表绘制#####################

		worksheet2.set_row(0,36)
		worksheet2.merge_range('A1:AA1','CPU指标图表展示',format_head)

		#创建一个柱形样式和线条样式图表，类型是column、line
		chart_cpu = self.workbook.add_chart({'type': 'line'})  #CPU使用率
		chart_cpu_temperature = self.workbook.add_chart({'type': 'line'})  #CPU温度

		# 配置series,这个和前面wordsheet是有关系的。
		cpu_row_num=len(test_cpu_detail_list)
		cpu_temperature_row_num=len(test_cpu_temperature_detail_list)
		#******************CPU占用率%(Top)与CPU温度_柱形图表*****************

		chart_cpu.set_drop_lines()
		chart_cpu.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart_cpu_temperature.set_drop_lines()
		chart_cpu_temperature.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})
		#cpu占用率
		chart_cpu.add_series({
		    'name':       '=性能测试报告!$B$16',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(cpu_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$B$18:$B${}'.format(cpu_row_num+18),  #图表数据范围
		})

		chart_cpu.add_series({
		    'name':       '=性能测试报告!$C$16',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(cpu_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$C$18:$C${}'.format(cpu_row_num+18),  #图表数据范围
		})

		#cpu温度
		chart_cpu_temperature.add_series({
		    'name':       '测试版本【CPU温度】',   #显示名称,直接赋值字符串
		    'categories': '=性能测试报告!$A$18:$A${}'.format(cpu_temperature_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$Q$18:$Q${}'.format(cpu_temperature_row_num+18),  #图表数据范围
		})

		chart_cpu_temperature.add_series({
		    'name':       '基线版本【CPU温度】',   #显示名称，直接赋值字符串
		    'categories': '=性能测试报告!$A$18:$A${}'.format(cpu_temperature_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$S$18:$S${}'.format(cpu_temperature_row_num+18),  #图表数据范围
		})
		chart_cpu.set_title ({'name': 'CPU占用率%(Top)_线形图'})
		chart_cpu.set_x_axis({'name': '采样次数'})
		chart_cpu.set_y_axis({'name': 'CPU占用率(MB)'})
		chart_cpu.set_size({'width': 820, 'height': 300})

		chart_cpu_temperature.set_title ({'name': 'CPU实时温度℃_线形图'})
		chart_cpu_temperature.set_x_axis({'name': '采样次数'})
		chart_cpu_temperature.set_y_axis({'name': 'CPU温度℃'})
		chart_cpu_temperature.set_size({'width': 800, 'height': 300})

		worksheet2.insert_chart('A2', chart_cpu, {'x_offset': 15, 'y_offset': 10})
		worksheet2.insert_chart('N2', chart_cpu_temperature, {'x_offset': 15, 'y_offset': 10})

		worksheet2.merge_range('A2:AA19','')   #合并

		###########FPS图表绘制#####################

		worksheet2.set_row(19,36)
		worksheet2.merge_range('A20:AA20','GPU指标图表展示',format_head)

		#创建一个柱形样式和线条样式图表，类型是column、line
		chart_fps = self.workbook.add_chart({'type': 'line'})  #每帧耗时


		# 配置series,这个和前面wordsheet是有关系的。
		fps_row_num=len(test_fps_detail_list)

		#******************fps每帧耗时_柱形图表*****************

		# chart_fps.set_drop_lines()
		# chart_fps.set_drop_lines({'line': {'color': 'red',
         #                       'dash_type': 'square_dot'}})

		#fps每帧耗时
		chart_fps.add_series({
		    'name':       '测试版本【每帧耗时ms】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(fps_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$D$18:$D${}'.format(fps_row_num+18),  #图表数据范围
		})

		chart_fps.add_series({
		    'name':       '基线版本【每帧耗时ms】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(fps_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$E$18:$E${}'.format(fps_row_num+18),  #图表数据范围
		})


		chart_fps.set_title ({'name': 'FPS每帧耗时ms_线形图'})
		chart_fps.set_x_axis({'name': '采样次数'})
		chart_fps.set_y_axis({'name': '耗时ms'})
		chart_fps.set_size({'width': 1600, 'height': 300})

		worksheet2.insert_chart('A21', chart_fps, {'x_offset': 25, 'y_offset': 10})

		worksheet2.merge_range('A21:AA38','')   #合并

		###########内存Memory图表绘制#####################

		worksheet2.set_row(38,38)
		worksheet2.merge_range('A39:AA39','内存指标图表展示',format_head)

		#创建一个柱形样式和线条样式图表，类型是column、line
		chart_memory_Dalvik_Heap = self.workbook.add_chart({'type': 'line'})  #Dalvik_Heap
		chart_memory_PSS_Total = self.workbook.add_chart({'type': 'line'})  #PSS_Total
		chart_memory_PSS_Dalvik = self.workbook.add_chart({'type': 'line'})  #PSS_Dalvik

		# 配置series,这个和前面wordsheet是有关系的。
		Dalvik_Heap_row_num=len(test_Dalvik_Heap_list)
		PSS_Total_row_num=len(test_PSS_Total_list)
		PSS_Dalvik_row_num=len(test_PSS_Dalvik_list)

		#******************内存各指标_柱形图表*****************

		chart_memory_Dalvik_Heap.set_drop_lines()
		chart_memory_Dalvik_Heap.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart_memory_PSS_Total.set_drop_lines()
		chart_memory_PSS_Total.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		chart_memory_PSS_Dalvik.set_drop_lines()
		chart_memory_PSS_Dalvik.set_drop_lines({'line': {'color': 'red',
                               'dash_type': 'square_dot'}})

		#Dalvik_Heap
		chart_memory_Dalvik_Heap.add_series({
		    'name':       '测试版本【Dalvik_Heap】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(Dalvik_Heap_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$F$18:$F${}'.format(Dalvik_Heap_row_num+18),  #图表数据范围
		})

		chart_memory_Dalvik_Heap.add_series({
		    'name':       '基线版本【Dalvik_Heap】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(Dalvik_Heap_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$I$18:$I${}'.format(Dalvik_Heap_row_num+18),  #图表数据范围
		})

		#PSS_Total
		chart_memory_PSS_Total.add_series({
		    'name':       '测试版本【PSS_Total】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(PSS_Total_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$G$18:$G${}'.format(PSS_Total_row_num+18),  #图表数据范围
		})

		chart_memory_PSS_Total.add_series({
		    'name':       '基线版本【PSS_Total】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(PSS_Total_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$J$18:$J${}'.format(PSS_Total_row_num+18),  #图表数据范围
		})

		#PSS_Dalvik
		chart_memory_PSS_Dalvik.add_series({
		    'name':       '测试版本【PSS_Dalvik】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(PSS_Dalvik_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$H$18:$H${}'.format(PSS_Dalvik_row_num+18),  #图表数据范围
		})

		chart_memory_PSS_Dalvik.add_series({
		    'name':       '基线版本【PSS_Dalvik】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(PSS_Dalvik_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$K$18:$K${}'.format(PSS_Dalvik_row_num+18),  #图表数据范围
		})



		chart_memory_Dalvik_Heap.set_title ({'name': '内存【Dalvik_Heap】_线形图'})
		chart_memory_Dalvik_Heap.set_x_axis({'name': '采样次数'})
		chart_memory_Dalvik_Heap.set_y_axis({'name': 'Dalvik_Heap值(MB)'})
		chart_memory_Dalvik_Heap.set_size({'width': 820, 'height': 300})

		chart_memory_PSS_Total.set_title ({'name': '内存【PSS_Total】_线形图'})
		chart_memory_PSS_Total.set_x_axis({'name': '采样次数'})
		chart_memory_PSS_Total.set_y_axis({'name': 'PSS_Total值(MB)'})
		chart_memory_PSS_Total.set_size({'width': 800, 'height': 300})

		chart_memory_PSS_Dalvik.set_title ({'name': '内存【PSS_Dalvik】_线形图'})
		chart_memory_PSS_Dalvik.set_x_axis({'name': '采样次数'})
		chart_memory_PSS_Dalvik.set_y_axis({'name': 'PSS_Dalvik值(MB)'})
		chart_memory_PSS_Dalvik.set_size({'width': 820, 'height': 300})


		worksheet2.insert_chart('A40', chart_memory_Dalvik_Heap, {'x_offset': 15, 'y_offset': 10})
		worksheet2.insert_chart('N40', chart_memory_PSS_Total, {'x_offset': 15, 'y_offset': 10})
		worksheet2.insert_chart('A56', chart_memory_PSS_Dalvik, {'x_offset': 15, 'y_offset': 10})

		worksheet2.merge_range('A40:AA72','')

		###########流量NET图表绘制#####################

		worksheet2.set_row(72,36)
		worksheet2.merge_range('A73:AA73','流量NET指标图表展示',format_head)

		#创建一个柱形样式和线条样式图表，类型是column、line
		chart_net_revc = self.workbook.add_chart({'type': 'line'})  #流量接收
		chart_net_send = self.workbook.add_chart({'type': 'line'})  #流量发送

		# 配置series,这个和前面wordsheet是有关系的。
		net_recv_row_num=len(test_net_revc_list)
		net_send_row_num=len(test_net_send_list)

		#******************流量_柱形图表*****************

		# chart_net_revc.set_drop_lines()
		# chart_net_revc.set_drop_lines({'line': {'color': 'red',
         #                       'dash_type': 'square_dot'}})
		#
		# chart_net_send.set_drop_lines()
		# chart_net_send.set_drop_lines({'line': {'color': 'red',
         #                       'dash_type': 'square_dot'}})

		#流量接收
		chart_net_revc.add_series({
		    'name':       '测试版本【接收字节数MB】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(net_recv_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$L$18:$L${}'.format(net_recv_row_num+18),  #图表数据范围
		})

		chart_net_revc.add_series({
		    'name':       '基线版本【接收字节数MB】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(net_recv_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$N$18:$N${}'.format(net_recv_row_num+18),  #图表数据范围
		})

		#流量发送
		chart_net_send.add_series({
		    'name':       '测试版本【发送字节数MB】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(net_send_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$M$18:$M${}'.format(net_send_row_num+18),  #图表数据范围
		})

		chart_net_send.add_series({
		    'name':       '基线版本【发送字节数MB】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(net_send_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$O$18:$O${}'.format(net_send_row_num+18),  #图表数据范围
		})

		chart_net_revc.set_title ({'name': '流量接收字节数MB_线形图'})
		chart_net_revc.set_x_axis({'name': '采样次数'})
		chart_net_revc.set_y_axis({'name': '单位MB'})
		chart_net_revc.set_size({'width': 820, 'height': 300})

		chart_net_send.set_title ({'name': '流量发送字节数MB_线形图'})
		chart_net_send.set_x_axis({'name': '采样次数'})
		chart_net_send.set_y_axis({'name': '单位MB'})
		chart_net_send.set_size({'width': 800, 'height': 300})

		worksheet2.insert_chart('A74', chart_net_revc, {'x_offset': 15, 'y_offset': 10})
		worksheet2.insert_chart('N74', chart_net_send, {'x_offset': 15, 'y_offset': 10})

		worksheet2.merge_range('A74:AA90','')   #合并

		###########电量图表绘制#####################

		worksheet2.set_row(90,36)
		worksheet2.merge_range('A91:AA91','耗电量图表展示',format_head)

		#创建一个柱形样式和线条样式图表，类型是column、line
		chart_battery = self.workbook.add_chart({'type': 'line'})  #每帧耗时


		# 配置series,这个和前面wordsheet是有关系的。
		battery_row_num=len(test_battery_detail_list)

		#******************电量百分比_柱形图表*****************

		# chart_battery.set_drop_lines()
		# chart_battery.set_drop_lines({'line': {'color': 'red',
         #                       'dash_type': 'square_dot'}})

		#耗电量百分比消耗
		chart_battery.add_series({
		    'name':       '测试版本【电量实时百分比】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(battery_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$P$18:$P${}'.format(battery_row_num+18),  #图表数据范围
		})

		chart_battery.add_series({
		    'name':       '基线版本【电量实时百分比】',   #显示名称
		    'categories': '=性能测试报告!$A$18:$A${}'.format(battery_row_num+18),  #x坐标范围
		    'values':     '=性能测试报告!$R$18:$R${}'.format(battery_row_num+18),  #图表数据范围
		})


		chart_battery.set_title ({'name': '电量实时百分比_线形图'})
		chart_battery.set_x_axis({'name': '采样次数'})
		chart_battery.set_y_axis({'name': '电量百分比'})
		chart_battery.set_size({'width': 840, 'height': 300})

		worksheet2.insert_chart('A92', chart_battery, {'x_offset': 15, 'y_offset': 10})
		worksheet2.merge_range('A92:AA108','')

		worksheet.write_comment('Q17',"CPU实时温度为0时，则说明当前设备获取CPU温度提示Permission denied，故赋默认值0")
		worksheet.write_comment('S17',"CPU实时温度为0时，则说明当前设备获取CPU温度提示Permission denied，故赋默认值0")

class ReadExcel():
	def __init__(self):
		if system is "Windows":
			print "开始读取报表数据...".encode('gbk')
		else:
			print "开始读取报表数据..."

	def readExcelFPS(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_fps=excel_1.sheet_by_name('fps')
		excel_1_nrows = excel_1_fps.nrows    #行总数
		excel_1_ncols = excel_1_fps.ncols   #列总数
		self.excel_1_row_data = excel_1_fps.row_values(1)  #第二行
		self.excel_1_col_data = excel_1_fps.col_values(0)  #第一列

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_fps=excel_2.sheet_by_name('fps')
		excel_2_nrows = excel_2_fps.nrows    #行总数
		excel_2_ncols = excel_2_fps.ncols   #列总数
		self.excel_2_row_data = excel_2_fps.row_values(1)  #第二行
		self.excel_2_col_data = excel_2_fps.col_values(0)  #第一列

		return self.excel_1_row_data,self.excel_2_row_data

	def readExcelCPU(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_cpu=excel_1.sheet_by_name('cpu')

		self.excel_1_row_data = excel_1_cpu.row_values(1)  #第二行

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_cpu=excel_2.sheet_by_name('cpu')

		self.excel_2_row_data = excel_2_cpu.row_values(1)  #第二行

		return self.excel_1_row_data,self.excel_2_row_data


	def readExcelNET(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_net=excel_1.sheet_by_name('net')

		self.excel_1_row_data = excel_1_net.row_values(1)  #第二行

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_net=excel_2.sheet_by_name('net')

		self.excel_2_row_data = excel_2_net.row_values(1)  #第二行

		return self.excel_1_row_data,self.excel_2_row_data

	def readExcelBattery(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_battery=excel_1.sheet_by_name('battery')

		self.excel_1_row_data = excel_1_battery.row_values(1)  #第二行
		self.excel_1_row6_data = excel_1_battery.row_values(5)  #第六行

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_battery=excel_2.sheet_by_name('battery')

		self.excel_2_row_data = excel_2_battery.row_values(1)  #第二行
		self.excel_2_row6_data = excel_2_battery.row_values(5)  #第六行

		return self.excel_1_row_data,self.excel_1_row6_data,self.excel_2_row_data,self.excel_2_row6_data

	def readExcelMemory(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_battery=excel_1.sheet_by_name('memory')

		self.excel_1_row2_data = excel_1_battery.row_values(1)  #第二行
		self.excel_1_row6_data = excel_1_battery.row_values(5)  #第六行
		self.excel_1_row10_data = excel_1_battery.row_values(9)  #第十行

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_battery=excel_2.sheet_by_name('memory')

		self.excel_2_row2_data = excel_2_battery.row_values(1)  #第二行
		self.excel_2_row6_data = excel_2_battery.row_values(5)  #第六行
		self.excel_2_row10_data = excel_2_battery.row_values(9)  #第十行

		return self.excel_1_row2_data,self.excel_1_row6_data,self.excel_1_row10_data,self.excel_2_row2_data,self.excel_2_row6_data,self.excel_2_row10_data

	#获取excel文件中所有sheet名称
	def get_sheet_names(self,xlsfilename):
		if os.path.exists(os.path.join(os.getcwd(),xlsfilename)):
			sheet_names_list=[]
			book = xlrd.open_workbook(xlsfilename)
			for i in xrange(len(book.sheet_names())):
				sheet_name=book.sheet_names()[i]
				sheet_names_list.append(sheet_name)
			return sheet_names_list


class ReadExcelFX():
	def __init__(self):
		if system is "Windows":
			print "开始读取报表数据...".encode('gbk')
		else:
			print "开始读取报表数据..."

	def readExcelFPS(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_fps=excel_1.sheet_by_name('fps')
		excel_1_nrows = excel_1_fps.nrows    #行总数
		excel_1_ncols = excel_1_fps.ncols   #列总数
		self.excel_1_row_data = excel_1_fps.row_values(1)  #第二行
		self.excel_1_col6_data = excel_1_fps.col_values(5)  #第六列

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_fps=excel_2.sheet_by_name('fps')
		excel_2_nrows = excel_2_fps.nrows    #行总数
		excel_2_ncols = excel_2_fps.ncols   #列总数
		self.excel_2_row_data = excel_2_fps.row_values(1)  #第二行
		self.excel_2_col6_data = excel_2_fps.col_values(5)  #第六列

		return self.excel_1_row_data,self.excel_2_row_data,self.excel_1_col6_data,self.excel_2_col6_data

	def readExcelCPU(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_cpu=excel_1.sheet_by_name('cpu')

		self.excel_1_row_data = excel_1_cpu.row_values(1)  #第二行
		self.excel_1_col6_data = excel_1_cpu.col_values(5)  #第六列
		self.excel_1_col8_data = excel_1_cpu.col_values(7)  #第八列

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_cpu=excel_2.sheet_by_name('cpu')

		self.excel_2_row_data = excel_2_cpu.row_values(1)  #第二行
		self.excel_2_col6_data = excel_2_cpu.col_values(5)  #第六列
		self.excel_2_col8_data = excel_2_cpu.col_values(7)  #第八列

		return self.excel_1_row_data,self.excel_2_row_data,self.excel_1_col6_data,self.excel_2_col6_data,self.excel_1_col8_data,self.excel_2_col8_data


	def readExcelNET(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_net=excel_1.sheet_by_name('net')

		self.excel_1_row_data = excel_1_net.row_values(1)  #第二行

		self.excel_1_col2_data = excel_1_net.col_values(1)  #第二列
		self.excel_1_col3_data = excel_1_net.col_values(2)  #第三列

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_net=excel_2.sheet_by_name('net')

		self.excel_2_row_data = excel_2_net.row_values(1)  #第二行
		self.excel_2_col2_data = excel_2_net.col_values(1)  #第二列
		self.excel_2_col3_data = excel_2_net.col_values(2)  #第三列

		return self.excel_1_row_data,self.excel_2_row_data,self.excel_1_col2_data,self.excel_1_col3_data,self.excel_2_col2_data,self.excel_2_col3_data

	def readExcelBattery(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_battery=excel_1.sheet_by_name('battery')

		self.excel_1_row_data = excel_1_battery.row_values(1)  #第二行
		self.excel_1_row6_data = excel_1_battery.row_values(5)  #第六行
		self.excel_1_col3_data= excel_1_battery.col_values(2)   #第三列

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_battery=excel_2.sheet_by_name('battery')

		self.excel_2_row_data = excel_2_battery.row_values(1)  #第二行
		self.excel_2_row6_data = excel_2_battery.row_values(5)  #第六行
		self.excel_2_col3_data= excel_2_battery.col_values(2)   #第三列

		return self.excel_1_row_data,self.excel_1_row6_data,self.excel_2_row_data,self.excel_2_row6_data,self.excel_1_col3_data,self.excel_2_col3_data

	def readExcelMemory(self,xlsfile1,xlsfile2):

		#读取第一张excel表
		excel_1 = xlrd.open_workbook(xlsfile1)
		excel_1_memory=excel_1.sheet_by_name('memory')
		excel_1_memory_details=excel_1.sheet_by_name('memory_details')

		self.excel_1_row2_data = excel_1_memory.row_values(1)  #第二行
		self.excel_1_row6_data = excel_1_memory.row_values(5)  #第六行
		self.excel_1_row10_data = excel_1_memory.row_values(9)  #第十行

		self.excel_1_col2_data=excel_1_memory_details.col_values(1) #第二列
		self.excel_1_col3_data=excel_1_memory_details.col_values(2) #第三列
		self.excel_1_col8_data=excel_1_memory_details.col_values(7) #第八列

		#读取第二张excel表
		excel_2 = xlrd.open_workbook(xlsfile2)
		excel_2_memory=excel_2.sheet_by_name('memory')
		excel_2_memory_details=excel_2.sheet_by_name('memory_details')

		self.excel_2_row2_data = excel_2_memory.row_values(1)  #第二行
		self.excel_2_row6_data = excel_2_memory.row_values(5)  #第六行
		self.excel_2_row10_data = excel_2_memory.row_values(9)  #第十行

		self.excel_2_col2_data=excel_2_memory_details.col_values(1) #第二列
		self.excel_2_col3_data=excel_2_memory_details.col_values(2) #第三列
		self.excel_2_col8_data=excel_2_memory_details.col_values(7) #第八列

		return self.excel_1_row2_data,self.excel_1_row6_data,self.excel_1_row10_data,self.excel_2_row2_data,self.excel_2_row6_data,self.excel_2_row10_data,\
		       self.excel_1_col2_data,self.excel_1_col3_data,self.excel_2_col2_data,self.excel_2_col3_data,self.excel_1_col8_data,self.excel_2_col8_data

	#获取excel文件中所有sheet名称
	def get_sheet_names(self,xlsfilename):
		if os.path.exists(os.path.join(os.getcwd(),xlsfilename)):
			sheet_names_list=[]
			book = xlrd.open_workbook(xlsfilename)
			for i in xrange(len(book.sheet_names())):
				sheet_name=book.sheet_names()[i]
				sheet_names_list.append(sheet_name)
			return sheet_names_list


#主类
class android_permance_tool():

	def main(self,device_name,packapgename,flag,delay_time,max_time,report_name):
		try:
			if system is "Windows":
				copyAWK()

			#关闭、打开飞行模式，用于清空网络之前统计的流量数据
			# if system is "Windows":
			# 	print '\n'+"*"*20+'打开、关闭飞行模式，用于清空网络之前统计的流量数据'.encode('gbk')+'*'*20
			# 	window.printRed('打开飞行模式后，如果APP界面网络异常，请在程序自动关闭飞行模式后手动恢复!\n'.encode('gbk'))
			#
			# 	# turn_airplane_mode(device_name,1)  #打开
			# 	# turn_airplane_mode(device_name,0)  #关闭
			# else:
			# 	print "*"*20+'关闭、打开飞行模式，用于清空网络之前统计的流量数据'+'*'*20+'\n'
				# turn_airplane_mode(device_name,1)
				# turn_airplane_mode(device_name,0)

			# if system is "Windows":
			# 	raw_input("\n请先手动点击App屏幕重试，再按任意键开始继续性能数据采集...\n".encode('gbk'))
			# else:
			# 	raw_input("\n请先手动点击App屏幕重试，再按任意键开始继续性能数据采集...\n")

			if system is "Windows":
				print "*"*20+'开始进行android性能数据采集'.encode('gbk')+'*'*20+'\n'

			else:
				print "*"*20+'开始进行android性能数据采集'+'*'*20+'\n'

			p=ResultReport(report_name)

			#设置计时线程
			timeit_thread=threading.Thread(target=timer,args=(max_time,))
			timeit_thread.setDaemon(True)
			timeit_thread.start()
			timeit_thread.join(3)   #执行此线程后，等待3秒，再往后执行

			threads=[]
			if flag=='All':

				#************顺序执行采集*************
				# p.gen_memory_report(device_name,packapgename,times)
				# p.gen_cpu_report(device_name,packapgename,times)
				# p.gen_net_report(device_name,packapgename,times)
				# p.gen_fps_report(device_name,packapgename,times)

				#**********采用多线程来采集执行*********
				gen_memory_thread=threading.Thread(target=p.gen_memory_report,args=(device_name,packapgename,delay_time))
				gen_net_thread=threading.Thread(target=p.gen_net_report,args=(device_name,packapgename,delay_time))
				gen_cpu_thread=threading.Thread(target=p.gen_cpu_report,args=(device_name,packapgename,delay_time))
				gen_fps_thread=threading.Thread(target=p.gen_fps_report,args=(device_name,packapgename,delay_time))
				gen_battery_thread=threading.Thread(target=p.gen_battery_report,args=(device_name,packapgename,delay_time))


				gen_memory_thread.setDaemon(True)
				gen_net_thread.setDaemon(True)
				gen_cpu_thread.setDaemon(True)
				gen_fps_thread.setDaemon(True)
				gen_battery_thread.setDaemon(True)


				gen_memory_thread.start()
				gen_cpu_thread.start()
				gen_battery_thread.start()
				gen_fps_thread.start()
				gen_net_thread.start()

				#将所有线程增加到线程列表中

				threads.append(gen_memory_thread)
				threads.append(gen_fps_thread)
				threads.append(gen_battery_thread)
				threads.append(gen_net_thread)
				threads.append(gen_cpu_thread)

				# gen_memory_thread.join()
				# gen_net_thread.join()
				# gen_cpu_thread.join()
				# gen_fps_thread.join()
				# gen_battery_thread.join()

				while 1:
					alive = False
					for i in range(len(threads)):
						alive = alive or threads[i].isAlive()
					if not alive:
							break

			elif flag=='memory':
				# p.gen_memory_report(device_name,packapgename,delay_time)
				gen_memory_thread=threading.Thread(target=p.gen_memory_report,args=(device_name,packapgename,delay_time))
				gen_memory_thread.setDaemon(True)
				gen_memory_thread.start()
				# gen_memory_thread.join()

				threads.append(gen_memory_thread)
				while 1:
					alive = False
					for i in range(len(threads)):
						alive = alive or threads[i].isAlive()
					if not alive:
							break

			elif flag=='cpu':
				# p.gen_cpu_report(device_name,packapgename,delay_time)
				gen_cpu_thread=threading.Thread(target=p.gen_cpu_report,args=(device_name,packapgename,delay_time))
				gen_cpu_thread.setDaemon(True)
				gen_cpu_thread.start()
				# gen_cpu_thread.join()

				threads.append(gen_cpu_thread)
				while 1:
					alive = False
					for i in range(len(threads)):
						alive = alive or threads[i].isAlive()
					if not alive:
							break

			elif flag=='net':
				# p.gen_net_report(device_name,packapgename,delay_time)
				gen_net_thread=threading.Thread(target=p.gen_net_report,args=(device_name,packapgename,delay_time))
				gen_net_thread.setDaemon(True)
				gen_net_thread.start()
				# gen_net_thread.join()

				threads.append(gen_net_thread)
				while 1:
					alive = False
					for i in range(len(threads)):
						alive = alive or threads[i].isAlive()
					if not alive:
							break

			elif flag=='fps':
				# p.gen_fps_report(device_name,packapgename,delay_time)
				gen_fps_thread=threading.Thread(target=p.gen_fps_report,args=(device_name,packapgename,delay_time))
				gen_fps_thread.setDaemon(True)
				gen_fps_thread.start()
				# gen_fps_thread.join()

				threads.append(gen_fps_thread)
				while 1:
					alive = False
					for i in range(len(threads)):
						alive = alive or threads[i].isAlive()
					if not alive:
							break

			elif flag=='battery':
				# p.gen_battery_report(device_name,packapgename,delay_time)
				gen_battery_thread=threading.Thread(target=p.gen_battery_report,args=(device_name,packapgename,delay_time))
				gen_battery_thread.setDaemon(True)
				gen_battery_thread.start()
				# gen_battery_thread.join()

				threads.append(gen_battery_thread)
				while 1:
					alive = False
					for i in range(len(threads)):
						alive = alive or threads[i].isAlive()
					if not alive:
							break

		except Exception,e:
			# traceback.print_exc()   #捕获错误信息
			pass
		finally:
			p.workbook.close()
			# if system is "Windows":
			# 	print "结果报告输出目录:".encode('gbk'),p.report_path
			# else:
			# 	print "结果报告输出目录:",p.report_path



	#版本对比，帧率合并函数
	def mergeFPS(self,xlsfile1,xlsfile2):
		if system is "Windows":
			print "*"*20+'开始进行fps帧率性能报告分析，汇总'.encode('gbk')+'*'*20+'\n'
		else:
			print "*"*20+'开始进行fps帧率性能报告分析，汇总'+'*'*20+'\n'
		p1=MegerResultReport()
		try:
			p1.merge_fps_report(xlsfile1,xlsfile2)
		except Exception:
			traceback.print_exc()
		else:
			if system is "Windows":
				print "test3"
				print '\n'+'*'*20+"fps帧率报告分析比较，合并完成!".encode('gbk')+'*'*20
				print '分析合并生成的报告名称为:{}'.encode('gbk').format(report_merge_name)
			else:
				print '\n'+'*'*20+"fps帧率报告分析比较，合并完成!"+'*'*20
				print '分析合并生成的报告名称为:{}'.format(report_merge_name)
		finally:
			p1.workbook.close()

	#版本对比，CPU合并函数
	def mergeCPU(self,xlsfile1,xlsfile2):
		if system is "Windows":
			print "*"*20+'开始进行cpu性能报告分析，汇总'.encode('gbk')+'*'*20+'\n'
		else:
			print "*"*20+'开始进行cpu性能报告分析，汇总'+'*'*20+'\n'
		p1=MegerResultReport()
		try:
			p1.merge_cpu_report(xlsfile1,xlsfile2)
		except Exception:
			traceback.print_exc()
		else:
			if system is "Windows":
				print '\n'+'*'*20+"cpu报告分析比较，合并完成!".encode('gbk')+'*'*20
				print '分析合并生成的报告名称为:{}'.encode('gbk').format(report_merge_name)
			else:
				print '\n'+'*'*20+"cpu报告分析比较，合并完成!"+'*'*20
				print '分析合并生成的报告名称为:{}'.format(report_merge_name)
		finally:
			p1.workbook.close()


	#版本对比，CPU合并函数
	def mergeNET(self,xlsfile1,xlsfile2):
		if system is "Windows":
			print "*"*20+'开始进行net性能报告分析，汇总'.encode('gbk')+'*'*20+'\n'
		else:
			print "*"*20+'开始进行net性能报告分析，汇总'+'*'*20+'\n'
		p1=MegerResultReport()
		try:
			p1.merge_net_report(xlsfile1,xlsfile2)
		except Exception:
			traceback.print_exc()
		else:
			if system is "Windows":
				print '\n'+'*'*20+"net报告分析比较，合并完成!".encode('gbk')+'*'*20
				print '分析合并生成的报告名称为:{}'.encode('gbk').format(report_merge_name)
			else:
				print '\n'+'*'*20+"net报告分析比较，合并完成!"+'*'*20
				print '分析合并生成的报告名称为:{}'.format(report_merge_name)
		finally:
			p1.workbook.close()

	#版本对比，电量、温度、电压合并函数
	def mergeBattery(self,xlsfile1,xlsfile2):
		if system is "Windows":
			print "*"*20+'开始进行电量、电压、温度性能报告分析，汇总'.encode('gbk')+'*'*20+'\n'
		else:
			print "*"*20+'开始进行电量、电压、温度帧率性能报告分析，汇总'+'*'*20+'\n'
		p1=MegerResultReport()
		try:
			p1.merge_battery_report(xlsfile1,xlsfile2)
		except Exception:
			traceback.print_exc()
		else:
			if system is "Windows":
				print '\n'+'*'*20+"电量、电压、温度报告分析，合并完成!".encode('gbk')+'*'*20
				print '分析合并生成的报告名称为:{}'.encode('gbk').format(report_merge_name)
			else:
				print '\n'+'*'*20+"电量、电压、温度报告分析，合并完成!"+'*'*20
				print '分析合并生成的报告名称为:{}'.format(report_merge_name)
		finally:
			p1.workbook.close()

	#版本对比，内存合并函数
	def mergeMemory(self,xlsfile1,xlsfile2):
		if system is "Windows":
			print "*"*20+'开始进行内存性能报告分析，汇总'.encode('gbk')+'*'*20+'\n'
		else:
			print "*"*20+'开始进行内存性能报告分析，汇总'+'*'*20+'\n'
		p1=MegerResultReport()
		try:
			p1.merge_memory_report(xlsfile1,xlsfile2)
		except Exception:
			traceback.print_exc()
		else:
			if system is "Windows":
				print '\n'+'*'*20+"内存报告分析比较，合并完成!".encode('gbk')+'*'*20
				print '分析合并生成的报告名称为:{}'.encode('gbk').format(report_merge_name)
			else:
				print '\n'+'*'*20+"内存报告分析比较，合并完成!"+'*'*20
				print '分析合并生成的报告名称为:{}'.format(report_merge_name)
		finally:
			p1.workbook.close()


	#版本对比，全部性能指标合并函数
	def mergeAll(self,xlsfile1,xlsfile2):
		if system is "Windows":
			print "*"*20+'开始进行全部指标性能报告分析，汇总'.encode('gbk')+'*'*20+'\n'
		else:
			print "*"*20+'开始进行全部指标性能报告分析，汇总'+'*'*20+'\n'
		p1=MegerResultReport()
		try:
			p1.merge_memory_report(xlsfile1,xlsfile2)
			p1.merge_fps_report(xlsfile1,xlsfile2)
			p1.merge_cpu_report(xlsfile1,xlsfile2)
			p1.merge_net_report(xlsfile1,xlsfile2)
			p1.merge_battery_report(xlsfile1,xlsfile2)

		except Exception:
			traceback.print_exc()
		else:
			if system is "Windows":
				print '\n'+'*'*20+"全部报告分析比较，合并完成!".encode('gbk')+'*'*20
				print '分析合并生成的报告名称为:{}'.encode('gbk').format(report_merge_name)
			else:
				print '\n'+'*'*20+"全部报告分析比较，合并完成!"+'*'*20
				print '分析合并生成的报告名称为:{}'.format(report_merge_name)
		finally:
			p1.workbook.close()



	#版本对比，全部指标合并汇总，手机繁星报告定制化生成
	def mergeAllFX(self,xlsfile1,xlsfile2):
		if system is "Windows":
			print "*"*20+'开始进行全部指标性能报告分析，汇总'.encode('gbk')+'*'*20+'\n'
		else:
			print "*"*20+'开始进行全部指标性能报告分析，汇总'+'*'*20+'\n'
		p1=MegerResultReportFX()
		try:
			p1.merge_All_report_fx(xlsfile1,xlsfile2)

		except Exception:
			traceback.print_exc()
		else:
			if system is "Windows":
				print '\n'+'*'*20+"全部报告分析比较，合并完成!".encode('gbk')+'*'*20
				print '分析合并生成的繁星定制化性能报告名称为:{}'.encode('gbk').format(report_merge_name)
			else:
				print '\n'+'*'*20+"全部报告分析比较，合并完成!"+'*'*20
				print '分析合并生成的繁星定制化性能报告名称为:{}'.format(report_merge_name)
		finally:
			p1.workbook.close()

#复制gawk命令到系统根目录下
def copyAWK():
	if os.path.exists(os.path.join(os.getcwd(),'gawk.exe')):
		if not os.path.exists(os.path.join("c:\\","Windows\\System32\\gawk.exe")):
			print "复制文件到c:\windows\system32目录下".encode('gbk')
			shutil.copyfile(os.path.join(os.getcwd(),'gawk.exe'),os.path.join("c:\\","Windows\\System32\\gawk.exe"))
			print "复制完成!".encode('gbk')
		else:
			print 'gawk.exe已存在c:\windows\system32目录下'.encode('gbk')
	else:
		print "gawk.exe源文件不存在脚本根目录下".encode('gbk')



is_exit = False
def quit(signum,frame):
	if system is 'Windows':
		window.printRed('好黄好暴力!!! 你已强制中止程序，停止采集!\n'.encode('gbk'))
	else:
		print styles.RED+'好黄好暴力!!! 你已强制中止程序，停止采集!\n'+styles.ENDC
	# os.popen('taskkill /f /pid {}'.format(os.getpid()))
	os.kill(os.getpid(),signal.SIGTERM)
	sys.exit()



#每3秒检查一次设备状态
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
						window.printRed('亲，当前测试设备【{}】状态不在线，状态为：{}，请检查!\n'.encode('gbk').format(device_name,serino[1::2][index]))
						window.printWhite('')
						os.popen('taskkill /f /pid {}'.format(os.getpid()))
						sys.exit()
					else:
						window.printRed('亲，当前测试设备【{}】状态不在线,状态为:{}，请检查!\n'.encode('gbk').format(device_name,serino[1::2][index]))
						window.printWhite('')
						os.popen('kill -9 {}'.format(os.getpid()))
						sys.exit()
			else:
				logging.info('adb devices==>{}\n serino==>{}'.format(device_info,serino))
				logging.info('当前设备名为:{},所有设备列表为:{}'.format(device_name,serino[::2]).encode(str_encode))
				if system is 'Windows':
					window.printRed('亲，当前测试设备【{}】未连接或已断开，请检查！\n'.encode('gbk').format(device_name))
					window.printWhite('')
					os.popen('taskkill /f /pid {}'.format(os.getpid()))
					sys.exit()


				else:
					window.printRed('亲，当前测试设备【{}】未连接或已断开，请检查！\n'.format(device_name))
					sys.exit()


if __name__ == '__main__':
	arguments = docopt(__doc__)
	p=android_permance_tool()

	signal.signal(signal.SIGINT,quit)   #中断进程信号(control+c)
	signal.signal(signal.SIGTERM,quit)  #软件终止信号

	'''
	如果参数不等于5个视为无效，只有当参数等于5个时，才执行函数，
	第1个sys.arg[0]参数为：执行的python文件名
	第2个sys.arg[1]参数为：传入的设备名
	第3个sys.arg[2]参数为：传入的包名
	第4个sys.arg[3]参数为: 传入的采集类型,分为,memory\cpu\fps\net\battery\All,其中All为全部采集，
	第5个sys.arg[4]参数为: 传入的采集时间间隔，单位s
	第6个sys.arg[5]参数为: 传入的采集时长，单位s
	第7个sys.arg[6]参数为: 传入的报告名称
	'''
	if system is "Windows" and len(sys.argv)==1:
		print """Usage: 
android_permance_tool.py [-h | --help]
android_permance_tool.py <device_name> <packagename> <collect_type> <delay_time> <max_time> <report_name>
android_permance_tool.py [--merge] <merge_type> <xlsfile1> <xlsfile2>
android_permance_tool.py [--mergefx] <merge_type> <xlsfile1> <xlsfile2>
android_permance_tool.py [-vv]

功能1：Android端性能数据收集及图表自动生成工具（支持内存、cpu、流量、fps、电量、 电压、温度），且同时兼容windows\liunx\mac机上执行采集
功能2：支持两个版本性能数据分析比较，汇总，自动生成新的汇总结果报告，且支持性能测试定制化报告生成
功能3：打印输出当前连接手机设备的应用包名、Activity名

Author：mikezhou
Date:  2017年4月12号

Arguments1:
  device_name     第1个sys.arg[1]参数为：设备序列号
  packagename     第2个sys.arg[2]参数为：采集应用包名
  collect_type    第3个sys.arg[3]参数为：采集类型分为memory、cpu、fps、net、battery、All,其中All为全部采集
  delay_time      第4个sys.arg[4]参数为采集间隔，单位秒，当设置为0时，则持续采集
  max_time        第5个sys.arg[5]参数为采集时长，单位秒
  report_name     第6个sys.arg[6]参数为生成报告名称

Arguments2:
  merge           第1个sys.arg[1]参数为:需执行的动作为合并汇总报告，使用--merge或--mergefx（繁星定制化模板）
  merge_type      第2个sys.arg[2]参数为：合并汇总指标类别,分为memory、cpu、fps、net、battery、All,其中All为全部分析（当使用--mergefx时，类别只能选择All）
  xlsfile1        第3个sys.arg[3]参数为：报告文件1，报告文件需放在脚本根目录下
  xlsfile2        第4个sys.arg[4]参数为：报告文件2，报告文件需放在脚本根目录下


Example1:
说明:针对android性能数据采集命令示例
示例1：python android_permance_tool.py K31GLMA660800338 com.kugou.fanxing battery 2 30  采集繁星电量指标30秒
示例2：python android_permance_tool.py K31GLMA660800338 com.kugou.fanxing memory 0 30  采集繁星内存指标30秒
示例3：python android_permance_tool.py K31GLMA660800338 com.kugou.fanxing All 1 60  采集繁星全部指标60秒
示例4：python android_permance_tool.py AA7DKF4LRGBMPVYL com.kugou.android All 1 30  采集酷狗全部指标30秒

Example2:
说明:针对版本数据自动分析，对比分析两个版本之间结果汇总示例 (表格1为基线版本，表格2为测试版本)
示例1：python android_permance_tool.py --merge fps android_permance_report_2016_12_01_15_38_44.xlsx android_permance_report_2016_12_01_15_44_01.xlsx
示例2：python android_permance_tool.py --merge All android_permance_report1.xlsx android_permance_report2.xlsx

Example3:
说明: 定制化报告模板生成，对比分析两个版本之间结果汇总示例 (表格1为基线版本，表格2为测试版本)
示例1：python android_permance_tool.py --mergefx All 基线版本.xlsx 测试版本.xlsx

Options:
  -H --help    查看帮助信息
  --merge      合并功能
  --mergefx    繁星定制化合并报告
  -vv          输出当前应用包名、activity名
""".encode('gbk')

	elif len(sys.argv)==5 and sys.argv[1]=='--merge':
		xlsfile1=os.path.join(os.getcwd(),sys.argv[3])
		xlsfile2=os.path.join(os.getcwd(),sys.argv[4])
		if os.path.exists(xlsfile1) and os.path.exists(xlsfile2):
			read_excel=ReadExcel()
			#获取两个表中所有sheets名称
			xlsfile1_sheets=read_excel.get_sheet_names(xlsfile1)
			xlsfile2_sheets=read_excel.get_sheet_names(xlsfile2)
			#分析合并fps报表
			if sys.argv[2]=='fps' and 'fps' in xlsfile1_sheets and 'fps' in xlsfile2_sheets:
				p.mergeFPS(xlsfile1,xlsfile2)

			if sys.argv[2]=='cpu' and 'cpu' in xlsfile1_sheets and 'cpu' in xlsfile2_sheets:
				p.mergeCPU(xlsfile1,xlsfile2)

			if sys.argv[2]=='net' and 'net' in xlsfile1_sheets and 'net' in xlsfile2_sheets:
				p.mergeNET(xlsfile1,xlsfile2)

			if sys.argv[2]=='battery' and 'battery' in xlsfile1_sheets and 'battery' in xlsfile2_sheets:
				p.mergeBattery(xlsfile1,xlsfile2)

			if sys.argv[2]=='memory' and 'memory' in xlsfile1_sheets and 'memory' in xlsfile2_sheets:
				p.mergeMemory(xlsfile1,xlsfile2)

			if sys.argv[2]=='All' and 'fps' in xlsfile1_sheets and 'fps' in xlsfile2_sheets and \
							'cpu' in xlsfile1_sheets and 'cpu' in xlsfile2_sheets and \
							'battery' in xlsfile1_sheets and 'battery' in xlsfile2_sheets and\
							'net' in xlsfile1_sheets and 'net' in xlsfile2_sheets and \
							'memory' in xlsfile1_sheets and 'memory' in xlsfile2_sheets:
				p.mergeAll(xlsfile1,xlsfile2)

	elif len(sys.argv)==5 and sys.argv[1]=='--mergefx':
		xlsfile1=os.path.join(os.getcwd(),sys.argv[3])
		xlsfile2=os.path.join(os.getcwd(),sys.argv[4])
		if os.path.exists(xlsfile1) and os.path.exists(xlsfile2):
			read_excel=ReadExcelFX()
			#获取两个表中所有sheets名称
			xlsfile1_sheets=read_excel.get_sheet_names(xlsfile1)
			xlsfile2_sheets=read_excel.get_sheet_names(xlsfile2)

			if sys.argv[2]=='All' and 'fps' in xlsfile1_sheets and 'fps' in xlsfile2_sheets and \
							'cpu' in xlsfile1_sheets and 'cpu' in xlsfile2_sheets and \
							'battery' in xlsfile1_sheets and 'battery' in xlsfile2_sheets and\
							'net' in xlsfile1_sheets and 'net' in xlsfile2_sheets and \
							'memory' in xlsfile1_sheets and 'memory' in xlsfile2_sheets:
				p.mergeAllFX(xlsfile1,xlsfile2)

		else:
			if system is "Windows":
				if not os.path.exists(xlsfile1) and not os.path.exists(xlsfile2):
					print "指定的报告名{},{}在执行的根目录下都不存在!".encode('gbk').format(os.path.basename(xlsfile1),os.path.basename(xlsfile2))
				elif not os.path.exists(xlsfile1):
					print "指定的报告名{}在执行的根目录下不存在!".encode('gbk').format(os.path.basename(xlsfile1))
				elif not os.path.exists(xlsfile2):
					print "指定的报告名{}在执行的根目录下不存在!".encode('gbk').format(os.path.basename(xlsfile2))
			else:
				if not os.path.exists(xlsfile1) and not os.path.exists(xlsfile2):
					print "指定的报告名{},{}在执行的根目录下都不存在!".format(os.path.basename(xlsfile1),os.path.basename(xlsfile2))
				elif not os.path.exists(xlsfile1):
					print "指定的报告名{}在执行的根目录下不存在!".format(os.path.basename(xlsfile1))
				elif not os.path.exists(xlsfile2):
					print "指定的报告名{}在执行的根目录下不存在!".format(os.path.basename(xlsfile2))

	#输出当前连接的设备序列号、包名、activity名
	elif len(sys.argv)==2 and sys.argv[1]=='-vv':
		get_current_device_info()

	elif len(sys.argv)<6:
		print 'No action specified.'
		sys.exit(0)
	else:
		device_name=sys.argv[1]
		packapgename=sys.argv[2]
		_type=sys.argv[3]
		_times=sys.argv[4]
		_durings=sys.argv[5]
		report_name=sys.argv[6]
		if system is "Windows":
			print "参数列表:".encode('gbk'),device_name,packapgename,_type,_times,_durings,report_name
		else:
			print "参数列表:",device_name,packapgename,_type,_times,_durings,report_name

		for i in ext:
			if i in packapgename:
				ext_.append(i)

		if len(ext_)==0:
			logging.info('传入的进程名为前端进程!'.encode(str_encode))
		else:
			logging.info('传入的进程名为后台进程!'.encode(str_encode))

		get_current_device_info()
		t=threading.Thread(target=check_device_status,args=(device_name,))
		t.start()

		p.main(device_name,packapgename,_type,int(_times),int(_durings),report_name)
		if system is "Windows":
			print "结果报告输出目录:".encode('gbk'),os.path.abspath(os.getcwd())
		else:
			print "结果报告输出目录:",os.path.abspath(os.getcwd())

		if system is "Windows":
			print "报告名称为:{}\n报告自动生成完成!".encode('gbk').format(report_name)
			os.popen('taskkill /f /pid {}'.format(os.getpid()))
		else:
			print "报告名称为:{}\n报告自动生成完成!".format(report_name)
			os.popen('kill -9 {}'.format(os.getpid()))


					


