from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMenu, QAction, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    def __init__(self, MainWindow):
        super().__init__()


        self.MainWindow = MainWindow

        self.createMenu()

    def createMenu(self):
        self.menu = QMenu()
        self.work_flag = True
        self.toggle_action = QAction("停止")
        self.toggle_action.triggered.connect(self.toggel)
        self.exit_action = QtWidgets.QAction("退出")
        self.exit_action.triggered.connect(self.close)

        self.menu.addAction(self.toggle_action)
        self.menu.addAction(self.exit_action)
        self.setContextMenu(self.menu)

        # 设置图标
        self.setIcon(QtGui.QIcon("./img/logo.png"))

        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.onIconClicked)

    def toggel(self):
        if self.work_flag:
            self.toggle_action.setText("启动")
            self.work_flag = False
        else:
            self.toggle_action.setText("停止")
            self.work_flag = True

    def close(self):
        exit(0)

    def show_normal_window(self):
        self.MainWindow.showNormal()

    def quit(self):
        QtWidgets.qApp.quit()

    # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
    def onIconClicked(self, event):
        if event == 3 or 2:
            self.show_normal_window()

