#coding=utf-8
import random
# import Get_UserId_list
# import Get_roomid_list
import pickle  
import tool_Libary

#功能：测试环境下，变量文件。（除环境url外，其它需使用到的外部变量均在此文件定义）


#**************************定义函数区******************************************
#随机选择版本号
def choiceVersion():
    version=random.randint(7000,8000)
    return str(version)


#随机获取线上环境UserId，提供两种方法，一种随机获取，一种根据下标获取
def choiceUserId(n):
    userid_list=Get_UserId_list.main()
    # print userid_list
    if n=="random":
        userid_random=random.choice(userid_list)
        return str(userid_random)
    elif isinstance(n,int):
        userid_random=userid_list[n]
        return str(userid_random)


#随机获取线上环境RoomId，提供两种方法，一种随机获取，一种根据下标获取
def choiceRoomId(n):
    roomid_list=Get_roomid_list.main()
    # print roomid_list
    if n=="random":
        roomid_list_random=random.choice(roomid_list)
        return str(roomid_list_random)
    elif isinstance(n,int):
        roomid_list_random=roomid_list[n]
        return str(roomid_list_random)


#随机获取测试环境指定的userid，提供两种方法，一种随机获取，一种根据下标获取
def choiceTest_UserId(n):
    '''
    关注mvcomment1帐号,对应userId为：39096439
    关注mvcomment1帐号,对应userId为：39096442
    关注fxapptest帐号,对应userid为: 39096701
    关注leq5566帐号, 对应userid为: 39095863
    '''
    userid_list=['39096439','39096442','39096701','39095863']
    # print userid_list
    if n=="random":
        userid_random=random.choice(userid_list)
        return str(userid_random)
    elif isinstance(n,int):
        userid_random=userid_list[n]
        return str(userid_random)


#随机获取测试环境指定的用户名，提供两种方法，一种随机获取，一种根据下标获取
def choiceTest_UserName(n):

    userName_list=['testfx01','mvcomment1','leq5566','mikezhou2026']
    # print userid_list
    if n=="random":
        userName_random=random.choice(userName_list)
        return str(userName_random)
    elif isinstance(n,int):
        userName_random=userName_list[n]
        return str(userName_random)


#随机从指定的歌手列表中获取关键字
def choiceSiner_list_keyword():
    choiceSiner_keyword=random.choice(singer_list)
    return choiceSiner_keyword


#随机从指定的歌曲列表中获取关键字
def choiceSong_list_keyword():
    choiceSong_keyword=random.choice(song_list)
    return choiceSong_keyword
#随机从指定的評論列表中获取关键字
def choiceComment_list_keyword():
    choiceComment_keyword=random.choice(comment_list)
    return choiceComment_keyword


#随机从某个取值范围获取整型数值，且在取值时，进行数字去重，之前已取过的，下次随机获取时，不再返回
def getRandomValue_Range(min,max):
    for i in xrange(max+1):
        result_choice=[]
        random_num=random.choice(range(min,max+1))

        f1=open("id.pkl","ab")
        f2=open("id.pkl","rb")
        f2_content=f2.readlines()

        for line in f2_content:
            line=line.replace('\n','')
            result_choice.append(int(line))
    
        print result_choice

        if i+1==max and len(result_choice)==max:
            print "所有数字已取完！"
            break

        if random_num not in result_choice:
            f1.write(str(random_num))
            f1.write("\n")
            print u"第%d次随机的数:%d"%(len(result_choice)+1,random_num)
            return str(random_num)

        else:
            print u"第%d次随机的数:%d,已重复，自动重新获取"%(len(result_choice)+1,random_num)
            continue


        f1.close()
        f2.close()


#随机从列表中获取数值，且在取值时，进行数据去重，之前已取过的，下次随机获取时，不再返回
def getRandomValue_List(list1):
	list1_len=len(list1)
	for i in xrange(list1_len+1):
		result_choice=[]
		random_num=random.choice(list1)

		f1=open("id_list.pkl","ab")
		f2=open("id_list.pkl","rb")
		f2_content=f2.readlines()

		for line in f2_content:
			line=line.replace('\n','')
			result_choice.append(str(line))

		print result_choice

		if i+1==list1_len and len(result_choice)==list1_len:
			print "列表中所有的值已取完！"
			break

		if str(random_num) not in result_choice:
			f1.write(str(random_num))
			f1.write("\n")
			print u"第%d次随机的值为:%s"%(len(result_choice)+1,random_num)
			return str(random_num)

		else:
			print u"第%d次随机的值为:%s,已重复，自动重新获取"%(len(result_choice)+1,random_num)
			continue


		f1.close()
		f2.close()


#测试环境songID高潮hash取值
def getClientHash():
    hash={46211:"0B1F31FBFABE3920B4284CDDFC60986D",
            2681335:"14EE6824410B8999631837E5E56680F7",
            174201:"42E9A70B8FE5052A4C84F6765738E27B"}
    hash_len=len(hash)
    hash_key=hash.keys()
    hash_value=hash.values()
    # print hash_key
    # print hash_value
    return str(hash_key[hash_len-1]),str(hash_value[hash_len-1])


#生成IDFA数据
def generalIDFA(bit):
    bit=int(bit)
    list1=[]
    for i in range(10):
        list1.append(str(tool_Libary.randomstr(bit)))
    return list1




#*********************************变量定义区域***********************************
#随机获取版本号
getVersion=choiceVersion()

#设置预期值变量
expected=0

#获取测试环境下的userid
getUserId=choiceTest_UserId("random")
# print getUserId


getUserName=choiceTest_UserName("random")
# print getUserName

getSongId=getRandomValue_Range(1000001,5000000)
# print getSongId

#生成IDFA数据列表
idfa_32=generalIDFA(32)
idfa_40=generalIDFA(40)
idfa_50=generalIDFA(50)


#******************线上环境变量***************************
#获取线上环境下的userid,根据下标
#getUserId=choiceUserId(0)
# print getUserId
#获取线上环境下userid,随机
#getUserId=choiceUserId("random")
# print getUserId

#获取roomid,根据下标
#getRoomId=choiceRoomId(0)
# print getRoomId
#获取roomid,随机
# getRoomId=choiceRoomId("random")
# print getRoomId


#取歌曲id及hash值
Clienthash=getClientHash()

#生成IDFA数据列表
idfa_32=generalIDFA(32)
idfa_40=generalIDFA(40)
idfa_50=generalIDFA(50)

#定义歌手列表，用于搜索功能
singer_list=[u"阿信",u"饶天亮",u"陈奕迅",u"成龙",u"张学友",u"周华健",u"宠龙",u"萧亚轩",u"崔子格",u"筷子兄弟",u"凤凰传奇",u"Twins",u"Usher",u"Michael Jackson","Justin","M2M","Backstreet","westlife","PSY",u"安七炫",u"李洪基","EXO","Bigbang","a","b"]
song_list=[u"父亲",u"左右",u"卓玛",u"家在东北",u"说好了不见面",u"一生何求",u"约定",u"青青河边草",u"亲密爱人",u"约定","a","b",u"雪中情"]


#定義評論內容
comment_list=["好爱你","美","喜欢你","大家点点关注啦","不错","萌萌的","好萌啊","不错哦","诶哟不错哦","好听","好爱演","爱演","会演","会玩","真有意思","有趣","逗逗你","23333","6666","32个赞","真好看","太棒啦","棒棒哒","我爱你","也是6了","给力","顶","顶起","主播加油","真心赞","我也要演","沙发","粉上你了","关注主播了","关注一个","等着你直播","挺好的","哈哈哈","O(∩_∩)O","拍的不错","喜欢","跟真的一样","太牛啦","牛","厉害","很好很强大","看不够啊","强烈要求再来一段","求更多视频","跪求录更多视频啊！！","帅死了","这个最好看","酷","酷，爱你","我喜欢","就这个feel","就是这个味儿","勇气可嘉","哇塞","哇！","真会玩","有点牛","永远支持你","加油吧","每天看一遍","一天刷十遍","天天来看你","签到打卡","刷视频签到","围观团","每日签到么么哒","粉丝团围观","wuli亲亲","谢谢"]
#返回随机获取的歌手关键字
get_Singer_keyword=choiceSiner_list_keyword()
# print get_Singer_keyword

#返回随机获取的歌曲关键字
get_Song_keyword=choiceSong_list_keyword()
# print get_Song_keyword

# get_value_list=getRandomValue_List(singer_list)
# print get_value_list


#返回隨機抽出來的評論內容
get_comment_keyword=choiceComment_list_keyword()
# print get_comment_keyword


#获取随机字符串
randomstr=tool_Libary.randomstr()