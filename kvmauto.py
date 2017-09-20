import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from ssh_testE import SSHTest

kvmautofile = 'auto-restore-host.py'
scpfile = 'kvmscripts/NRestVName'

class KvmAuto(QWidget):
    def __init__(self):
        super().__init__()
        self.inititem()
        self.sshtest = SSHTest()
        self.Hbox1()
        self.GridL()
        self.Allvm()
        self.avm1 = []

    def inititem(self):
        self.setGeometry(500, 300, 500, 400)
        self.setWindowTitle('kvm 自动启动器')

    def GridL(self):
        self.Grid = QGridLayout()

        self.listallvm = QListWidget()
        self.needvm = QListWidget()
        self.allKvmName = QLabel("全部虚拟机")
        self.needKvmname = QLabel("已选择")

        self.Grid.addWidget(self.allKvmName, 0, 0)
        self.Grid.addWidget(self.listallvm, 1, 0)
        self.Grid.addWidget(self.needKvmname, 2, 0)
        self.Grid.addWidget(self.needvm, 3, 0)
        self.Grid.addLayout(self.hboxb1, 4, 0)

        self.setLayout(self.Grid)
        self.listallvm.itemClicked.connect(self.addvm)
        self.needvm.itemClicked.connect(self.delvm)
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)

    def Hbox1(self):
        self.hboxb1 = QHBoxLayout()

        self.startButton = QPushButton("开始")
        self.stopButton = QPushButton("停止")
        self.onoff = QLabel()
        self.pixmapoff = QPixmap('img/no.ico')
        self.onoff.setPixmap(self.pixmapoff)

        self.hboxb1.addWidget(self.stopButton)
        self.hboxb1.addWidget(self.onoff)
        self.hboxb1.addWidget(self.startButton)
    #添加到needvm框中
    def addvm(self, obj1):
        if obj1.text() not in self.avm1:
            self.avm1.append(obj1.text())
            self.needvm.addItem(obj1.text())
    #删除needvm框中的值
    def delvm(self, obj2):
        self.avm1.remove(obj2.text())
        self.needvm.takeItem(self.needvm.currentRow())

    #查看文件,载入全部虚拟机名
    def Allvm(self):
        #载入用户密码
        import login
        l = login.LoginDialog()
        l.loginInterZ()
        self.loginInter = login.loginInter

        self.sshtest.SSHMain(ip=self.loginInter[0], username=self.loginInter[1], password=self.loginInter[2], maincmd='searchVM')
        #打开AllVM文件, 查找所有虚拟机
        with open('ini/AllVM') as f:
            allvm1 = f.read().split('\n')
        for i in range(len(allvm1)):
            self.listallvm.insertItem(i+1, QListWidgetItem(allvm1[i]))

    #开始按钮对应函数
    def start(self):
        #检测needvm 是否时空值, 是提示
        if self.avm1 == []:
            QMessageBox.critical(self, u'警告', u'请确定需要自动启动的虚拟机')
        self.onoff.setPixmap(QPixmap('img/start.ico'))
        #更改 kvmscripts/NRestVName 中的值
        with open('kvmscripts/NRestVName', 'w') as f:
            for i in self.avm1:
                f.write(i+'\n')
        #之后传送文件到远程主机
        self.sshtest.SSHMain(ip=self.loginInter[0], username=self.loginInter[1], password=self.loginInter[2], maincmd='Isexist', filename=scpfile)
        #运行脚本
        self.sshtest.SSHMain(ip=self.loginInter[0], username=self.loginInter[1], password=self.loginInter[2], maincmd='runpy')
        
    #停止按钮对应函数
    def stop(self):
        self.sshtest.SSHMain(ip=self.loginInter[0], username=self.loginInter[1], password=self.loginInter[2], maincmd='stoppy')
        self.onoff.setPixmap(QPixmap('img/no.ico'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    kvm = KvmAuto()
    kvm.show()
    sys.exit(app.exec_())