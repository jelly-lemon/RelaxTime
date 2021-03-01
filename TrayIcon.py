from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    """
    托盘图标
    """
    def __init__(self, MainWindow):
        super().__init__()

        self.setToolTip('Relax Time 正在运行')

        self.MainWindow = MainWindow

        self.createMenu()




    def createMenu(self):
        """
        初始化右键菜单
        """
        menu = QMenu()
        self.toggle_action = QAction("停止")
        self.toggle_action.triggered.connect(self.toggle)
        self.exit_action = QAction("退出")
        self.exit_action.triggered.connect(self.MainWindow.exit)

        menu.addAction(self.toggle_action)
        menu.addAction(self.exit_action)
        self.setContextMenu(menu)  # 设置之后右键就出现菜单

        # 设置图标
        self.setIcon(QIcon(":/logo.png"))

        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.onIconClicked)

    def toggle(self):
        """
        切换状态，关闭或打开
        """
        if self.MainWindow.is_working():
            # 关闭
            self.toggle_action.setText("启动")
            self.MainWindow.stop_working()
            self.MainWindow.stop_timer()
            self.setToolTip("Relax Time 已停止")
            self.setIcon(QIcon(":/logo_grey.png"))
            print("关闭功能")
        else:
            # 开启
            self.toggle_action.setText("停止")
            self.MainWindow.start_working()
            self.MainWindow.start_timer()
            self.setToolTip('Relax Time 正在运行')
            self.setIcon(QIcon(":/logo.png"))
            print("打开功能")


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
