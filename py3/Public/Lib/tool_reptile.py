# It is reptile;信息清洗方法集合

import re
import json


def convertCode(dataobj, encodingtype, datatypes=None):
    if encodingtype:
        print("The 'encodingtype' is no longer required!")
    if datatypes in ["List", "list", "LIST", None]:
        try:
            dataobj1 = json.dumps(
                dataobj, ensure_ascii=False)  # , encoding=encodingtype)
            print(dataobj1)
            print(type(dataobj1))
            print("完成转码")
            dataobj = json.loads(dataobj1)
            print(type(dataobj))
        except UnicodeEncodeError:
            try:
                dataobj = json.dumps(
                    dataobj, ensure_ascii=False)  # , encoding=encodingtype)
                print("未完成转码")
            except:
                pass
            pass
    print("dataobj类型为", type(dataobj))
    return dataobj


def Dict_sorted(scrdict, type=None):
    '''
    ``param scrdict``: 源字典类型的参数; \n 
    ``param type``: 排序类型，None为不排序返回；\n
    1为key的升序排序，2代表按key的降序排序，3代表按value的升序排序,4代表按value的降序排序，其他不排序返回列表嵌套列表\n
    ``return``: 返回列表类型参数；\n
    匹配到返回列表嵌套元组[(key1,value1),(key2,value2)...]；\n
    未匹配到返回列表嵌套列表[[key1,value1],[key2,value2]...]
    '''
    print("  input:type:【%s】,\n  scrdict:【%s】" % (type, scrdict))
    if type in ['3', 3]:
        print("  type为【%s】,则按Value升序排序" % type)
        orderlist = sorted(scrdict.items(), key=lambda d: d[1])
        print("  【%s】" % orderlist)
    elif type in ['4', 4]:
        print("  type为【%s】,则按Value降序排序" % type)
        orderlist = sorted(scrdict.items(), key=lambda d: d[1], reverse=True)
        print("  【%s】" % orderlist)
    elif type in ['2', 2]:
        print("  type为【%s】,则按key降序排序" % type)
        orderlist = sorted(scrdict.items(), key=lambda d: d[0], reverse=True)
        print("  【%s】" % orderlist)
    elif type in ['1', 1]:
        print("  type为【%s】,则按Key升序排序" % type)
        orderlist = sorted(scrdict.items(), key=lambda d: d[0])
        print("  【%s】" % orderlist)
    else:
        print("  type为【%s】,未匹配到类型,返回列表嵌套列表" % type)
        orderlist = []
        for keyscr in scrdict.keys():
            #print(  keyscr,scrdict.get(keyscr))
            kvlist = [keyscr, scrdict.get(keyscr)]
            #print(  kvstring)
            orderlist.append(kvlist)
        print("  【%s】" % orderlist)
    return orderlist


def Json_to_Dict(scrdata):
    """
    :param scrdata类型为dict时，以json字符串输出，类型为json字符串时，以字典类型输出；
    """
    if type(scrdata) == dict:
        print("源变量为dict类型,将转为字符str类型")
        DictJson = json.dumps(scrdata)
        print("转化后的类型为", type(DictJson))
        print(DictJson)
    elif type(scrdata) == str:
        print("源变量为Json str类型,将转为字典dictionary类型")
        DictJson = json.loads(scrdata)
        print("转化后的类型为", type(DictJson))
        print(DictJson)
    else:
        print("非字典dictionary和json字符str类型")
        DictJson = scrdata
    return DictJson


def funfilter(srcobj, conditionstr):
    print("funfilter start ...")
    conditionlist = list()
    condition = conditionstr
    if "And" in conditionstr:
        conditionlist = conditionstr.split(" And ")
    elif "OR" in conditionstr:
        conditionlist = conditionstr.split(" OR ")
    else:
        conditionlist.append(conditionstr)
    print("条件列表为：")
    print(conditionlist)
    i = 1
    for condition in conditionlist:
        #(yuanstring, leftlimit, rightlimit, ORD=None, valuetype=None, pt=None):
        if "==" in condition:
            filter = FindAndValue(condition, None, "==", 1, "Gen")
        elif "<=" in condition:
            filter = FindAndValue(condition, None, "<=", 1, "Gen")
        elif ">=" in condition:
            filter = FindAndValue(condition, None, ">=", 1, "Gen")
        elif "!=" in condition:
            filter = FindAndValue(condition, None, "!=", 1, "Gen")
        elif "!=" in condition:
            filter = FindAndValue(condition, None, "!=", 1, "Gen")
        elif "<" in condition:
            filter = FindAndValue(condition, None, "<", 1, "Gen")
        elif ">" in condition:
            filter = FindAndValue(condition, None, ">", 1, "Gen")
        else:
            filter = "1=1"
        filter = filter.replace("\"", "")
        print(u"条件解析的第%s个条件为%s" % (i, condition))
        #print(  "condition=",condition)
        print("字段为", filter)
        i = i + 1
        if type(srcobj) == list:
            objlen = len(srcobj)
            if objlen <= 0:
                print("没有符合要求的数据")
                srcobj = list()
            else:
                print("objlen=", objlen)
                korder = 0
                print("korderN进入for之前=", korder)
                for indexN in range(0, objlen):
                    print("indexN=", indexN)
                    srcobj_n = srcobj[korder]
                    print(srcobj_n)
                    if type(srcobj_n) == dict:
                        filtersValue = srcobj_n.get(filter)
                    else:
                        findValue = FindAndValue(srcobj_n, filter, "[,|}|)]",
                                                 1)
                        if findValue == None:
                            filtersValue = "00000"
                        else:
                            filtersValue = findValue
                        filtersValue = filtersValue.replace("\"", "")
                    #print(  "filtersValue=", filtersValue)
                    #print(   "type(condition)=",type(condition))
                    #print(   "type(filter)=", type(filter))
                    #print(   "type(filtersValue)=", type(filtersValue))
                    if type(filtersValue) == int:
                        #当值为int类型时，不能用replace来处理，要先转为字符类型；
                        filtersValue = str(filtersValue)
                    conditionx = condition.replace(filter, filtersValue)
                    if '!=' in conditionx:
                        conditionx=conditionx.replace('!=','!=')
                    print("conditionx=", conditionx)
                    print("eval(conditionx)=", eval(conditionx))
                    if eval(conditionx) == False:
                        print("不符合条件%s，移除此项" % condition)
                        print("处理前：%s" % srcobj)
                        srcobj.remove(srcobj_n)
                        print("列表取值序号korder保持不变=", korder)
                        print(u"第%s轮的%d次scrobj处理后：%s" % (i - 1, indexN + 1,
                                                         srcobj))
                    else:
                        korder = korder + 1
                        print("列表取值序号korder增加1=", korder)
                        print("%s 符合条件" % srcobj_n)
                        print("condition为", condition)
                        print(
                            u"第%s轮的%d次scrobj为%s" % (i - 1, indexN + 1, srcobj))

        else:
            print("请将源数据转换为列表格式")
    print("条件表达式为", conditionstr)
    print("funfilter返回的结果为", srcobj)
    print("funfilter End ...")
    return srcobj


def FindAndValue(yuanstring,
                 leftlimit,
                 rightlimit,
                 ORD=None,
                 valuetype=None,
                 pt=None):
    '''
    通过左右边界来筛选数据,返回列表或字符类型的值，没有符合条件的返回None；
    :param yuanstring: 为源字符串
    :param leftlimit: 为左边界字符串
    :param rightlimit: 为右边界字符串
    :param ORD: 为在查询结果中取第几个值，整数和All，All与0表示返回列表，Num，Count为返回找到的个数,
                基他整数表示返回值列表第N个值，超过列表值个数取最后的值；
    :param valuetype: 表示筛选规则（即取值字符串的类型），为空时，默认json格式除换行符外所有字符，
                json整型int，json大小字母字符串str,json正负小数点数字num,
                json网络连接为url,通用类型gen为除换行符外所有字符,支持非json取值,其他类型为自定义类型
    :param pt: 表示自定义类型的正则表达示，只有当valuetype为自定义类型才会用到，其他类型不用传
    :return:返回列表或字符串，如没有符合条件的返回None
            常用正则表达示的特殊字符用法介绍：0|9  表示0或9；.表示匹配除“\\n”之外的任何单个字符;
            +表示匹配前面的子表达式一次或多次；*匹配前面的子表达式零次或多次；[a-zA-Z0-9]表示0至9数字和大小字母;
            ?匹配前面的子表达式零次或一次；{n}n是一个非负整数。匹配确定的n次；{n,}n是一个非负整数。至少匹配n次;
            ?当该字符紧跟在任何一个其他限制符（*,+,?，{n}，{n,}，{n,m}）后面时，匹配模式是非贪婪的。
            非贪婪模式尽可能少的匹配所搜索的字符串，而默认的贪婪模式则尽可能多的匹配所搜索的字符串。
            例如，对于字符串“oooo”，“o+?”将匹配单个“o”，而“o+”将匹配所有“o”。
    '''
    _leftlimit = leftlimit
    _rightlimit = rightlimit
    if valuetype == None:
        print("默认取值:从json串取除\\n外的所有字符类型字符串")
        _pattern = "\":(.*?)"
        if _leftlimit != None:
            _pattern = _leftlimit + _pattern
        if _rightlimit != None:
            _pattern = _pattern + _rightlimit
    elif valuetype in [
            'num', 'number', 'NUM', 'Num', 'Number', 'DATA', 'data', 'Data'
    ]:
        print("从json串取数字(包括小数和负数)的字符串")
        _pattern = "\":\"([-0-9.]+)\""
        if _leftlimit != None:
            _pattern = _leftlimit + _pattern
        if _rightlimit != None:
            _pattern = _pattern + _rightlimit
    elif valuetype in ['int', 'INT', 'Int', 'Long', 'long', 'LONG']:
        print("从json串取整型（数字）的字符串")
        _pattern = "\":([0-9]+)"
        if _leftlimit != None:
            _pattern = _leftlimit + _pattern
        if _rightlimit != None:
            _pattern = _pattern + _rightlimit
    elif valuetype in ['char', 'string', 'str', 'Char', 'Str', 'CHAR', 'STR']:
        print("从json串取字母类型的字符串")
        _pattern = "\":\"([a-zA-Z]+)\""
        if _leftlimit != None:
            _pattern = _leftlimit + _pattern
        if _rightlimit != None:
            _pattern = _pattern + _rightlimit
    elif valuetype in ['url', 'URL', 'Url']:
        print("从json串取URL类型字符串")
        _pattern = "\":\"([a-zA-z]+://[^\\s]+?)\""
        if _leftlimit != None:
            _pattern = _leftlimit + _pattern
        if _rightlimit != None:
            _pattern = _pattern + _rightlimit
    elif valuetype in ['gen', 'GEN', 'Gen']:
        print("通用取值除\\n外所有字符，支持非json字符串取值")
        _pattern = "(.*?)"
        if _leftlimit != None:
            _pattern = _leftlimit + _pattern
        if _rightlimit != None:
            _pattern = _pattern + _rightlimit
    else:
        print("未匹配到类型，为自定义类型,匹配的规则为", pt)
        _pattern = pt
        if _leftlimit != None:
            _pattern = _leftlimit + _pattern
        if _rightlimit != None:
            _pattern = _pattern + _rightlimit
    print("正则表达示：", _pattern)
    _compile_pattern = re.compile(_pattern)
    print("编译的正则表达示为", _compile_pattern.pattern)
    returnList = re.findall(_compile_pattern, yuanstring, 0)
    print("符合条件的信息列表:", returnList)
    listlen = len(returnList)
    print("符合条件共:", listlen)
    if ORD == None:
        print("ORD为None,默认给值为1:")
        _orderid = 1
        print("取值序号为:", _orderid)
    elif ORD in ['count', 'num', 'Count', 'Num', 'COUNT']:
        print("ORD为%s,将统计个数返回:" % ORD)
        _orderid = 'COUNT'
    else:
        _orderid = ORD
        print("取值序号为:", _orderid)
    if listlen == 0:
        print("没有符合的信息,返回None")
        RT = None
    elif _orderid == 'COUNT':
        print("返回类型为%s,返回查找符合要求的个数" % _orderid)
        RT = listlen
    elif _orderid in ['ALL', 'all', 'All', '0', '', 0]:
        print("返回整个列表")
        RT = returnList
    else:
        if int(_orderid) > 0:
            num = int(_orderid) - 1
        else:
            num = int(_orderid)
        if listlen - num > 0 and listlen + num >= 0:
            print("取值序号正常,取列表下标为:", num)
            returnstring = returnList[num]
        else:
            print("取值序号过大,自动容错为取列表最后的值,取列表下标为:", listlen - 1)
            returnstring = returnList[listlen - 1]
        RT = returnstring
    print("Return Value:", RT)
    return RT


def pyfilter(srcobjs, condition, spitstring=None):
    """

    :param srcobj: 原数据，可以为字符类型和列表类型 因RF输入的参数都为Unicode类型，在RF中引用要用list,str强转类型； /r/n

    :param condition: 过滤条件,支持==,>=,<=,!=,!=,>,<,连接符暂只支持And; 比如 a>10 And b!=0 And "C"=="abcdef"  /r/n

    :param spitstring: 当srcobj为字符类型，此字段为分割符或分割字符,默认为},{   ; srcobj为dict不用传,/r/n

    :return: 返回list,无结果返回空list/r/n

    例如：/r/n

        e="[{\"b\":7,\"c\":\"ab\",\"a\":1},{\"b\":9,\"c\":\"4a6\",\"a\":12},{\"b\":9,\"c\":\"4a6\",\"a\":112}]"   /r/n

        d = pyfilter(e,"b>=9 And \"c\"==\"4a6\" And a!=112","c")

    """

    print("pyfilter start ...")
    srcobj = srcobjs
    print(type(srcobjs))
    if type(srcobj) == list:
        resrobj = funfilter(srcobj, condition)
    elif type(srcobj) == str:
        if spitstring == None:
            spitstrings = "}Joyrunzzqsplitstring{"
            if "}, {" in srcobj:
                srcobj = srcobj.replace("}, {", spitstrings)
            if "},{" in srcobj:
                srcobj = srcobj.replace("},{", spitstrings)
        else:
            spitstrings = spitstring + "Joyrunzzqsplitstring" + spitstring
            srcobj = srcobj.replace(spitstring, spitstrings)
        srclist = srcobj.split("Joyrunzzqsplitstring")
        print("切割前的srcobj为", srcobj)
        print('srclist列表为', srclist)
        resrobj = funfilter(srclist, condition)
    else:
        resrobj = "请将原数据转为字符类型或列表类型"
    print("pyfilter结果为:", resrobj)
    print("pyfilter End ...")
    return resrobj


# 测试代码
if __name__ == '__main__':
    # a = FindAndValue("[{\"ret\":11111},{\"ret\":2222},{\"ret\":\"ab1cd_w\"}]","ret","}",'1',"int")
    b = Dict_sorted({"ret":"0","sid":"e8705bd983da43d98b9cc0963a78666d","lasttime":1533108241,"user":12345,"msg":"e1aa"},4)
    # data1 = "{\"b\":789,\"c\": 456,\"a\":123}"
    # data1 = {"b": 789, "c": 456, "a": 123}
    # c = Json_to_Dict(data1)
    # #print(  str.split.__doc__)
    # #e = [{"b":7,"c":"ab","a":1},{"b":9,"c":"4a6","a":12},{"b":78,"c":46,"a":13},{"b":781,"c":"416","a":123},{"b":7,"c":"6","a":913},{"b":78,"c":"46","a":93},{"b":79,"c":"56","a":13}]
    # e = "[{\"b\":7,\"c\":\"ab\",\"a\":1},{\"b\":9,\"c\":\"4a6\",\"a\":12},{\"b\":9,\"c\":\"4a6\",\"a\":112}]"
    # d = pyfilter(e, "b>=9 And \"c\"==\"4a6\" And a!=112", "c")

   # #print( Dict_sorted.__doc__,pyfilter.__doc__)