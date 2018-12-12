#coding=utf-8
#脚本作用：公共json数据校验方法，遍历data数据，判断指定的字段是否在实际的返回中存在。



import logging
import json
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')


logging.basicConfig(level=logging.INFO)

data=[{"songId": 8269,
     "singerId": 5785,
    "hash": "A31F9FBFC5E73AA93CBF7EC1C6247A98",
     "recomflag": 5,
     "singerName": "1",
     "singerImg": "20140117151145992387.jpg",
    "startTime": 75000,
     "climaxHash": "B349729F8E040F849C532C904B2A4C22",
     "krc": "jj"},

    [{"songId": 8269,
         "singerId": 5785,
        "hash": "A31F9FBFC5E73AA93CBF7EC1C6247A98",
         "recomflag": 5,
         "singerName": "1",
         "singerImg": "20140117151145992387.jpg",
        "startTime": 75000,
         "climaxHash": "B349729F8E040F849C532C904B2A4C22",
         "krc": "jj"}]]


test=['songId',  'hash', 'singerId']



def verfication_Field(data,test,msg=None):
    '''
    1、验证传入的参数，如果为字典，则遍历字典中的各个key，再校验各个key对应的value值，如果为字符串型，则校验字符串为非空，如果为整型，则校验字符串>=0
    2、如果传入的参数为列表，则将列表中各个参数取出，如果列表中各个参数为字典，处理方法参照第1步。
    3、入参格式: Verfication Field	${data}	[parm1,parm2,parm3...]
    '''
    # print "传入data的类型为:%s"%type(data)

    if type(data)==list:
    	pass
    elif type(data)==dict:
    	pass
    else:
    	data=json.loads(data)

    if type(test)!=list:
       test=unicodeConvList(test)


    if isinstance(data,dict):

        logging.info("---基本信息获取---".decode('utf-8'))
        logging.info("传入的data为dict字典对象!".decode('utf-8'))
        logging.info(('传入过来的dict对象主key的长度：%s'%len(data)).decode('utf-8'))
        keys=data.keys()
        # logging.info(keys)

        logging.info('---开始进行字段校验---'.decode('utf-8'))
        listContain(test,keys)
        # #定义变量，计算遍历次数
        times=0
        for key,value in data.iteritems():
            times=times+1
            logging.info("")
            logging.info(("---传入的data数据，第%s对象元素,key值对应为:%s---"%(times,key)).decode('utf-8'))
            logging.info(('%s:%s' % (key, value)).decode('utf-8'))
            analysis_subItem(value,msg)

    elif isinstance(data,list):
           logging.info("---基本信息获取---".decode('utf-8'))
           logging.info("传入的data为list列表对象!".decode('utf-8'))
           logging.info(('传入过来的list列表对象的长度：%s'%len(data)).decode('utf-8'))

           logging.info('---开始进行字段校验---'.decode('utf-8'))

           data_list_len=len(data)
           # logging.info('%s对应值的类型为list且长度为%s'%(data,data_list_len))
           for i in range(data_list_len):
               # logging.info("")
               logging.info(("--传入的data数据，列表中第%s个子元素"%(i+1)).decode('utf-8'))
               analysis_subItem(data[i],test,msg)

    else:
        logging.info(("传入的data数据不是dict或者list对象").decode('utf-8'))


#判断两个列表中的值是否相等，且将不相等的值提取出来
def listContain(list1,list2):
     error=[]
     logging.info(("指定检测字段个数为:%s"%len(list1)).decode('utf-8'))
     logging.info(("指定检测字段分别为：%s"%list1).decode('utf-8'))
     logging.info(("实际获取到的字段个数为:%s"%len(list2)).decode('utf-8'))
     logging.info(("实际获取到的字段分别为:%s"%list2).decode('utf-8'))

     for i in list1:
        if i in list2:
            logging.info(("被检测的字段【%s】在实际返回的列表字段:%s中"%(i,list2)).decode('utf-8'))
            continue
        else:
            error.append(i)
     if error:
         for i in xrange(len(error)):
            logging.info(("请注意,被检测的字段【%s】不在实际返回的列表字段:%s中,请检查!"%(error[i],list2)).decode('utf-8'))
         raise RuntimeError(("在实际返回中，不存在的字段为:%s"%error).decode('utf-8'))


#将unicode字符串转换成list列表，保证从RF中传入的参数为列表
def unicodeConvList(data):
    if type(data)!=list:

        test_list=[]
        test_str=str(data)
        test_str_list= test_str.split(',')

        for i in xrange(len(test_str_list)):

            if '[' in test_str_list[i] and ']' in test_str_list[i]:
                  test_list.append(test_str_list[i].replace('[','').replace(']',''))

            elif '[' in test_str_list[i]:
                test_list.append(test_str_list[i].replace('[',''))

            elif ']' in test_str_list[i]:
                test_list.append(test_str_list[i].replace(']',''))

            else:
                test_list.append(test_str_list[i])

        return test_list


#判断value值对应的类型，从而进行相应的处理，嵌入递归函数
def analysis_subItem(item,test,msg):
    '''
    1、不管value值取出如何，最终还是拆解成最小单元，字符串或者是整型来进行判断
    :return:
    '''
    if isinstance(item,str):
        if get_length(item) == 0:
            raise AssertionError(msg or "'%s' should not be empty." % str)
    elif isinstance(item,int):
        if int(item)<0:
            raise AssertionError("当前int型获取到的数字小于等于0".decode('utf-8'))

    elif isinstance(item,list):
           value_list_len=len(item)
           logging.info(('%s对应值的类型为list且长度为%s'%(item,value_list_len)).decode('utf-8'))
           for i in range(value_list_len):
               logging.info("")
               logging.info(("内嵌的列表中，第%s个子元素"%(i+1)).decode('utf-8'))
               analysis_subItem(item[i],test,msg)

    elif isinstance(item,dict):
           value_dict_len=len(item)
           logging.info(('%s对应值的类型为dict且长度为%s'%(item,value_dict_len)).decode('utf-8'))
           subkey=item.keys()
           listContain(test,subkey)
           times=0
           for subkey,subvalue in item.iteritems():
                times=times+1
                logging.info("")
                logging.info(("---内嵌的字典中,第%s对象元素,key值对应为:%s---"%(times,subkey)).decode('utf-8'))
                logging.info(('%s:%s' % (subkey, subvalue)).decode('utf-8'))
           
                analysis_subItem(subvalue,msg)


#计算字符串长度
def get_length(item):
        length = _get_length(item)
        logging.info('Length is %d' % length)
        logging.info("")
        return length

def _get_length(item):
        try:
            return len(item)

        except:
            raise RuntimeError("Could not get length of '%s'." % item)



if __name__ == '__main__':
    verfication_Field(data,test)

