import random
import time
import logging
import os
import re
import json
import sys
import base64
from io import StringIO
import gzip
import string
import uuid

#作用：公共函数库


##获取当前的目录
def Get_pwd():
    ostype = sys.platform  #获取当前系统类型
    print('os type is:', ostype)
    if ostype == 'win32' or ostype == 'win64':
        pwd = os.popen('cd').readlines()[0]
        print('Path  is:', pwd)
    else:
        pwd = os.popen('pwd').readlines()[0]
        print('Path  is:', pwd)
    pwd = pwd.replace('\n', '')
    return pwd


#从两个列表中，提取相同的值，并作为一个新的列表返回
def Get_Duplicates_List(list1, list2):
    list_new = []
    for i in list1:
        if i in list2:
            list_new.append(i)
    return list_new


#从列表中随机取值并返回
def choiceValue(list1):
    value = random.choice(list1)
    return value


#去掉字符串开头与结尾的双引号
def stripStr(teststr):
    teststr = teststr.strip('\"')
    return teststr


#去掉字符串开头与结尾的单引号
def stripStrSingle(teststr):
    teststr = teststr.strip("\'")
    return teststr


#判断某个值是否在指定的列表中，如果在返回True，否则返回False
def ListContainValue(value1, list1):

    for i in list1:
        if str(i) == str(value1):
            return True
        else:
            continue
    return False


#判断指定列表是按降序还是升序排列，当reverse为True时，则为升序，为False为降序
def listCmp(list1, reverse):
    list1_len = len(list1)
    reverse = str(reverse)
    if reverse == 'True':
        for i in range(list1_len):
            if i == list1_len - 1:
                break
            elif int(list1[i]) <= int(list1[i + 1]):
                continue
            else:
                return "列表中共【%s】个元素，升序[小到大]校验时，第【%s】个元素，即下标为【%s】的位置对应的数小于前面的数，当前值为:【%s】,而前一个数为：【%s】," % (
                    list1_len, i + 2, i + 1, list1[i + 1], list1[i])
                raise AssertionError(
                    "列表中共【%s】个元素，升序[小到大]校验时，第【%s】个元素，即下标为【%s】的位置对应的数小于前面的数，当前值为:【%s】,而前一个数为：【%s】,"
                    % (list1_len, i + 2, i + 1, list1[i + 1], list1[i]))

    elif reverse == 'False':
        for i in range(list1_len):
            if i == list1_len - 1:
                break
            elif int(list1[i]) >= int(list1[i + 1]):
                continue
            else:
                return "列表中共【%s】个元素，降序[大到小]校验时，第【%s】个元素,即下标为【%s】的位置对应的数大于前面的数，当前值为:【%s】,而前一个数为：【%s】" % (
                    list1_len, i + 2, i + 1, list1[i + 1], list1[i])
                raise AssertionError(
                    "列表中共【%s】个元素，降序[大到小]校验时，第【%s】个元素,即下标为【%s】的位置对应的数大于前面的数，当前值为:【%s】,而前一个数为：【%s】"
                    % (list1_len, i + 2, i + 1, list1[i + 1], list1[i]))


#格式化时间戳，传入的时间戳格式化标准格式返回
def stampTime(stamptime):
    try:
        if len(str(stamptime)) == 10:
            pass
        else:
            stamptime = stamptime / 1000

        ltime = time.localtime(int(stamptime))
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
        return timeStr
    except:
        return None


#判断字符串是否为空，判断前，过滤单引号及双引号
def ShouldStringNotBeEmpty(str1):
    str1 = str1.strip('\"').strip('\'')
    if len(str1) == 0:
        raise AssertionError("%s传入字符串检验为空，请检查！" % str1)
    else:
        logging.info(str1)
        print("长度为【%d】个字符" % (len(str1)))


#写文件操作，通常用作临时外部存储
def writeFile(str1, name):
    file1 = open(name, "w")
    file1.write(str1)
    file1.close()


#读文件，配合写文件使用
def ReadFile(name):
    file1 = open(name, "r")
    str1 = file1.read()
    file1.close
    return str1


#向指定文件追加内容
def WriteAppendFile(str1, name):
    f1 = open(name, "a")
    f1.write(str(str1))
    f1.write("\n")
    f1.close()


#将指定的文件全部读取，写入到列表并返回
def ReadAllFile(name):
    result_choice = []
    f2 = open(name, "r")
    f2_content = f2.readlines()

    for line in f2_content:
        line = line.replace('\n', '')
        result_choice.append(line)

    f2.close()
    return result_choice


#判断指定文件是否存在，且文件内容是否为空,存在且内容不为空则返回True，反之返回False
def VerifyFileExist(name):
    if os.path.exists(name):
        f1 = open(name, "r")
        f1_len = len(f1.read())
        if f1_len != 0:
            return True
        else:
            return False
    else:
        return False


#功能：从返回的内容中提取json串。
#例如:结果返回为 callback({"songerid":123})，提取里面的json串
def getJsonData(response):
    #通过此正则表达式提取出所需的json串
    # jsonData=re.findall(r'\w+[(]{1}(.*)[)]{1}',response,re.S)[0]
    # jsonData=re.findall(r'\w[\x21-\x7e]+\((.*)\)',response,re.S)[0]   #增加[\x21-\x7e]匹配特殊字符如&符号，callbackjson&version=123&platform=({"songerid":123})等

    # if '{' in response and '(' not in response:
    #     jsonData = re.findall(r'.*[{}]{1}(.*)[}]{1}', response, re.S)[0]
    #     jsonData.center(len(jsonData)+2,'{')
    # elif '(' in response:
    #     jsonData = re.findall(r'.*[(]{1}(.*)[)]{1}', response, re.S)[0]  #匹配（）前任意字符

    jsonData = re.findall(r'.*[(]{1}(.*)[)]{1}', response, re.S)[0]  #匹配（）前任意字符
    jdict = json.loads(jsonData)

    return jdict


#将data数据以base64进行解码
def base64Code(data):
    # bype_string = bytes(data, 'utf-8')
    bype_string = data
    missing_padding = len(bype_string) % 4
    if missing_padding != 0:
        bype_string += b'=' * missing_padding
    return base64.decodestring(bype_string)


#将data数据以base64进行编码
def base64ENCode(data):
    bytes_string = data.encode(encoding="utf-8")
    data1 = base64.b64encode(bytes_string)
    return data1


#将data数据以gzip进行解压
def gzipCode(data):
    compressedstream = StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()
    return data2


#将data字符串以utf-8形式输出
def printUTF(data):
    str(data)
    print(data.decode('utf-8'))


#随机从某个取值范围获取整型数值，且在取值时，进行数字去重，之前已取过的，下次随机获取时，不再返回
def getRandomValue_Range(min, max):

    # `min` `max` 为关键字，尽量不使用
    # 为避免传参错误，参数名暂先保持不变
    min_num = min
    max_num = max

    result_choice = []

    f1 = open("id.pkl", "a")
    f2 = open("id.pkl", "r")
    f2_content = f2.readlines()

    for line in f2_content:
        line = line.replace('\n', '')
        result_choice.append(int(line))

    print(result_choice)

    if len(result_choice) >= (max_num - min_num + 1):
        print("所有数字已取完！")
        return None

    else:
        while (len(result_choice)) < max_num - min_num + 1:
            random_num = random.choice(range(min_num, max_num + 1))
            if random_num not in result_choice:
                f1.write(str(random_num))
                f1.write("\n")
                print("第%d次随机的数:%d" % (len(result_choice) + 1, random_num))
                f1.close()
                f2.close()
                return str(random_num)
            else:
                print("第%d次随机的数:%d,已重复，自动重新获取" % (len(result_choice) + 1,
                                                  random_num))
                continue

    f1.close()
    f2.close()


#随机从列表中获取数值，且在取值时，进行数据去重，之前已取过的，下次随机获取时，不再返回
def getRandomValue_List(list1):

    news_list = []
    for id in list1:
        if id not in news_list:
            news_list.append(id)

    print('去重后的新列表为:\n', news_list)

    list_len = len(news_list)

    result_choice = []

    f1 = open("id_list.pkl", "a")
    f2 = open("id_list.pkl", "r")
    f2_content = f2.readlines()

    for line in f2_content:
        line = line.replace('\n', '')
        result_choice.append(str(line))

    print(result_choice)

    if len(result_choice) >= list_len:
        print("列表中所有的值已取完！")

    else:
        while (len(result_choice)) < list_len:
            random_num = random.choice(news_list)

            if str(random_num) not in result_choice:
                f1.write(str(random_num))
                f1.write("\n")
                print("第%d次随机的值为:%s" % (len(result_choice) + 1, random_num))
                f1.close()
                f2.close()
                return str(random_num)

            else:
                print("第%d次随机的值为:%s,已重复，自动重新获取" % (len(result_choice) + 1,
                                                   random_num))
                continue

    f1.close()
    f2.close()


#生成随机字符串
def randomstr(bit=16):
    intbit = int(bit)
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    l = []
    for i in range(intbit):
        l.append(random.choice(seed))
    random_str = ''.join(l).replace(' ', '')
    return random_str


#扩展列表，将列表list2連接至list1上，并返回最終連接的列表
def extendList(list1, list2):
    list1.extend(list2)
    return list1


#扩展字典，将字典dcit1連接至dict2上，并返回最終連接的字典
def extendDict(dict1, dict2):
    dict3 = dict1.copy()
    dict3.update(dict2)
    return dict3


test = '<script>window.name={"code":0,"data":{"fxId":39097443,"kugouId":582326271,"success":true,"ticket":"016800FDCDCA8847C0C769059957BF5F22F267DFC155319A74F5B8B581BB4A5A464DE0DA364032C704B8008319A255E58D475A3C36407B30E589509E569CF4399C239948EB9EA3A7BF2AE939869EA6CD70FEC4FFC4BABEBB5BBEFFFAFD5308CC366F05ECC2EF3923EE0AD1"},"needCaptcha":0,"times":1458035189124};</script>'


#针对H5返回的JS脚本进行提取有效的数据
def getH5JsonData(response):
    #通过此正则表达式提取出所需的json串
    #先从取出window.name后的值
    jsonData = re.findall(r'\w+[window.name]=(.*)', response, re.S)[0]
    #取出除了;</script>以外的值
    jsonData = re.findall(r'(.*)(;</script>)', jsonData, re.S)[0][0]
    #去掉单引号
    jsonData = stripStrSingle(jsonData)
    #转换成字典对象
    jdict = json.loads(jsonData)
    print(jdict)
    return jdict


# print( getH5JsonData(test))


#传入索引号，从列表中取值
def getlist(list1, index):
    try:
        value = list1[index]
        return value
    except IndexError:
        print('List out index range. Please input index less than %s!' %
              len(list1))
        pass


#判断列表中所有的值是否都相等，如果相等，则返回True,方法一
def checkListEqual(lst):
    a = lst[1:]
    b = lst[:-1]
    c = a == b

    return lst[1:] == lst[:-1]


#判断列表中所有的值是否都相等，如果都相等，则返回True,方法二
def checkEqual2(iterator):
    return len(set(iterator)) <= 1


def listA_isEquel_listB(list1, list2):
    if list1 != list2:
        AssertionError("传入的两个列表不相等")


def stringbyequal(arglist):

    arglist = repr(arglist)
    pattern = re.compile('=')
    res = pattern.split(arglist, 1)
    res = res
    return res
