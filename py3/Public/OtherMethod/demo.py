#coding=utf-8
import random

min=1
max=20

def getValue():
	for i in xrange(max+1):
		result_choice=[]
		random_num=random.choice(range(min,max+1))

		f1=open("id.txt","ab")
		f2=open("id.txt","rb")
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
			return random_num

		else:
			print u"第%d次随机的数:%d,已重复，自动重新获取"%(len(result_choice)+1,random_num)
			continue


		f1.close()
		f2.close()

if __name__ == '__main__':
	
	a=getValue()
	print a