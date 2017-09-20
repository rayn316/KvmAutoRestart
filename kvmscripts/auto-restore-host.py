#!/usr/bin/python
# -*- coding:utf-8 -*-
from os import system
from commands import getoutput
import time
import sys, os

#切换到脚本目录
pypath = sys.argv[0]
if len(pypath.split('/')) > 1:
    b = os.path.basename(pypath)
    pypath = pypath.split(b)[0]
    os.chdir(pypath)

#设定时间,没过5秒检查到没开机的系统,自动恢复快照并重启
#值为设定时间减一
autotime = 4

#从文件中读取所有需要自动重置的虚拟机名
def getVritualName():
    with open('./NRestVName') as Vname:
        a = Vname.read().split('\n')
	for i in a:
	    if i == '':
		a.remove(i)
        return a

#恢复快照并重启
def hfkzAcq(hostname):
    snapname = getoutput('''virsh snapshot-list {0} |tail -n 2'''.format(hostname)).split()[0]
    if '------------' not in snapname:
        system('''virsh snapshot-revert {0} {1}'''.format(hostname, snapname))
        print '''virsh snapshot-revert {0} {1}'''.format(hostname, snapname)
    system('''virsh start {0} '''.format(hostname))
    print '恢复重启了: ' + hostname

#得到所有虚拟机名
def getname(allclonename):
    allhostname = []
    awds = getoutput('''virsh list --all |awk '{print $2, $3}' |grep -v '^$' |sed '1d' ''')
    #过滤
    for nas in awds.split('\n'):
        if nas == ' ':
            continue
        #判断需要重启的虚拟机名 是否正确
        for i in allclonename:
            if i in nas:
                a = nas.split()
		#判断虚拟机是否关闭
                allhostname.append(nas)
    return allhostname

#判断需要重置的虚拟机是否处于关机状态, 如果连续关机5秒, 则会自动 重置 虚拟机
#恢复虚拟机 最近的一个快照
def startRestore():
    print '已经开启了此脚本'
    thostname = {}
    allclonename = getVritualName()
    while True:
        allhostname = getname(allclonename=allclonename)
        for nas in allhostname:
	    print nas
            a = nas.split()
            for tclonename in allclonename:
                if a[1] == 'shut':
                    #判断是否有值,没有初始化虚拟机的值,为0
                    if not thostname.get(a[0]):
                        thostname[a[0]] = 1
                    else:
                        thostname[a[0]] += 1
                    if thostname[a[0]] == autotime:
                        print '正在重置虚拟机: '+ a[0]
                        hfkzAcq(a[0])
                        #此处删除值
                        del thostname[a[0]]
        time.sleep(1)

if __name__ == "__main__":
    startRestore()
