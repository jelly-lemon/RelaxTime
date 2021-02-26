from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMenu, QAction, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    """
    托盘图标
    """

    def __init__(self, MainWindow):
        super().__init__()

        self.work_flag = True

        self.MainWindow = MainWindow

        self.createMenu()

        self.setToolTip('This is a <b>QWidget</b> widget')

    def createMenu(self):
        """
        初始化右键菜单
        """
        self.menu = QMenu()
        self.toggle_action = QAction("停止")
        self.toggle_action.triggered.connect(self.toggle)
        exit_action = QtWidgets.QAction("退出")
        exit_action.triggered.connect(self.MainWindow.exit)

        self.menu.addAction(self.toggle_action)
        self.menu.addAction(exit_action)
        self.setContextMenu(self.menu)  # 设置之后右键就出现菜单

        # 设置图标
        self.setIcon(QtGui.QIcon("./img/logo.png"))

        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.onIconClicked)

    def toggle(self):
        """
        切换状态，关闭或打开
        """
        if self.work_flag:
            self.toggle_action.setText("启动")
            self.work_flag = False
        else:
            self.toggle_action.setText("停止")
            self.work_flag = True


    def onIconClicked(self, event):
        """
        这个函数是覆盖吗？
        1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击

        :param event:
        :return:
        """
        print(event)
        if event == 1:
            pass
        elif event == 2 or 3:
            self.MainWindow.show()
