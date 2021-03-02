import sys

from PyQt5.QtWidgets import QApplication

from MainWindow import RelaxWindow
from TrayIcon import TrayIcon

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 主界面
    relaxWindow = RelaxWindow()
    relaxWindow.show()

    # 托盘图标
    tray_icon = TrayIcon(relaxWindow)
    tray_icon.show()

    # 事件驱动
    sys.exit(app.exec_())