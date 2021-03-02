import sys

from PyQt5.QtWidgets import QApplication

from MainWindow import RelaxWindow
from TrayIcon import TrayIcon

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # ������
    relaxWindow = RelaxWindow()
    relaxWindow.show()

    # ����ͼ��
    tray_icon = TrayIcon(relaxWindow)
    tray_icon.show()

    # �¼�����
    sys.exit(app.exec_())