import re
import os
import sys
import glob
import time
import hashlib
import random
import string
import urllib
import base64
import shutil
import struct
from threading import Thread
from urllib.parse import quote, unquote

#socket
import socket

#db connect
import pymysql

exedir = os.path.abspath('.')
sys.path.insert(0, glob.glob(exedir)[0])


class tools_library(object):
    ##正则表达式等号分割字符串，用于header，cookie等处理
    def __init__(self):
        self.clients = {}

    def splitbyequal(self, arglist):

        pattern = re.compile(r'=')
        res = pattern.split(arglist, 1)
        return res

    def charconver(self, content):
        """Converts the utf-8 content to unicode 
		
		ex:
		| charconver | ${resp.content} |
		"""
        print(type(content))
        print(content)
        if type(content) == bytes:
            content = str(content, encoding='UTF-8')
            print(type(content))
            print(content)
            return content
        elif type(content) == str:
            return content
        elif type(content) == dict:
            return str(content)
        else:
            raise TypeError

    def charconver_unicode(self, content):
        """converts chinese(unicode_escape) to unicode"""
        string = content('unicode_escape')
        return string

##匹配php的获取第几周接口

    def getNumericOfNowWeek(self):
        week = int(time.strftime("%W")) + 1
        if week < 10:
            return '0' + str(week)
        else:
            return str(week)

    def GetMiddleStr(self, content, startStr, endStr):
        """get the middle string between the startStr and endStr
		
		ex:
		| GetMiddleStr | AhelloB | A | B |
		The result is 'hello'
		"""
        if '[' in startStr:
            startStr = startStr.replace('[', '\\[')
        if ']' in endStr:
            endStr = endStr.replace(']', '\\]')
        patternStr = r'%s(.+?)%s' % (startStr, endStr)
        p = re.compile(patternStr)
        res = p.search(content).groups()
        return res[0]

##获取星期几

    def getWeekday(self):
        """
		rtype: 0-6
		"""
        return time.strftime("%w", time.localtime())

###加密

    def _md5(self, encstr, bit):
        md5str = hashlib.md5(encstr).hexdigest()
        if bit == 16:
            return md5str[8:-8]
        return md5str

    def _sha1(self, encstr):
        sha1str = hashlib.sha1(encstr).hexdigest()
        return sha1str

    def _sha512(self, encstr):
        sha512str = hashlib.sha512(encstr).hexdigest()
        return sha512str

    def _base64en(self, encstr):
        base64str = base64.b64encode(encstr)
        return base64str

    def _base64de(self, encstr):
        base64str = base64.b64decode(encstr)

    def encrypt(self, encstr, type, bit=16):
        """encrypt string, support md5, sha1, sha512, base64en, base64de present. md5 default 16bit.
		
		ex:
		| ${md5str}= | encrypt | abcd1234 | md5 |
		"""
        ##switch dictionary
        encrypttype = {
            'md5': self._md5,
            'sha1': self._sha1,
            'sha512': self._sha512,
            'base64en': self._base64en,
            'base64de': self._base64de
        }

        if type == 'md5':
            str = encrypttype.get(type)(encstr.encode('utf-8'), bit)
        else:
            str = encrypttype.get(type)(encstr.encode('utf-8'))
        return str

###随机生成字符串

    def randomstr(self, bit=16):
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
        str = ''.join(l).replace(' ', '')
        return str

###将cookie写入文件

    def writecookie(self, cookieId, conf_dir, cookies):
        """write user cookie into config file
		
		ex:
		| ${config_file}=  |  set variable  |  ${CURDIR}\\config.py |
		| ${cookie_tony0}=  |  fx_get_login_notsuite_cookie  |  ${referer}  |  shinetony  |  654321a |
		| ${cookie_tony1}=  |  fx_get_login_notsuite_cookie  |  ${referer}  |  shinetony1  |  654321a |
		| Writecookie  |  cookie_tony0  |  ${config_file}  |  '${cookie_tony0}' |
		| Writecookie  |  cookie_tony1  |  ${config_file}  |  '${cookie_tony1}' |
		"""
        content = "%s = %s" % (eval('cookieId'), eval('cookies'))

        file = open(conf_dir, "r")
        lines = file.readlines()
        file.close()
        for eachline in lines:
            if cookieId in eachline:
                lines[lines.index(eachline)] = content + '\n'

        file = open(conf_dir, "w")
        file.writelines(lines)
        file.close()

###rsa for asing

    def rsaEncrypt(self, msg, dp='m', pd=None):
        from Crypto.Cipher import PKCS1_v1_5
        from Crypto.PublicKey import RSA
        import binascii
        m_exkey = b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2DT4odzkDd7hMlZ7djdZQH12j38nKxriINW1MGjMry3tXheya113xwmbBOwN0GA4zTwKFauFJRzcsD0nDFq1eaatcFKeDF25R4dnQRX+4BdTwFVS8lIb8nJMluSBwK+i4Z3VF+gfZ0AqQOXda6lJ4jPBt9Ep7VXEAHXUDn9JM8wIDAQAB'  #mobile
        #exkey = b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIAG7QOELSYoIJvTFJhMpe1s/gbjDJX51HBNnEl5HXqTW6lQ7LC8jr9fWZTwusknp+sVGzwd40MwP6U5yDE27M/X1+UR4tvOGOqp94TJtQ1EPnWGWXngpeIW5GxoQGao1rmYWAu6oi1z9XkChrsUdC6DJE5E221wf/4WLFxwAtRQIDAQAB'
        pc_exkey = b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDfKKPMFF1ubzVM4/BPNWNLpZXTXzPNScvJM5CRPzQVql0pHaJyBhXipBVFOQZTzsakai7qyn4K+0W/cu1wbJ1NsHHtmhscSC/+5VSE/UTjcvUfCgBamWPNHhOldxE80m8XananVYNIYwUPJQxNAp2Zgh4mrco4XSxiMDs02rHf6wIDAQAB'  #pcserver
        java_exkey = b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC8QiwOOAXpvl6UZHWLyFBkLIkBzubpg4/lMCinzCyhhmB7HRRNGNEaUHiGjCAvWSvvdd+YOoR55Z7SSI3gL3d257DpZNq5tZYKxJEnYOlNWlcUrGYL7JYgrkgVQneVbGsJnxNT3KeaxcrJb4JsA4QhMjU3chJTUGoJW1L3zwletQIDAQAB'
        if dp == 'm':
            exkey = m_exkey
        elif dp == 'java':
            exkey = java_exkey
        else:
            exkey = pc_exkey
        keyDER = base64.b64decode(exkey)
        keyPub = RSA.importKey(keyDER)
        while len(msg) < 128:  #匹配java rsa加密，补位
            msg = msg + '\0'
        if dp == 'java':
            cipher = PKCS1_v1_5.new(keyPub)
            emsg = cipher.encrypt(str(msg[:-11]))
            ret = binascii.hexlify(emsg)
        else:
            emsg = keyPub.encrypt(msg, '')[0]
            ret = binascii.hexlify(emsg).upper()
        return ret

###delete null value for asing

    def popNull(self, dict):
        for (k, v) in dict.items():
            if len(str(v)) == 0: dict.pop(k)
            else: pass
        return dict

###将数据写入文件

    def filewrite(self, conf_dir, data):
        file = open(conf_dir, "a")
        file.writelines(data + '\n')
        file.close()

    def filewrite_not_overwrite(self, conf_dir, data):
        #for mid autumn
        import codecs
        file = codecs.open(conf_dir, "a", "utf-8")
        data = data.decode("unicode_escape")
        #file.write(data)
        file.writelines(data + '\n')
        file.close()

###清空文件内容

    def filetruncate(self, conf_dir):
        file = open(conf_dir, "a")
        file.truncate()
        file.close()

###读文件内容

    def fileread(self, conf_dir):
        file = open(conf_dir, "r")
        lines = file.readlines()
        file.close()
        return lines

    def utf8urlencode(self, content):
        str = urllib.parse.urlencode({"a": content.encode("utf8")})
        return str

    def urlencode(self, content):
        str = quote(content.encode("utf8"))
        return str

    def urluncode(self, content):
        str = quote(content.encode("utf8"))
        return str

###获取本地ip

    def getip(self, iptype='str'):
        """获取本地ip，不传参默认返回字符串，传任意参返回unsignlong类型的ip
		
		example:
		| getip | # get string ip like:"172.17.10.225"
		| getip | 1 | # get unsignlong ip like "2886798049"  """

        localIP = socket.gethostbyname(socket.gethostname())
        if iptype == 'str':
            return localIP
        else:
            return self.iptolong(localIP)

###将ip由str转为unsignlong

    def iptolong(self, ip):
        intip = struct.unpack('!L', socket.inet_aton(ip))[0]
        return intip

###绑定host

    def bindhost(self, ip, host):
        """edit the hosts, bind a new ip-host or overwrite the binding ip-host	

		ex:
		| bindhost | 10.12.0.62 | act.fxkf.kugou.com |
		you shoud use method "restorehost" to restore the hosts after testing
		"""
        p = re.compile(r'.+' + host + r'\n')
        rhosts = open("C:\\Windows\\System32\\drivers\\etc\\hosts", 'r')
        shutil.copyfile("C:\\Windows\\System32\\drivers\\etc\\hosts",
                        "C:\\Windows\\System32\\drivers\\etc\\hoststemp")
        s = rhosts.read()
        s2 = re.sub(p, '', s)
        if (s2[len(s2) - 1] == '\n'):
            s2 = s2 + str(ip) + ' ' + str(host) + '\n'
        else:
            s2 = s2 + '\n' + str(ip) + ' ' + str(host) + '\n'
        whosts = open("C:\\Windows\\System32\\drivers\\etc\\hosts", 'w')
        whosts.write(s2)

###还原hosts文件

    def restorehost(self):
        """	restore the hosts from /etc/hoststemp
		
		ex:
		| restorehost |
		"""
        shutil.copyfile("C:\\Windows\\System32\\drivers\\etc\\hoststemp",
                        "C:\\Windows\\System32\\drivers\\etc\\hosts")

#db connect

    def _db_conn(self):
        return pymysql.connect(
            host='10.16.6.90',
            port=3306,
            user='fanxing',
            passwd='kugou2014',
            db='d_fanxing',
            charset='utf8')

###进房记录

    def _enterRoom(self, es, roomid, userid):
        #新key算法
        self.HOST = '10.16.6.90'
        ENTERPORT = 4321
        self.QUERYPORT = 50005
        #securityKey = 'sJ65(7JHJJX'   #old key
        SECURITYKEY = 'sJ65(%^*()'  # new key

        conn = self._db_conn()
        c = conn.cursor()
        c.execute("select kugouId from t_user where userId = %d" % int(userid))
        for r in c:
            kugouid = str(r[0])

        nickname = "abc"
        richlevel = 13
        staruserid = '1234567'
        ext = ''

        timestamp = int(time.time())
        str_for_dsk = str(timestamp) + SECURITYKEY + kugouid
        DynamicSecurityKey = self._sha1(str_for_dsk)
        str_for_md5key = str(roomid) + str(userid) + nickname + str(
            richlevel) + ext + DynamicSecurityKey
        md5key = self._md5(str_for_md5key, 32)
        #key = self._md5(str_for_key,32)
        key = md5key[0:16] + str("%x" % timestamp) + md5key[16:]

        #进房socket
        try:
            es.connect((self.HOST, ENTERPORT))
            #print( "starting to enter room...")
            #相比旧的进房，需加上kugouid
            es.send(
                '{"cmd":201,"roomid":%d,"userid":"%s","nickname":"%s","richlevel":%d,"ismaster":2,"staruserid":"%s","key":"%s","kugouid":%d,"keytime":"","ext":""}\r\n'
                % (int(roomid), str(userid), nickname, int(richlevel),
                   staruserid, key, int(kugouid)))
        except socket.error as msg:
            pass
        # #查询socket
        # qs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # try:
        #     qs.connect((HOST, QUERYPORT))
        #     qs.send('{"commid":2224,"req":1,"sequence":"1234567","uid":"%s"}\r\n' % userid)
        #     res = qs.recv(1000)
        # except socket.error, msg:
        #     print( msg)
        # qs.close()
        time.sleep(20)  #进房记录保持20秒
        es.close()

    def enterRoom(self, roomid, *userid):
        """create one or more enterRoom date use socket for soa
		default host：10.16.6.90 , if you want to change it, please check the method _enterRoom in tools_library.
		
		example:
		| enterRoom | 1012021 | 39089058 |
		| enterRoom | 1012021 | 39089058 | 39088973 | # two userids |
		"""
        for user in userid:
            #线程后台进房，不影响后续用例执行
            es = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #一个user可以进多个roomid，分开申请socket
            self.clients.setdefault(user, {})
            self.clients[user][roomid] = es
            t = Thread(target=self._enterRoom, args=(es, roomid, user))
            t.start()
            print("%s enter room success..." % str(user))
        time.sleep(1)  #等待进房记录更新

        #p.join()

    def leaveRoom(self, roomid, *userid):
        """close one or more leaveRoom date use socket for soa
		use it after enterRoom
		
		example:
		| leaveRoom | 1012021 | 39089058 |
		| leaveRoom | 1012021 | 39089058 | 39088973 | # two userids |
		"""
        for user in userid:
            self.sendcmd(self.clients[user][roomid], '{"cmd":202}')
            self.clients[user][roomid].close()

    def sendcmd(self, es, msg):
        #发送指令，暂不对外提供
        try:
            es.send(msg + '\r\n')
        except socket.error as msg:
            pass

    def queryRoomInfo(self, *userid):
        """用于校验进房是否成功，请勿单独调用
		"""
        # #查询socket
        res = []
        qs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            qs.connect((self.HOST, self.QUERYPORT))
            for user in userid:
                qs.send(
                    '{"commid":2224,"req":1,"sequence":"1234567","uid":"%s"}\r\n'
                    % user)
                res.append(qs.recv(1000))
        except socket.error as msg:
            print(msg)
        qs.close()
        return res


#测试代码
if __name__ == '__main__':
    t = tools_library()
    # t.enterRoom(1012021, 39089058)
    # t.leaveRoom(1012021, 39089058)
    # print(t.clients[39089058])
    # time.sleep(12)
    t.queryRoomInfo(39089058)
