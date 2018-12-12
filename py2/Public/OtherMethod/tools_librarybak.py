#_*_ coding:utf-8 _*_
import re
import os
import sys
import glob
import time
import hashlib
import random
import string
import urllib
from multiprocessing import Process
from threading import Thread

#socket
import socket

exedir = os.path.abspath('.')
sys.path.insert(0,glob.glob(exedir)[0])


class tools_library(object):
##正则表达式等号分割字符串，用于header，cookie等处理
	def splitbyequal(self,arglist):

		pattern = re.compile(r'=')
		res = pattern.split(arglist,1) 
		return res
		
	def char conver(self,content):
		"""Converts the utf-8 content to unicode 
		
		ex:
		| char conver | ${resp.content} |
		"""
		CODEC = 'utf-8'
		str = content.decode(CODEC)
		return str	

	def char conver_unicode(self,content):
		string = content.decode('unicode_escape')
		return string
		
##匹配php的获取第几周接口
	def getNumericOfNowWeek(self):
		return int(time.strftime("%W"))+1
		
	def GetMiddleStr(self,content,startStr,endStr):
		"""get the middle string between the startStr and endStr
		
		ex:
		| GetMiddleStr | AhelloB | A | B |
		The result is 'hello'
		"""		
		if '[' in startStr:
			startStr = startStr.replace('[','\[')
		if ']' in endStr:
			endStr = endStr.replace(']','\]')
		patternStr = r'%s(.+?)%s'%(startStr,endStr)
		p = re.compile(patternStr)
		res = p.search(content).groups()
		return res[0]

###加密	
	def _md5(self,encstr,bit):
		md5str = hashlib.md5(encstr).hexdigest()
		if bit == 16:
			return md5str[8:-8]
		return md5str
		
	def _sha1(self,encstr):
		sha1str = hashlib.sha1(encstr).hexdigest()
		return sha1str

	def _sha512(self,encstr):
		sha512str = hashlib.sha512(encstr).hexdigest()
		return sha512str
		
	def encrypt(self,encstr,type,bit=16):
		"""encrypt string, support MD5, SHA1 present. MD5 default 16bit.
		
		ex:
		| ${md5str}= | encrypt | abcd1234 | md5 |
		"""	
		##switch dictionary
		encrypttype = {'md5':self._md5,'sha1':self._sha1, 'sha512':self._sha512}
		
		if type == 'md5':
			str = encrypttype.get(type)(encstr,bit)
		else:
			str = encrypttype.get(type)(encstr)
		return str
		
###随机生成字符串
	def randomstr(self,bit=16):
		"""generate random string, default 16bit.
		
		ex:
		| ${str}= | randomstr | 13 |
		==> ${str} is a 13 bit string
		"""		
		intbit = int(bit)
		seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
		l = []
		for i in range(intbit):
			l.append(random.choice(seed))
		str = string.join(l).replace(' ','')
		return str

###将cookie写入文件
	def writecookie(self,cookieId,conf_dir,cookies):
		"""write user cookie into config file
		
		ex:
		| ${config_file}=  |  set variable  |  ${CURDIR}\\config.py |
		| ${cookie_tony0}=  |  fx_get_login_notsuite_cookie  |  ${referer}  |  shinetony  |  654321a |
		| ${cookie_tony1}=  |  fx_get_login_notsuite_cookie  |  ${referer}  |  shinetony1  |  654321a |
		| Writecookie  |  cookie_tony0  |  ${config_file}  |  '${cookie_tony0}' |
		| Writecookie  |  cookie_tony1  |  ${config_file}  |  '${cookie_tony1}' |
		"""
		content = "%s = %s"%(eval('cookieId'),eval('cookies'))

		file = open(conf_dir, "r")
		lines=file.readlines()
		file.close()
		for eachline in lines:
			if cookieId in eachline:
				lines[lines.index(eachline)] = content+'\n'
				
		file = open(conf_dir, "w")
		file.writelines(lines)
		file.close()	
		
###rsa for asing
	def rsaEncrypt(self,msg):
		from Crypto.PublicKey import RSA
		from base64 import b64decode
		import binascii 
		exkey = b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2DT4odzkDd7hMlZ7djdZQH12j38nKxriINW1MGjMry3tXheya113xwmbBOwN0GA4zTwKFauFJRzcsD0nDFq1eaatcFKeDF25R4dnQRX+4BdTwFVS8lIb8nJMluSBwK+i4Z3VF+gfZ0AqQOXda6lJ4jPBt9Ep7VXEAHXUDn9JM8wIDAQAB'
		#exkey = b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIAG7QOELSYoIJvTFJhMpe1s/gbjDJX51HBNnEl5HXqTW6lQ7LC8jr9fWZTwusknp+sVGzwd40MwP6U5yDE27M/X1+UR4tvOGOqp94TJtQ1EPnWGWXngpeIW5GxoQGao1rmYWAu6oi1z9XkChrsUdC6DJE5E221wf/4WLFxwAtRQIDAQAB'
		keyDER = b64decode(exkey)
		keyPub = RSA.importKey(keyDER)
		while len(msg) < 128: #匹配java rsa加密，补位
			msg = msg + '\0'
		#print len(msg)
		emsg = keyPub.encrypt(msg,'')[0]
		return binascii.hexlify(emsg).upper()
		
###delete null value for asing
	def popNull(self,dict):
		for (k,v) in dict.items():
			if len(str(v)) == 0 : dict.pop(k)
			else: pass
		return dict


###将数据写入文件
	def filewrite(self,conf_dir,data):
		file = open(conf_dir, "a")
		file.writelines(data+'\n')
		file.close()

	def filewrite_not_overwrite(self, conf_dir, data):
		#for mid autumn
		import codecs
		file = codecs.open(conf_dir, "a", "utf-8")
		data = data.decode("unicode_escape")
		#file.write(data)
		file.writelines(data+'\n')
		file.close()

###清空文件内容
	def filetruncate(self,conf_dir):
		file = open(conf_dir, "a")
		file.truncate()
		file.close()

###读文件内容
	def fileread(self,conf_dir):
		file = open(conf_dir, "r")
		lines=file.readlines()
		file.close()
		return lines

	def utf8urlencode(self,content):
		str = urllib.urlencode({"a":content.encode("utf8")})
		return str	
		
###进房记录
	def _enterRoom(self, roomid, userid):
		#新key算法 		
		self.HOST = '10.12.0.56'
		ENTERPORT = 4321
		self.QUERYPORT = 50005
		#securityKey = 'sJ65(7JHJJX'   #old key
		SECURITYKEY = 'sJ65(%^*()' # new key		

		nickname = "abc"
		richlevel = 13
		staruserid = '1234567'
		kugouid = '2234567'
		ext = ''
		
		timestamp = int(time.time())
		str_for_dsk = str(timestamp) + SECURITYKEY + kugouid
		DynamicSecurityKey = self._sha1(str_for_dsk)
		str_for_md5key = str(roomid) + str(userid) + nickname + str(richlevel) + ext + DynamicSecurityKey
		md5key = self._md5(str_for_md5key,32)
		#key = self._md5(str_for_key,32)
		key = md5key[0:16] + str("%x" % timestamp) + md5key[16:]

		#进房socket
		es = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:  
			es.connect((self.HOST, ENTERPORT))
			#print "starting to enter room..."
			#相比旧的进房，需加上kugouid
			es.send('{"cmd":201,"roomid":%d,"userid":"%s","nickname":"%s","richlevel":%d,"ismaster":2,"staruserid":"%s","key":"%s","kugouid":%d,"keytime":"","ext":""}\r\n' % (int(roomid), str(userid), nickname, int(richlevel), staruserid, key, int(kugouid)))
		except socket.error, msg:  
			print 'Bind failed. Error Code : %s, Message: %s' % (str(msg[0]), msg[1])

		# #查询socket
		# qs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# try:
		#     qs.connect((HOST, QUERYPORT))
		#     qs.send('{"commid":2224,"req":1,"sequence":"1234567","uid":"%s"}\r\n' % userid)
		#     res = qs.recv(1000)
		# except socket.error, msg:
		#     print msg
		# qs.close()

		time.sleep(10) #进房记录保持10秒
		es.close()
	
	def enterRoom(self, roomid, *userid):
		"""create one or more enterRoom date use socket for soa
		default host：10.12.0.56 , if you want to change it, please check the method _enterRoom in tools_library.
		
		example:
		| enterRoom | 1012021 | 39089058 |
		| enterRoom | 1012021 | 39089058 | 39088973 | # two userids |
		"""
		for user in userid:
			#线程后台进房，不影响后续用例执行
			t = Thread(target=self._enterRoom,args=(roomid,user))
			t.start()
			print "%s enter room success..." % str(user)
		time.sleep(1) #等待进房记录更新
		
		#p.join()

	def queryRoomInfo(self, *userid):
		"""用于校验进房是否成功，请勿单独调用
		"""
		# #查询socket
		res = []
		qs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
		    qs.connect((self.HOST, self.QUERYPORT))
		    for user in userid:
		    	qs.send('{"commid":2224,"req":1,"sequence":"1234567","uid":"%s"}\r\n' % user)
		    	res.append(qs.recv(1000))
		except socket.error, msg:
		    print msg
		qs.close()
		return res

		
#测试代码
if __name__ == '__main__':
	t = tools_library()
	t.enterRoom(1012021,39089058)
	t.queryRoomInfo(39089058)

		
		