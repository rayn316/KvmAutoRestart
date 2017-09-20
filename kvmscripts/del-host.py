#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
from os import system
from commands import getoutput
import sys

def myprompt():
    print '格式: oncedelhost.py 主机名'
    print '列: python oncedelhost.py centos6-1'
    sys.exit()

shostname = sys.argv[1:]
if len(shostname) != 1 or '-h' in shostname or '--help' in shostname:
    myprompt()
    
shostname = shostname[0]
if len(shostname.split('-')) != 2 or not shostname.split('-')[1].isdigit():
    print '请输入正确的参数'
    myprompt()

#得到所有虚拟机名
vmhostname = getoutput('''virsh list --all |awk '{print $2}' |grep -v '^$' |sed '1d' ''')
#判断输入的主机名是否正确
if shostname not in vmhostname:
    print '输入的源主机名错误: {0}'.format(shostname)
    sys.exit()

#得到源主机的xml配置文件
system('''virsh dumpxml {0} > {0}.xml'''.format(shostname))

#查找源主机所有磁盘
alldisk =  re.compile("(?<=device='disk).*?(?=</disk>)", re.S)
with open(shostname+'.xml') as f:
    xmlcom = f.read()

#onlydiskdata存放所有磁盘的信息
alldiskdata = alldisk.findall(xmlcom)
onlydisk = re.compile("(?<=file=').*(?='/>)")
for i in alldiskdata:
    vmdisk = onlydisk.findall(i)
    system('''rm -rf {0}'''.format(vmdisk[0]))

system('''virsh destroy {0} '''.format(shostname))
system('''virsh undefine {0} '''.format(shostname))
system('''rm -rf {0}.xml '''.format(shostname))
print '删除虚拟机 :' + shostname