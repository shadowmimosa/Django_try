#_*_ coding:utf-8 _*_

import os
import sys
import glob
import base64
from Crypto.Cipher import DES
from Crypto import Random



exedir = os.path.abspath('.')
sys.path.insert(0,glob.glob(exedir)[0])


class tools_library(object):

	def des_encrypt(self, data, key="@#$%eXPD*&#"):
		"""用于生成提现密码
		data为明文,key为密钥,key必须大于等于8位

		Examples:
		| des_encrypt | 123456 |
		| des_encrypt | 123456 | abcdefgh |
		"""

		if not data:
			return None

		bs = DES.block_size

		# PKCS5Padding
		pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

		if len(key) > 8:
			key = key[0:8]

		iv = Random.new().read(bs)
		cipher = DES.new(key, DES.MODE_ECB, iv)

		bt = cipher.encrypt(pad(data))

		return base64.urlsafe_b64encode(bt).rstrip("=")

	def des_decrypt(self, passwd, key="@#$%eXPD*&#"):
		"""用于将提现密码解码成明文
		data为密码, key为密钥,key必须大于等于8位

		Examples:
		| des_decrypt | Sb2tYr1chEI |
		"""

		if not passwd:
			return None

		# padding "="
		passwd += ( 4 - len(passwd) % 4 ) * "="

		bs = DES.block_size

		# PKCS5Padding
		unpad = lambda s : s[0:-ord(s[-1])]

		if len(key) > 8:
			key = key[0:8]

		# 解决base64 decode bug
		passwd = unicode(passwd).encode('ascii')
		passwd = base64.urlsafe_b64decode(passwd)

		iv = Random.new().read(bs)
		cipher = DES.new(key, DES.MODE_ECB, iv)

		return unpad(cipher.decrypt(passwd))


		
#测试代码
if __name__ == '__main__':
	t = tools_library()
	print t.des_encrypt("123456")
	print t.des_decrypt("Sb2tYr1chEI", "@#$%eXPD*&")