#!/bin/bash
###在jenkins中command中输入的命令串，现已不用！
##sudo sh  ${JENKINS_HOME}/workspace/JoyrunServer/Online_Master_Con_d2/Public/Online.sh  ${BUILD_TIMESTAMP}   ${JENKINS_HOME}/workspace/JoyrunServer/Online_Master_Con_d2
sudo  mkdir  /var/lib/jenkins/Report/$1
sleep 3 
pybot --include Online  --variable  JoyrunEvn:Online   -V   /home/apps/thejoyrunTestcode/Public/JoyrunOnline_var.py  -d /var/lib/jenkins/Report/$1   $2 