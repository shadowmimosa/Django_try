#coding=utf-8
import random
# import Get_UserId_list
# import Get_roomid_list
import tool_Libary
import os,sys,glob
#功能：线上环境下，变量文件。（除环境url外，其它需使用到的外部变量均在此文件定义）

exedir = os.path.abspath('.')
sys.path.insert(0,glob.glob(exedir)[0])


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
    关注mvcomment1帐号,对应userId为：137115211
    关注mvcomment1帐号,对应userId为：137113289
    关注leq5566帐号,对应userid为: 68430171
    关注leq3344帐号, 对应userid为: 64313938
    '''
    userid_list=['137115211','137113289','68430171','64313938']
    # print userid_list
    if n=="random":
        userid_random=random.choice(userid_list)
        return str(userid_random)
    elif isinstance(n,int):
        userid_random=userid_list[n]
        return str(userid_random)


#随机获取测试环境指定的用户名，提供两种方法，一种随机获取，一种根据下标获取
def choiceTest_UserName(n):

    # userName_list=['testfx01','mvcomment1','leq5566','mikezhou2026']
    userName_list=['testfx01','testfx02','testfx03','testfx04','mvcomment1','leq5566','mikezhou2026','kevinpowter1','kevinpowter2','kevinpowter3','kevinpowter4','kevinpowter5']
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


#线上songID高潮hash取值
def getClientHash():
    hash={46211:"DFEA69D3A5A08AC7442F3FB03728D11C",
            2681335:"F1F99E0ABB8A4D85955FE72230B4ED85",
            174201:"33E71CF40EBB3BC115B20E533569718B"}
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
# getUserId=choiceTest_UserId("random")
# print getUserId


getUserName=choiceTest_UserName("random")
# print getUserName

# getSongId=getRandomValue_Range(1000001,5000000)
# print getSongId

#生成IDFA数据列表
idfa_32=generalIDFA(32)
idfa_40=generalIDFA(40)
idfa_50=generalIDFA(50)

#******************线上环境变量***************************
#获取线上环境下的userid,根据下标
# getUserId=choiceUserId(0)
# print getUserId
#获取线上环境下userid,随机
getUserId=choiceTest_UserId("random")
# print getUserId

#获取roomid,根据下标
# getRoomId=choiceRoomId(0)
# print getRoomId
#获取roomid,随机

# getSongId=getRandomValue_Range(10001,100000)

# getRoomId=choiceRoomId("random")
# print getRoomId


#获取随机不重复id
getSongId=getRandomValue_Range(20001,10000000)


#取歌曲id及hash值
Clienthash=getClientHash()

#生成IDFA数据列表
idfa_32=generalIDFA(32)
idfa_40=generalIDFA(40)
idfa_50=generalIDFA(50)
#定义歌手列表，用于搜索功能
singer_list=["阿信","饶天亮","陈奕迅","成龙","张学友","周华健","宠龙","萧亚轩","崔子格","筷子兄弟","凤凰传奇","Twins","PSY","安七炫","EXO"]
song_list=["父亲","左右","小","红日","吻别","草原","千里","亲密爱人","约定","可爱"]


#定義評論內容
comment_list=["好爱你","美","喜欢你","大家点点关注啦","不错","萌萌的","好萌啊","不错哦","诶哟不错哦","好听","好爱演","爱演","会演","会玩","真有意思","有趣","逗逗你","23333","6666","32个赞","真好看","太棒啦","棒棒哒","我爱你","也是6了","给力","顶","顶起","主播加油","真心赞","我也要演","沙发","粉上你了","关注主播了","关注一个","等着你直播","挺好的","哈哈哈","O(∩_∩)O","拍的不错","喜欢","跟真的一样","太牛啦","牛","厉害","很好很强大","看不够啊","强烈要求再来一段","求更多视频","跪求录更多视频啊！！","帅死了","这个最好看","酷","酷，爱你","我喜欢","就这个feel","就是这个味儿","勇气可嘉","哇塞","哇！","真会玩","有点牛","永远支持你","加油吧","每天看一遍","一天刷十遍","天天来看你","签到打卡","刷视频签到","围观团","每日签到么么哒","粉丝团围观","wuli亲亲","谢谢","抱抱","你是主播吗","哇啊啊","爱心","老有意思了","牛得很了","32个赞~","不错不错","求关注转发","路过听听","哎哟 不错哦","支持一下！","演的这么好，你麻麻知道吗~","牛的上天了","支了个持","来看看你","我来啦","来支持你啦","挺你yo","我看好你","loveyou","loving","baby love","okok","撑你","好","好叻","正!","好正","睇极都唔厌...","你好醒目!","得劲","真得劲","麻溜地","牛老鼻子啦","贼好看","贼逗","贼有意思","贼感动","贼有内涵","嗯呐","蒽呐","稀罕","嬬得很","心疼！","巴适","巴适得板","好耍哈","有点意思蛮","可以三","可以认识你吗","你好吗","想认识你","想和你交朋友","有机会给你刷礼物吗","送礼送礼","还行","22222333333","6666666666","六六六六","今天看的最好的","看过最好的","我喜欢这个","这个挺好的","这个不错","这个牛","这个有意思","这个有点6","这个厉害","路过，赞一个","加油！！","真的很好","你是哪的","哈哈哈哈哈","真不错！","哈哈哈","真棒！","好像在附近诶","离我7km","哇，1km内，可以认识你吗","太有才了 ","鼓掌","这样也可以，厉害","火起来了","这眼神","这表情","好好听","给一个赞吧！","火火 火","演的","好好看","嘻嘻","超级搞","你好你好","天天能看到你了","哈喽","繁星越来越好玩了","繁星666","233333","老想看见","想死我了","好看又好玩","我也挺像演的","我也要秀","爱演哈哈","爱演好玩","真是爱演","爱演爱秀","力挺","力挺力挺","好，哈哈","祝福你","谢谢","谢谢你","谢谢表演","有意思","真好玩","太搞了","想听真人唱","配口型哈哈","对口型哈哈","对嘴型有意思","对嘴型666","口型动作表演！","配口型有点意思","对嘴6666","对嘴型66666","对嘴2333","对口型233333","口型也是6","还挺有神韵","每个视频都点赞","第一","第二名","第六名","沙发","板凳","点赞啦大家","点赞点赞","给你点个赞","为你赞","赞赞赞不停","思密达","么么","么么哒！","哇是原唱","哪里人","来看看你","看你今天","点击左上角头像加关注"]

#定义评论用户列表
userName_list=['testfx01','testfx02','testfx03','testfx04','mvcomment1','leq5566','mikezhou2026','kevinpowter1','kevinpowter2','kevinpowter3','kevinpowter4','kevinpowter5',"testuser2053","testuser2052","mikezhou2029","mikezhou2028","mikezhou2027","mikezhou2020","leq3344","fxlogin","fxapptest"]

#返回随机获取的歌手关键字
get_Singer_keyword=choiceSiner_list_keyword()
# print get_Singer_keyword

#返回随机获取的歌曲关键字
get_Song_keyword=choiceSong_list_keyword()
# print get_Song_keyword

#返回隨機抽出來的評論內容
get_comment_keyword=choiceComment_list_keyword()
# print get_comment_keyword

#获取随机字符串choiceTest_UserId
randomstr=tool_Libary.randomstr()
