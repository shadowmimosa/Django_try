#coding=utf-8
#脚本作用：公共json数据校验方法，遍历data数据，判断指定的字段是否在实际的返回中存在。

import logging
import json

#logging.basicConfig(level=logging.INFO)


def CheckField(data, test, ignore=None):
    '''
    1、验证传入data 中没有包括test中必须存在的字段；
    2、data可以为列表 字符串、字典；test为字符串表示要检查的字段名，多个字段名用逗号分隔,如fid,sid
    3、ignore 参数当为非空时，在验证不通过时不会报错，会返回0，ignore为空时，验证不通过会失败报错！
    3、入参格式: CheckField     ${data}      field1,field2    1
    '''
    # print "传入data的类型为:%s"%type(data)

    if type(data) == list:
        pass
    elif type(data) == dict:
        pass
    else:
        data = json.loads(data)

    if type(test) != list:
        test = unicodeConvList(test)
        logging.info(test)
    list2 = []
    list2 = analysis_subItem(data, list2)
    logging.info(list2)
    yesNo = listContain(test, list2)
    if yesNo:
        print("Oh,yes! This is PASS!!")
        return yesNo
    else:
        if ignore:
            return yesNo
        raise AssertionError("my god! It is Fail !!".decode('utf-8'))


#判断两个列表中的值是否相等，且将不相等的值提取出来
def listContain(list1, list2):
    error = []
    ispas = 1
    for i in list1:
        if i in list2:
            continue
        else:
            error.append(i)
    if error:
        ispas = 0
        for i in range(len(error)):
            logging.info(("非常遗憾！！在【目标list1字段集】中未发现list2中的【%s】字段！！！" %
                          (error[i])).decode('utf-8'))
            pass
    return ispas


#将unicode字符串转换成list列表，保证从RF中传入的参数为列表
def unicodeConvList(data):
    if type(data) != list:

        test_list = []
        test_str = str(data)
        test_str_list = test_str.split(',')

        for i in range(len(test_str_list)):

            if '[' in test_str_list[i] and ']' in test_str_list[i]:
                test_list.append(test_str_list[i].replace('[', '').replace(
                    ']', ''))

            elif '[' in test_str_list[i]:
                test_list.append(test_str_list[i].replace('[', ''))

            elif ']' in test_str_list[i]:
                test_list.append(test_str_list[i].replace(']', ''))

            else:
                test_list.append(test_str_list[i])

        return test_list


#判断value值对应的类型，从而进行相应的处理，嵌入递归函数
def analysis_subItem(item, test):
    '''
    1、不管value值取出如何，最终还是拆解成最小单元，字符串或者是整型来进行判断
    :return:
    '''
    if isinstance(item, str):
        pass
    elif isinstance(item, int):
        if int(item) < 0:
            raise AssertionError("当前int型获取到的数字小于等于0".decode('utf-8'))

    elif isinstance(item, list):
        value_list_len = len(item)
        for i in range(value_list_len):
            analysis_subItem(item[i], test)

    elif isinstance(item, dict):
        value_dict_len = len(item)
        # logging.info(('%s对应值的类型为dict且长度为%s'%(item,value_dict_len)).decode('utf-8'))

        for key, value in item.items():
            test.append(key)
            analysis_subItem(value, test)
    return test


#计算字符串长度
def get_length(item):
    length = _get_length(item)
    # logging.info('Length is %d' % length)
    # logging.info("")
    return length


def _get_length(item):
    try:
        return len(item)

    except:
        raise RuntimeError("Could not get length of '%s'." % item)


if __name__ == '__main__':
    data1 = [{
        "songId": 8269,
        "singerId": 5785,
        "hash": "A31F9FBFC5E73AA93CBF7EC1C6247A98",
        "recomflag": 5,
        "singerName": "1",
        "singerImg": "20140117151145992387.jpg",
        "startTime": 75000,
        "climaxHash": "B349729F8E040F849C532C904B2A4C22",
        "krc": "jj"
    },
             [{
                 "songId": 8269,
                 "singerId": 5785,
                 "hash": "A31F9FBFC5E73AA93CBF7EC1C6247A98",
                 "recomflag": 5,
                 "singerName": "1",
                 "singerImg": "20140117151145992387.jpg",
                 "startTime": 75000,
                 "climaxHash": "B349729F8E040F849C532C904B2A4C22",
                 "krc": "jj"
             }]]

    test1 = ['songId', 'hash', 'singerId']
    CheckField(data1, test1)
