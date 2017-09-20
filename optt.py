import sys
from PyQt5.QtWidgets import *
import kvmauto

class OPTT(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('选择功能')
        self.setGeometry(500, 300, 400, 300)
        self.GridK()

    def GridK(self):
        self.grid = QGridLayout()
        self.kvma1()
        self.setLayout(self.grid)

        self.kvmautobutton.clicked.connect(self.kvmautomain)

    def kvma1(self):
        self.kvmautobutton = QPushButton('kvm自动重启工具')
        self.kvmclonebutton = QPushButton('kvm一键克隆')
        self.kvm1 = QLabel('')

        self.grid.addWidget(self.kvmautobutton, 0, 0)
        self.grid.addWidget(self.kvmclonebutton, 1, 0)
        self.grid.addWidget(self.kvm1)

    def kvmautomain(self):
        KKK.show()
        self.hide()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    KKK = kvmauto.KvmAuto()
    optt = OPTT()
    optt.show()
    sys.exit(app.exec_())
else:
    app = QApplication(sys.argv)
    KKK = kvmauto.KvmAuto()