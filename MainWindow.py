import json
import os
import subprocess
import sys
from random import choice
from threading import Thread

from PyQt5.QtCore import QPoint, Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, \
    QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMenu, QAction, QMessageBox
from pynput import mouse

from TrayIcon import TrayIcon


class BaseSignal(QObject):
    signal = pyqtSignal()

    def emit(self):
        self.signal.emit()

    def connect(self, func):
        self.signal.connect(func)


class RelaxWindow(QMainWindow):
    config = {"waiting_time": 300, "player": "default", "play_list": []}

    def __init__(self):
        super().__init__()
        self.read_config()

        self.initUI()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.play)

        self.start_timer_signal = BaseSignal()
        self.start_timer_signal.connect(self.start_timer)

        # 子线程监听是否有鼠标、键盘活动
        thread = Thread(target=self.listen_activity)
        thread.setDaemon(True)
        thread.start()

    def listen_activity(self):
        with mouse.Listener(on_move=lambda x, y: self.start_timer_signal.emit()) as listener:
            listener.join()

    def start_timer(self):
        try:
            seconds = int(self.waiting_time_edit.text())
        except Exception:
            return

        if seconds > 0:
            print("start_timer", seconds)
            self.timer.start(seconds * 1000)

    def play(self):
        print("play")
        dir_list = []
        count = self.play_list_widget.count()
        print("count", count)
        for i in range(count):
            s = self.play_list_widget.item(i).text()
            print("path", s)
            dir_list.append(s)
        if len(dir_list) == 0:
            return

        dir = choice(dir_list)
        print("choose dir", dir)
        name_list = os.listdir(dir)
        print("test")

        while True:
            file_name = choice(name_list)
            file_path = dir + "/" + file_name
            if os.path.isfile(file_path):
                break

        player = self.player_path_label.text()

        t = Thread(target=lambda: self.t_play(player, file_path))
        t.setDaemon(True)
        t.start()

    def t_play(self, player, file_path):
        print("player", player)
        print("file_path", file_path)
        if player != "default":
            exe = "\"%s\"" % (player.replace('\\', '/'))
            print("exe", exe)
            os.system("%s %s" % (exe, file_path))
        else:
            os.startfile(file_path)

    def initUI(self):
        self.setWindowTitle("Relax Time")
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowMinimizeButtonHint & ~Qt.WindowMaximizeButtonHint)  # 取消最小化最大化按钮

        # 等待时间
        waiting_time_label = QLabel("等待时间：")
        self.waiting_time_edit = QLineEdit()
        self.waiting_time_edit.setText(str(self.config["waiting_time"]))
        seconds_label = QLabel("s")
        time_layout = QHBoxLayout()
        time_layout.addWidget(waiting_time_label)
        time_layout.addWidget(self.waiting_time_edit)
        time_layout.addWidget(seconds_label)

        # 播放器
        player_label = QLabel("播放器：")
        self.player_path_label = QLabel(self.config["player"])
        player_change_btn = QPushButton("更换")
        player_change_btn.clicked.connect(self.show_choose_player_dialog)
        player_layout = QHBoxLayout()
        player_layout.addWidget(player_label)
        player_layout.addWidget(self.player_path_label)
        player_layout.addWidget(player_change_btn)

        # 播放路径
        list_label = QLabel("播放路径：")
        self.add_play_dir_btn = QPushButton("添加")
        self.add_play_dir_btn.clicked.connect(self.show_choose_play_dir_dialog)
        play_dir_layout = QHBoxLayout()
        play_dir_layout.addWidget(list_label)
        play_dir_layout.addWidget(self.add_play_dir_btn)
        self.play_list_widget = QListWidget()
        for dir in self.config["play_list"]:
            self.play_list_widget.addItem(dir)
        self.play_list_widget.setContextMenuPolicy(3)
        self.play_list_widget.customContextMenuRequested[QPoint].connect(self.show_item_menu)

        # 保存配置
        save_btn = QPushButton("应用并保存配置")
        save_btn.clicked.connect(self.save_config)
        save_layout = QHBoxLayout()
        save_layout.addWidget(save_btn)

        # 子布局放入父布局中
        main_layout = QVBoxLayout()
        main_layout.addLayout(time_layout)
        main_layout.addLayout(player_layout)
        main_layout.addLayout(play_dir_layout)
        main_layout.addWidget(self.play_list_widget)
        main_layout.addLayout(save_layout)

        # 设置 MainWindow 的中心组件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def delete_play_dir(self):
        """
        删除播放路径
        """
        item = self.play_list_widget.currentItem()
        row = self.play_list_widget.row(item)
        self.config["play_list"].pop(row)
        self.play_list_widget.takeItem(row)

    def show_choose_player_dialog(self):
        """
        显示选中播放器的对话框
        """
        # 第二个返回值是什么呢？
        filename, _ = QFileDialog.getOpenFileName()
        if filename != "":
            self.player_path_label.setText(filename)

    def show_choose_play_dir_dialog(self):
        """
        显示选择播放路径对话框
        """
        dir = QFileDialog.getExistingDirectory()
        if dir != "":
            self.config["play_list"].append(dir)
            self.play_list_widget.addItem(dir)

    def read_config(self):
        """
        读取配置文件
        """
        config_path = self.get_config_file_path()

        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                self.config = json.load(file)

    def get_config_file_path(self):
        """
        获取配置文件路径
        :return:
        """
        config_dir = os.environ['TEMP']
        return config_dir + "/relax_time.config"

    def save_config(self):
        """
        保存配置到文件, json 格式
        """
        self.config["waiting_time"] = self.waiting_time_edit.text()
        self.config["player"] = self.player_path_label.text()
        self.config["play_list"] = []

        count = self.play_list_widget.count()
        for i in range(count):
            self.config["play_list"].append(self.play_list_widget.item(i).text())
        config_path = self.get_config_file_path()
        with open(config_path, "w") as file:
            json.dump(self.config, file)

    def show_item_menu(self):
        """
        显示列表项菜单
        :return:
        """
        popMenu = QMenu()
        delete_action = QAction("删除")
        delete_action.triggered.connect(self.delete_play_dir)
        popMenu.addAction(delete_action)
        popMenu.exec_(QCursor.pos())

    def closeEvent(self, event):
        """
        关闭窗口事件，覆盖父类函数

        :param event: 关闭窗口事件
        """
        event.ignore()  # 忽略该事件
        self.hide()  # 隐藏窗口

    def exit(self):
        self.timer.stop()
        exit(0)


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
