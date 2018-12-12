# 脚本作用：公共json数据校验方法，遍历data数据，校验字符串及整型数值

import logging
import json

logging.basicConfig(
    level=logging.DEBUG,  #控制台打印的日志级别
    filename='new.log',
    filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
    #a是追加模式，默认如果不写的话，就是追加模式
    format=
    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    #日志格式
)


def verfication_data(data, msg=None):
    '''
    1、验证传入的参数，如果为字典，则遍历字典中的各个key，再校验各个key对应的value值，
    如果为字符串型，则校验字符串为非空，如果为整型，则校验字符串大于等于0
    2、如果传入的参数为列表，则将列表中各个参数取出，如果列表中各个参数为字典，处理方法
    参照第1步。
    '''

    if type(data) == list:
        pass
    elif type(data) == dict:
        pass
    # elif type(data)==unicode:
        # logging.info(("---传入的data数据分析完成-11----"))
    else:
        data = json.loads(data)
        ##logging.info(("---传入的data11为%s----"%(data)))

    if isinstance(data, dict):

        logging.info("---基本信息获取---")
        logging.info("传入的data为dict对象!")
        logging.info(('传入过来的dict对象key的数量为：%s' % len(data)))
        keys = data.keys()
        logging.info(("----data对象key分别为%s---" % (keys)))
        logging.info('---开始进行校验data_dict---')
        #data_dict_len=len(data)
        #定义变量，计算遍历次数
        times = 0
        for key, value in data.items():
            times = times + 1
            logging.info("")
            logging.info(("---传入的data数据，第%s项,key值对应为:%s---" % (times, key)))
            logging.info(('%s:%s' % (key, value)))
            # if times==data_dict_len:
            # logging.info(("---传入的data_dict数据分析完成-----"))
            # break
            # else:
            analysis_subItem(value, msg)

    elif isinstance(data, list):
        logging.info("---基本信息获取---")
        logging.info("传入的data为list对象!")
        logging.info(('传入过来的list对象的长度：%s' % len(data)))

        logging.info('---开始进行校验data_list---')

        data_list_len = len(data)
        logging.info('%s对应值的类型为list且长度为%s' % (data, data_list_len))
        for i in range(data_list_len):
            logging.info("")
            logging.info(("--传入的data数据，第%s个子元素" % (i + 1)))
            analysis_subItem(data[i], msg)

    else:
        logging.info(("传入的data数据不是dict或者list对象"))
        logging.info(("---传入的data22为%s----" % (data)))


#判断value值对应的类型，从而进行相应的处理，嵌入递归函数
def analysis_subItem(item, msg):
    '''
    1、不管value值取出如何，最终还是拆解成最小单元，字符串或者是整型来进行判断
    :return:
    '''
    if isinstance(item, str):
        if get_length(item) == 0:
            print('str should not be empty.')
            pass
            # raise AssertionError(msg or "'%s' should not be empty." % str)
        else:
            logging.info(("---item==%s-----" % (item)))
    elif isinstance(item, int):
        if int(item) < 0:
            raise AssertionError("当前int型获取到的数字小于0")
        else:
            logging.info(("---item==%s-----" % (item)))

    elif isinstance(item, list):
        value_list_len = len(item)
        logging.info(('%s对应值的类型为list且长度为%s' % (item, value_list_len)))
        for i in range(value_list_len):
            logging.info("")
            logging.info(("内嵌的列表中，第%s个子元素" % (i + 1)))
            analysis_subItem(item[i], msg)

    elif isinstance(item, dict):
        value_dict_len = len(item)
        logging.info(('%s对应值的类型为+dict且长度为%s' % (item, value_dict_len)))
        ids = 0
        for subkey, subvalue in item.items():
            ids = ids + 1
            logging.info("")
            logging.info(("---内嵌的字典中,第%s项,subkey对应为:%s---其值为%s---" %
                          (ids, subkey, subvalue)))
            logging.info(('{"%s":"%s"}' % (subkey, subvalue)))
            # if ids==value_dict_len:
            # logging.info(("---传入的item-dict数据分析完成-----"))
            # break
            # else:
            analysis_subItem(subvalue, msg)


#将unicode字符串转换成list列表，保证从RF中传入的参数为列表


#计算字符串长度
def get_length(item):
    length = _get_length(item)
    logging.info('Length is %d' % length)
    logging.info("")
    print('This is ')
    return length


def _get_length(item):
    try:
        return len(item)

    except:
        raise RuntimeError("Could not get length of '%s'." % item)


if __name__ == '__main__':
    # verfication_data(data)
    pass