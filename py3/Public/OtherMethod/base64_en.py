#coding=utf-8
#base64加密解密工具
import base64
import StringIO, gzip
import sys,os


#将data数据以base64进行解码
def base64Code(data):
    data1=base64.decodestring(data)
    return data1


#将data数据以base64进行编码
def base64ENCode(data):
    data1=base64.b64encode(data)
    return data1

#数据是gzip解码
def gzipCode(data) :
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()
    return data2

#数据是gzip压缩
def gzipEncode(data) :
    uncompressedstream = StringIO.StringIO()
    gziper = gzip.GzipFile(mode="wb",fileobj=uncompressedstream)
    try:
        gziper.write(data)
    finally:
        gziper.close()
    data2=uncompressedstream.getvalue()
    return data2


def data_Dencode(data):
    #接口数据解密方法:先base64解密，再进行gzip解压
    data_base64=base64Code(data)
    data_gzip=gzipCode(data_base64)
    # print data_gzip
    data_gzip_len=len(data_gzip)
    print u"total:",data_gzip_len

    fopen=open("c:\decode.txt","w")
    fopen.write(data_gzip)
    fopen.close()
    print "decode file location:c:\decode.txt"

def data_Encode(data):
    #接口数据加密方法:先gzip压缩，再用base64加密
    data=str(data)
    data=gzipEncode(data)
    data_base64=base64ENCode(data)
    fopen=open("c:\encode.txt","w")
    fopen.write(data_base64)
    fopen.close()
    print "encode file location c:\encode.txt"


if __name__ == '__main__':
    if sys.argv[1]=="1":
        try:
          fopen=open(os.getcwd()+"\encode.txt","r")
          data=fopen.read()
          data_Dencode(data)
        except:
          print "file open or Dencode error !"
        finally:
          fopen.close()

    elif sys.argv[1]=="2":
      try:
        fopen=open(os.getcwd()+"\decode.txt","r")
        data=fopen.read()
        data_Encode(data)
      except:
        print "file open or encode error !"
      finally:
        fopen.close()
    else:
        print sys.argv[1]
        print "error!"