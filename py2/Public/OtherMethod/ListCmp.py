#coding=utf-8

list1=[0,0,1,0,0]
list2=[66,55,33,22,11]

#判断指定列表是按降序还是升序排列，当reverse为True时，则为升序，为False为降序

def listCmp(list1,reverse):
    list1_len=len(list1)
    if reverse==True:
        for i in xrange(list1_len):
            if i==list1_len-1:
                break
            elif list1[i]<=list1[i+1]:
                continue
            else:
                raise AssertionError("列表中共【%s】个元素，升序校验时，第【%s】个元素，即下标为【%s】的位置对应的数小于前面的数，当前值为:【%s】,而前一个数为：【%s】,"%(list1_len,i+2,i+1,list1[i+1],list1[i]))

    elif reverse==False:
        for i in xrange(list1_len):
            if i==list1_len-1:
                break
            elif list1[i]>=list1[i+1]:
                continue
            else:
                 raise AssertionError("列表中共【%s】个元素，降序校验时，第【%s】个元素,即下标为【%s】的位置对应的数大于前面的数，当前值为:【%s】,而前一个数为：【%s】"%(list1_len,i+2,i+1,list1[i+1],list1[i]))

# listCmp(list1,True)
# listCmp(list1,True)