#!/usr/bin/python
# -*- coding:utf-8 -*-
import re
from os import system
from commands import getoutput
import sys

#设置clone时默认放在源主机同一文件下
#多次数时,默认最后数字加一来clone,作为下一次的主机名

def myprompt():
    print '-s 1源主机名'
    print '-o 1新主机名( 格式:hostname-1(数字) ) 2次数( 默认为1 )'
    print '例: python onceclone.py -s centos6 -o centos6-1 3'
    sys.exit()

#得到所有输入
aargv = sys.argv[1:]
if len(aargv) == 0 or '-h' in aargv or '--help' in aargv or len(aargv) > 5:
    myprompt()

#得到源主名,新克隆名,次数(默认1)
shostname =  aargv[aargv.index('-s')+1]
optn = aargv.index('-o')
clonename = aargv[optn+1]
clonenum = 1
if len(aargv) > optn+2:
    if aargv[optn+2] != '-s':
        if aargv[optn+2].isdigit():
            clonenum = int(aargv[optn+2])

#判断传的克隆名是否正确:
if len(clonename.split('-')) != 2 or not clonename.split('-')[1].isdigit():
    print '请输入正确的参数'
    myprompt()

#得到所有虚拟机名
vmhostname = getoutput('''virsh list --all |awk '{print $2}' |grep -v '^$' |sed '1d' ''')
#判断输入的主机名是否正确
if shostname not in vmhostname:
    print '输入的源主机名错误: {0}'.format(shostname)
    sys.exit()
if clonename in vmhostname:
    print '新主机名已经有了,请修改'
    sys.exit()

#得到源主机mac地址, fixsmac修改mac地址
#smac是传入的mac地址,i是自我调用时的增量,以便拿到正确的mac段
#num是根据hostname-1(数字)中的数字来改变最后的mac数
def fixsmac(smac, i=0, num=1):
    while i<16:
        fixmac = smac[15-i:17-i]
        shi = int(fixmac, 16)
        if shi == 255:
            smac = fixsmac(smac, i=i+3)
        if shi==255:
            if i==0:
                smac = smac.replace(fixmac, hex(num).split('x')[1].zfill(2), 1)
            else:
                smac = smac.replace(fixmac, '00', 1)
        else:
            smac = smac.replace(fixmac, hex(shi+num).split('x')[1].zfill(2), 1)
        return smac
    print '处理错误'

#得到源主机的xml配置文件
system('''virsh dumpxml {0} > {0}.xml'''.format(shostname))

#查找源主机所有磁盘
alldisk =  re.compile("(?<=device='disk).*?(?=</disk>)", re.S)
with open(shostname+'.xml') as f:
    xmlcom = f.read()

#制造re.compile来查找vnc,判断是否需要修改vnc, 每次修改+1
sfvnc = re.compile("(?<=vnc' port=').*?(?=')")
sfvnc = sfvnc.findall(xmlcom)
svnc = 0
if len(sfvnc) > 0:
    svnc = 1
    vncport = sfvnc[0]

#onlydiskdata存放所有磁盘的信息
onlydiskdata = []
alldiskdata = alldisk.findall(xmlcom)
onlydisk = re.compile("(?<=file=').*(?='/>)")
for i in alldiskdata:
    vmdisk = onlydisk.findall(i)
    onlydiskdata.append(vmdisk[0])

system('mkdir ./kvminfo')
#查找源主机xml文件的mac地址
smac =  getoutput('''grep 'mac address' {0}.xml '''.format(shostname)).split("'")[1]
ZerohourName = clonename.split('-')
#hostnameandmac 是文件名
hostnameandmac = ZerohourName[0] +'-'+ clonename.split('-')[1] +'~'+ str(int(clonename.split('-')[1]) + clonenum-1)
for i in xrange(clonenum):
    ZerohourCloneName = ZerohourName[0] + '-' + str(int(ZerohourName[1])+i)
    print '正在复制虚拟机{0}'.format(ZerohourCloneName)
    #复制源xml文件,成为clone的xml文件
    system('yes |cp {0}.xml {1}.xml'''.format(shostname,ZerohourCloneName))
    #复制所有磁盘, 之后修改修改xml文件磁盘信息
    for diskdata in onlydiskdata:
        system('''yes |cp {0} {1}'''.format(diskdata, diskdata.replace(shostname, ZerohourCloneName)))
        system('''sed -i 's:{0}:{1}:g' {2}.xml '''.format(diskdata, disskdata.replace(shostname, ZerohourCloneName), ZerohourCloneName))
    #修改xml文件 中的 主机名, mac地址, 删除uuid号
    system('''sed -i 's:<name>{0}</name>:<name>{1}</name>:g' {1}.xml '''.format(shostname, ZerohourCloneName))
    clonemac = fixsmac(smac, num=int(ZerohourName[1])+i)
    system('''sed -i "s!<mac address='{0}'/>!<mac address='{1}'/>!g" {2}.xml '''.format(smac, clonemac, ZerohourCloneName))
    uuirow = int(getoutput('''grep -n 'uuid' {0}.xml'''.format(ZerohourCloneName))[0])
    system('''sed -i '{0}d' {1}.xml '''.format(uuirow, ZerohourCloneName))
    #判断是否修改vnc端口
    if svnc == 1:
        system('''sed -i "s/vnc' port='{0}'/vnc' port='{1}'/g" {2}.xml '''.format(vncport, int(vncport)+int(ZerohourCloneName.split('-')[1]), ZerohourCloneName))
    #移动xml文件到指定位置, 并定义xml文件
    system('''mkdir -p /etc/libvirt/qemu ''')
    system('''mv {0}.xml  /etc/libvirt/qemu/'''.format(ZerohourCloneName))
    system('''virsh define /etc/libvirt/qemu/{0}.xml '''.format(ZerohourCloneName))
    #建立主机名和mac对应的信息
    system('''echo '{0} {1}' >> ./kvminfo/{2} '''.format(ZerohourCloneName, clonemac, hostnameandmac))

system('''rm -rf {0}.xml '''.format(shostname))
print '完成'