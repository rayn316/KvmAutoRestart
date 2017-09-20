import paramiko
from time import sleep
import os
import threading
import time

class SSHTest():
    """docstring for self.sshTest"""
    def __init__(self):
        super().__init__()

    #测试用函数, 无特别意义
    def Test():
        pass

    # 执行命令,返回结果
    def execCommand(self, cmd, timeout=None):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=timeout)
            return stdout.readlines()
        except:
            pass

    # 判断脚本是否已经存在, 没有就先创建路径
    def Isexist(self):
        def pddir(filename):
            if os.path.isfile(filename):
                #直接ls 文件， 查看是否存在
                #分开路径和目录
                p, f = os.path.split(filename)
                #判断是不是带目录(不带)
                if not p:
                    self.scppyscripts(filename)
                else:
                    self.execCommand('mkdir -p {0}{1}'.format(self.path, p))
                    self.scppyscripts(filename)
            else:
                #目录不存在， 则创建目录
                if not self.execCommand('ls {0}{1}'.format(self.path, filename)):
                    self.execCommand('mkdir -p {0}{1}'.format(self.path, filename))
                    self.scppyscripts(filename)
        #判断是不是文件夹（是）
        def pdfile(filename):
            if os.path.isdir(filename):
                for i in os.walk(filename):
                    #判断i[0]是不是目录, 空目录不管
                    for j in i[2]:
                        filename = i[0]+'/'+j
                        pddir(filename)
        pdfile(self.filename)

    # 上传文件, 只负责上传功能
    def scppyscripts(self, filename):
        print(filename)
        print('正在上传')
        scppath = self.path
        # 因为上传文件路径中不能 以 ~开头, 将转化成 用户根目录
        if self.path[0] == '~':
            scppath = self.execCommand('pwd')[0].split('\n')[0] + '/kvmpy/'
        t = paramiko.Transport((self.ip, self.port))
        t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        localpath = './{0}'.format(filename)
        remotepath = '{0}{1}'.format(scppath, filename)
        sftp.put(localpath, remotepath)
        t.close()


    # 测试用户主目录下是否有脚本,没有 就上传脚本
    def SSHMain(self, ip, username, password, maincmd=Test(), path='~', port=22 ,filename='kvmscripts'):
        self.path = path + '/kvmpy/'
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.filename = filename
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, self.port, self.username, self.password)
        if maincmd == 'Isexist':
            self.Isexist()
        elif maincmd == 'runpy':
            self.runpy()
        elif maincmd == 'stoppy':
            self.stoppy()
        elif maincmd == 'searchVM':
            self.searchVM()
        # 最后关闭连接
        self.ssh.close()

    # 执行脚本, 应为怕传送的是文件夹, 所以固定filename
    def runpy(self, filename='kvmscripts/auto-restore-host.py'):
        print('python2 kvmpy/{0}'.format(filename))
        self.execCommand('python2 kvmpy/{0}&'.format(filename), timeout=1)

    # 停止脚本
    def stoppy(self, filename='auto-restore-host.py'):
        self.execCommand(''' ps -aux |grep auto-restore-host.py |awk '{print $2}' |xargs kill -9 ''')

    # 查询所有虚拟机
    def searchVM(self):
        a = self.execCommand(''' virsh list --all |awk '{print $2}' |grep -v '^$' |sed '1d' ''')
        with open('ini/AllVM', 'w') as f:
            for i in range(len(a)):
                f.write(a[i])

if __name__ =='__main__':
    SSHTest().SSHMain(ip="172.19.209.156", username='root', password='cqcet!!@)$', maincmd='runpy')