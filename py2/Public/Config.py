#coding=utf-8

import sys
import time,traceback
import os
import sys
import platform
import subprocess
import random
import re
###导入其他python文件的方法，Config_Env为文件名，引入此文件要与执行文件目录一致，否则要加文件路径
#sys.path.append(r'E:\Work\Test\Enjoytherun\Public\Sub')
##pathbase = os.path.dirname(os.path.realpath(__file__))    ##读取当前文件的路径
#pathfile =  pathbase +  '/Sub'
#sys.path.append(pathfile)
#from Config_Env import * 

reload(sys)
sys.setdefaultencoding('utf-8')

# # 环境变量配置JoyrunEvn（测试环境值：Test或0；生产环境值：其他值为生产环境）

JoyrunEvn='Test'
#home=Get_pwd()
ostype = sys.platform   #获取当前系统类型
print  'os type is:',ostype   
if  ostype=='win32'  or  ostype=='win64':
	pwd=os.popen('cd').readlines()[0]
	print   'Path is  ', pwd
else:
    pwd=os.popen('pwd').readlines()[0]
    print  'Path  is: ', pwd   
home=pwd.replace('\n','')
##==================================开发测试生产环境通用参数=======================
#请求头参数-前端系统版本号
SYSVERSION='11.2.1'

#请求头参数-设备号
deviceToken='cb9012fd0302813461884e4a3fcc382886b73f6518c1dbe1f031a3901ee72eb4'

#请求头参数-客户端浏览器
UserAgent='joyRunner/4.1.0 (iPhone; iOS 11.2.1; Scale/3.00)'

#请求头参数-APP的开发版本号
APPDEVINFO='iOS#4.4.1.AutoTest#iPhone 7X#11.2.Joyrun#DeveiceId#UserID#AppStore#E50BA530-7648-4F2F-BE00-4F9563FBCF6E'

#请求头参数-设备类型
MODELTYPE='iPhone 7 Plus'

#请求头参数-cookies中app的版本号信息
appversion='ios4.1.1'

#请求头参数Content-Type
ContentType='application/x-www-form-urlencoded'

#线上运行用户列表   注意以下用名的密码要一致；
Onlineuserlist='13926281760,13926281760,5145311,13064764870,13926281760,13064764870,13064764870,5145311,0802@163.com,13829744541'

#测试运行用户列表   注意以下用名的密码要一致；
Testuserlist='13829744541,13829744542,13829744543,13829744544,13829744545,13064764870,13926281760,5145311,13926281760'

#线上运行用户列表   格式【用户名/用户密码】分隔符【,】
Onlineusrp='13926281760/67889911,13926281760/67889911,5145311/67889911,13064764870/67889911,13926281760/67889911,13064764870/67889911,13064764870/67889911,5145311/67889911,0802@163.com/67889911,13829744541/67889911'

#测试运行用户列表   格式【用户名/用户密码】分隔符【,】
Testusrp='13829744541/67889911,13829744542/67889911,13829744543/67889911,13829744544/67889911,13829744545/67889911,13064764870/67889911,13926281760/67889911,5145311/67889911'

#各版本测试（3.1）Nginx密钥  （app_secrets["3.1"] = "fb1931e425f84313bfae4b93ab3ccdc4"
#app_secrets["3.2"] = "0ce938187774429689749a80d54d4a1b"
#app_secrets["3.3"] = "5dbfb17323a24666a6b6aa0b9620cab6"）
appkey1='fb1931e425f84313bfae4b93ab3ccdc4'

#业务测试密钥
appkey2='1fd6e28fd158406995f77727b35bf20a'

#前端验签名的版本号（需要与appkey1相对应，服务根据这个版本号验证appkey1）
APPVERSION='100.4.1.0'



if  JoyrunEvn=='Test' or JoyrunEvn=='0':


	# #===============测试环境下连接地址(Test)=======================
		# app通用签名
	APP_SGIN='a9ff6970eb814e6894389ca8b12f3030' 

	# 登录地址
	login_URL='http://api-test.thejoyrun.com' 

	#api项目地址
	api_URL='http://api-test.thejoyrun.com' 

	#beta约定跑相关
	beta_URL='http://beta-test.thejoyrun.com'

	#bet 动态配置相关
	bet_URL='http://bet-test.api.thejoyrun.com'

	# user用户工程,与用户信息相关
	user_URL='http://u-test.api.thejoyrun.com' 

	# topic工程,与首页相关
	topic_URL='http://topic-test.api.thejoyrun.com' 

	#crew-muilt 与跑团相关1
	crew_muilt_URL='http://crew-muilt-test.api.thejoyrun.com' 

	#crew 与跑团相关2
	crew_URL='http://crew-test.api.thejoyrun.com' 

	#crewapp 跑团相关3
	crewapp_URL='http://crewapp-test.api.thejoyrun.com'

	# ec电商工程,与订单相关
	ec_URL='http://ec-test.thejoyrun.com'

	# advert工程,与消息广告通告相关
	advert_URL='http://advert-test.api.thejoyrun.com'

	# training工程,与训练相关
	training_URL='http://training-test.api.thejoyrun.com'

	# wear工程,与穿戴相关
	wear_URL='http://wear-test.api.thejoyrun.com'

	#point_
	point_URL='http://point-test.api.thejoyrun.com'

	#im 消息相关
	im_URL='http://im-test.api.thejoyrun.com'

	#marathon 马拉松相关
	marathon_URL='http://marathon-test.api.thejoyrun.com'

	#recommend 推荐相关
	recommend_URL='http://recommend-test.api.thejoyrun.com'

	#live 赛事直播相关
	live_URL='http://live-test.api.thejoyrun.com'

	#wallet 推荐相关
	wallet_URL='http://wallet-test.api.thejoyrun.com'

	#media 媒体资讯相关
	media_URL='http://media-test.api.thejoyrun.com'

	#challenge 挑战相关
	challenge_URL='http://challenge-test.api.thejoyrun.com'

	#event 事件相关
	event_URL='http://event-test.api.thejoyrun.com'

	#企业跑团
	cr_URL='http://cr-test.thejoyrun.com'
	
	#天气web
	webevent_URL='http://webevent-test.thejoyrun.com'

	#跑场
	rd_URL='http://rd-test.api.thejoyrun.com'
	
	#赛事小助手
	trip_URL='http://trip-test.api.thejoyrun.com'
	
	#阿凡达
	equipment_URL='http://equipment-test.api.thejoyrun.com'
	
	#赛事实况
	racelive_URL='http://racelive-test.api.thejoyrun.com'
	
	#搜索
	search_URL='http://search-test.api.thejoyrun.com'
	
	#语音训练—H5
	training_dubbox_URL='http://training.dubbox.test.thejoyrun.com'

	
	##===================小程序相关配置=====================

	#小程序统一域名
	mapp_URL='https://mapp-test.api.thejoyrun.com'
	
	###小程序万能签名
	mapp_sgin='MAPP-MASTER-SECRET-TEST'

	#小程序公共密钥
	mappkey='hello-joyrun-micro-app'

	#跑团小程序APPID
	corpcrewappid='wx1fef2e38049c8d5f'

	#跑团小程序用户身份sid  2018-02-06 12:30    eda1412c27f249189d4a0901d9c18c4b8
	corpcrewsid='80e564cec2364e749f5400f1dad8a76bb'

	#约定跑小程序APPID    wxd19597f62e33ba65
	betappid='wx77b7bc5511256564'

	#约定跑小程序用户身份sid  2018-05-10 12:30 
	betsid='45e1af48da7541cebc86aec6c8215110f'
	
	#赛事小程序APPID  根据请求url的path取的第一级目录命名+appid=config中的命名，如赛事小程序trip/,tripappid
	tripappid='wx1f211a6a3607d8fe'
	
	#赛事小程序用户身份sid 2018-8-17   赛事小程序uid15108880，sid笙箫默微信
	tripsid='b4db1909f66a4af3b261a70e875c06a48'

else:
#=======================线上发布连接地址(Online)========================
	# app通用签名
	APP_SGIN='A4729E62-3701-48C3-A15D-7391838FA186' 

	# 登录地址
	login_URL='http://api.thejoyrun.com' 

	#api项目地址
	api_URL='http://api.thejoyrun.com' 

	#beta约定跑相关
	beta_URL='http://beta.thejoyrun.com'

	#bet 动态配置相关
	bet_URL='http://bet.api.thejoyrun.com'

	# user用户工程,与用户信息相关
	user_URL='http://u.api.thejoyrun.com' 

	# topic工程,与首页相关
	topic_URL='http://topic.api.thejoyrun.com' 

	#crew-muilt 与跑团相关1
	crew_muilt_URL='http://crew-muilt.api.thejoyrun.com' 

	#crew 与跑团相关2
	crew_URL='http://crew.api.thejoyrun.com' 

	#crewapp 跑团相关3
	crewapp_URL='http://crewapp.api.thejoyrun.com'

	# ec电商工程,与订单相关
	ec_URL='http://ec.thejoyrun.com'

	# advert工程,与消息广告通告相关
	advert_URL='http://advert.api.thejoyrun.com'

	# training工程,与训练相关
	training_URL='http://training.api.thejoyrun.com'

	# wear工程,与穿戴相关
	wear_URL='http://wear.api.thejoyrun.com'

	#point_
	point_URL='http://point.api.thejoyrun.com'

	#im 消息相关
	im_URL='http://im.api.thejoyrun.com'

	#marathon 马拉松相关
	marathon_URL='http://marathon.api.thejoyrun.com'

	#recommend 推荐相关
	recommend_URL='http://recommend.api.thejoyrun.com'

	#live 赛事直播相关
	live_URL='http://live.api.thejoyrun.com'

	#wallet 推荐相关
	wallet_URL='http://wallet.api.thejoyrun.com'

	#media 媒体资讯相关
	media_URL='http://media.api.thejoyrun.com'

	#challenge 挑战相关
	challenge_URL='http://challenge.api.thejoyrun.com'

	#event 事件相关
	event_URL='http://event.api.thejoyrun.com'

	#企业跑团
	cr_URL='https://cr.thejoyrun.com'
	
	#跑场
	rd_URL='http://rd.api.thejoyrun.com'

	#天气web
	webevent_URL='https://webevent.thejoyrun.com'
	
	#赛事小助手
	trip_URL='https://trip.api.thejoyrun.com'
	
	#阿凡达
	equipment_URL='http://equipment.api.thejoyrun.com'	
	
	#赛事实况
	racelive_URL='http://racelive.api.thejoyrun.com'

	#搜索
	search_URL='http://search.api.thejoyrun.com'
	
	#语音训练—H5
	training_dubbox_URL='http://training.dubbox.thejoyrun.com'

	
	#=====小程序相关配置=================================

	#小程序统一域名
	mapp_URL='https://mapp.api.thejoyrun.com'
	
	###小程序万能签名
	mapp_sgin='27509554-6861-4394-9B84-9D5698A4DD1A'
	
	#小程序公共密钥
	mappkey='hello-joyrun-micro-app'

	#跑团小程序APPID
	corpcrewappid='wx24fffb22401a1157'

	#跑团小程序用户身份sid===2018-02-06  10:28
	corpcrewsid='6861e3f7620840c2b03d8eff181a61d70'

	##约定跑小程序APPID
	betappid='wxd19597f62e33ba65'

	##约定跑小程序用户身份sid  2018-02-06 12:30 
	betsid='478364efd1f54d10860f263a724f7c364'
	
	#赛事小程序APPID  根据请求url的path取的第一级目录命名+appid=config中的命名，如赛事小程序trip/,tripappid
	tripappid='wx1f211a6a3607d8fe'
	
	#赛事小程序用户身份sid 2018-6-21
	tripsid='cfd56ea6c401403cba16c80d467bd7233'








