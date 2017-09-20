import sys
from PyQt5.QtWidgets import *
from cryptography.fernet import Fernet
from ssh_testE import SSHTest
import optt

loginInter = []
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.cipher = Fernet(b'5_-IbD5TmGz9GkwkBV9DoH0Sx1-zdEh9T2XNzHfDtrA=')
        self.setWindowTitle(u'登录')
        self.setGeometry(500, 300, 150, 180)
        self.initmain()
        self.show()

    def initmain(self):
        self.leIp = QLineEdit(self)
        self.leIp.setPlaceholderText(u'IP')

        self.leName = QLineEdit(self)
        self.leName.setPlaceholderText(u'用户名')

        self.lePassword = QLineEdit(self)
        self.lePassword.setEchoMode(QLineEdit.Password)
        self.lePassword.setPlaceholderText(u'密码')

        self.pbsave = QRadioButton(u'保存密码', self)
        self.pbLogin = QPushButton(u'登录', self)
        self.pbCancel = QPushButton(u'取消', self)

        self.pbLogin.clicked.connect(self.zlogin)
        self.pbCancel.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.leIp)
        layout.addWidget(self.leName)
        layout.addWidget(self.lePassword)

        # 放一个间隔对象美化布局
        spacerItem = QSpacerItem(20, 48, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacerItem)

        # 按钮布局
        buttonLayout = QHBoxLayout()
        # 左侧放一个间隔
        spancerItem2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttonLayout.addItem(spancerItem2)
        buttonLayout.addWidget(self.pbsave)
        buttonLayout.addWidget(self.pbLogin)
        buttonLayout.addWidget(self.pbCancel)

        self.firstfile()
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    #初始化时检查文件是否有ip用户密码
    def firstfile(self):
        a = len(open('ini/mimi.txt', 'rU').readlines())
        if a not in [2, 3]:
            return None
        with open('ini/mimi.txt') as f:
            f = f.read().split('\n')
            self.leIp.setText(f[0])
            self.leName.setText(f[1])
            #需要mini文件第三行不为空
            if f[2] != '':
                #密码需要解码
                self.lePassword.setText(self.cipher.decrypt(f[2].encode(encoding='utf-8')).decode())

    #登陆检查ip函数
    def zlogin(self):
        ip = self.leIp.text()
        if len(ip.split('.')) == 4 and self.ipYesorNo(ip) != 'error':
            #ip正确时, 连接测试环境
            a = self.logincheck()
            if a:
                self.loginInterZ()
                self.accept()  # 关闭对话框并返回
                opmain.show()
                self.hide()
                self.close()
        else:
            QMessageBox.critical(self, u'警告', u'IP不正确')

    #判断ip是不是正常的
    def ipYesorNo(self, ip):
        for i in ip.split('.'):
            if int(i) < 0 and int(i) > 255:
                return 'error'

    #登陆模块, 当密码错误时提示,并不停止
    #连接正确, 确立环境
    def logincheck(self):
        try:
            #自动保存IP 和用户名
            #判断保存密码键是否按下
            save = self.pbsave.isChecked()
            if save:
                # 加密密码
                self.ispbsave = self.cipher.encrypt(self.lePassword.text().encode(encoding='utf-8'))
                with open('ini/mimi.txt', 'w') as f:
                    f.write(self.leIp.text() + '\n' + self.leName.text() + '\n' + self.ispbsave.decode())
            else:
                with open('ini/mimi.txt', 'w') as f:
                    f.write(self.leIp.text() + '\n' + self.leName.text() + '\n')

            #测试连接, 没有错误返回 None
            sshtest = SSHTest()
            sshtest.SSHMain(ip=self.leIp.text(),username=self.leName.text(),password=self.lePassword.text())
            return True
        except Exception as e:
            print(e)
            QMessageBox.critical(self, u'警告', u'用户名或密码不正确')
            return False

    def loginInterZ(self):
        loginInter.append(self.leIp.text())
        loginInter.append(self.leName.text())
        loginInter.append(self.lePassword.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    opmain = optt.OPTT()
    dialog = LoginDialog()
    sys.exit(app.exec_())