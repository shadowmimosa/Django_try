#coding=utf-8

import sys
import time, traceback
import os
# import sys
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

# Evaluate    reload(sys)    sys
# sys.setdefaultencoding('utf-8')

# # 环境变量配置JoyrunEvn（测试环境值：Test或0；生产环境值：其他值为生产环境）

#home=Get_pwd()
ostype = sys.platform  #获取当前系统类型
print('os type is:', ostype)
if ostype == 'win32' or ostype == 'win64':
    pwd = os.popen('cd').readlines()[0]
    print('Path is  ', pwd)
else:
    pwd = os.popen('pwd').readlines()[0]
    print('Path  is: ', pwd)
home = pwd.replace('\n', '')
##==================================开发测试生产环境通用参数=======================
#请求头参数-前端系统版本号
SYSVERSION = '11.2.1'

#请求头参数-设备号
deviceToken = 'cb9012fd0302813461884e4a3fcc382886b73f6518c1dbe1f031a3901ee72eb4'

#请求头参数-客户端浏览器
UserAgent = 'joyRunner/4.1.0 (iPhone; iOS 11.2.1; Scale/3.00)'

#请求头参数-APP的开发版本号
APPDEVINFO = 'iOS#4.4.1.AutoTest#iPhone 7X#11.2.Joyrun#DeveiceId#UserID#AppStore#E50BA530-7648-4F2F-BE00-4F9563FBCF6E'

#请求头参数-设备类型
MODELTYPE = 'iPhone 7 Plus'

#请求头参数-cookies中app的版本号信息
appversion = 'ios4.1.1'

#请求头参数Content-Type
ContentType = 'application/x-www-form-urlencoded'

#线上运行用户列表   注意以下用名的密码要一致；
Onlineuserlist = '13926281760,13926281760,5145311,13064764870,13926281760,13064764870,13064764870,5145311,0802@163.com,13829744541'

#测试运行用户列表   注意以下用名的密码要一致；
Testuserlist = '13829744541,13829744542,13829744543,13829744544,13829744545,13064764870,13926281760,5145311,13926281760'

#beta测试运行用户列表   注意以下用名的密码要一致；
Betauserlist = '13829744541,13829744542,13829744543,13829744544,13829744545,13064764870,13926281760,5145311,13926281760'

#线上运行用户列表   格式【用户名/用户密码】分隔符【,】
Onlineusrp = '13926281760/67889911,13926281760/67889911,5145311/67889911,13064764870/67889911,13926281760/67889911,13064764870/67889911,13064764870/67889911,5145311/67889911,0802@163.com/67889911,13829744541/67889911'

#beta测试运行用户列表   格式【用户名/用户密码】分隔符【,】
Betausrp = '13829744541/67889911,13829744542/67889911,13829744543/67889911,13829744544/67889911,13829744545/67889911,13064764870/67889911,13926281760/67889911,5145311/67889911'

#测试运行用户列表   格式【用户名/用户密码】分隔符【,】
Testusrp = '13829744541/67889911,13829744542/67889911,13829744543/67889911,13829744544/67889911,13829744545/67889911,13064764870/67889911,13926281760/67889911,5145311/67889911'

#各版本测试（3.1）Nginx密钥  （app_secrets["3.1"] = "fb1931e425f84313bfae4b93ab3ccdc4"
#app_secrets["3.2"] = "0ce938187774429689749a80d54d4a1b"
#app_secrets["3.3"] = "5dbfb17323a24666a6b6aa0b9620cab6"）
appkey1 = 'fb1931e425f84313bfae4b93ab3ccdc4'

#业务测试密钥
appkey2 = '1fd6e28fd158406995f77727b35bf20a'

#前端验签名的版本号（需要与appkey1相对应，服务根据这个版本号验证appkey1）
APPVERSION = '100.4.1.0'

JoyrunEvn = 'Beta'

Env = ''
##根据JoyrunEnv变量导入不同的变量文件；
if JoyrunEvn in ['Test', 'test', '0', 0]:
    from JoyrunTestEnv_var import *
    Env = 'Test'
elif JoyrunEvn in ['Beta', 'beta', 'BeataEnv', 'betaenv', '1', 1, None]:
    from JoyrunBetaEnv_var import *
    Env = 'Beta'
else:
    from JoyrunOnline_var import *
    Env = 'Online'
