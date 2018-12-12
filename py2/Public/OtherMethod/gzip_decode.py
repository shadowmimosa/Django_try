#coding=utf-8
import base64
import StringIO, gzip


#将data数据以base64进行解码
def base64Code(data):
	data1=base64.decodestring(data)
	return data1


#将data数据以gzip进行解压
def gzipCode(data) :
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()
    return data2

#将data字符串以utf-8形式输出
def printUTF(data):
	str(data)
	print data.decode('utf-8')