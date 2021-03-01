import json
import os
import sys
import time
from random import choice
from threading import Thread

from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QCursor, QIcon, QIntValidator
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, \
    QPushButton, QListWidget, QFileDialog, QMenu, QAction
from pynput import mouse, keyboard
import resource  # 图片文件
from BaseSignal import BaseSignal
import BusyUtil

from TrayIcon import TrayIcon


class RelaxWindow(QMainWindow):
    """
    主界面
    """
    default_config = {"waiting_time": 300, "player": "default", "play_list": []}  # 默认配置

    def __init__(self):
        super().__init__()
        self.config = []
        self.working_flag = True

        # 读取配置
        self.read_config()

        # 初始化界面
        self.initUI()

        # 创建定时器
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.play)

        # 创建信号
        self.start_timer_signal = BaseSignal()
        self.start_timer_signal.connect(self.start_timer)
        self.start_timer_signal.emit()

        # 子线程监听是否有鼠标活动
        t_mouse = Thread(target=self.listen_mouse_activity)
        t_mouse.setDaemon(True)
        t_mouse.start()

        # 子线程监听是否有键盘活动
        t_keyboard = Thread(target=self.listen_keyboard_activity)
        t_keyboard.setDaemon(True)
        t_keyboard.start()

        # 避免电脑休眠
        t_wakeup = Thread(target=BusyUtil.wakeup)
        t_wakeup.setDaemon(True)
        t_wakeup.start()

    def listen_keyboard_activity(self):
        """
        监听键盘活动
        """
        with keyboard.Listener(on_press=lambda key: self.start_timer_signal.emit(),
                               on_release=lambda key: self.start_timer_signal.emit()) as listener:
            listener.join()

    def listen_mouse_activity(self):
        """
        监听是否有鼠标移动 or 点击 or 滑轮活动
        监听到活动就立即重启计时器
        """
        with mouse.Listener(on_move=lambda x, y: self.start_timer_signal.emit(),
                            on_click=lambda x, y, button, pressed: self.start_timer_signal.emit(),
                            on_scroll=lambda x, y, dx, dy: self.start_timer_signal.emit()) as listener:
            listener.join()

    def stop_timer(self):
        self.timer.stop()

    def start_timer(self, seconds=None):
        """
        开启或重启定时器
        """
        try:
            if seconds is None:
                seconds = int(self.waiting_time_edit.text())
        except Exception as e:
            print("seconds error", e)
            return

        if seconds > 0 and self.working_flag:
            print("start_timer", seconds, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            self.timer.start(seconds * 1000)

    def set_working_flag(self, flag: bool):
        self.working_flag = flag

    def start_working(self):
        self.working_flag = True
        self.setWindowIcon(QIcon(":/logo.png"))

    def stop_working(self):
        self.working_flag = False
        self.setWindowIcon(QIcon(":/logo_grey.png"))


    def is_working(self):
        return self.working_flag

    def play(self):
        """
        运行指定程序，随机选择文件夹中的某个文件，然后打开
        """
        print("play")
        if self.working_flag is False:
            return

        # 是否正在播放
        if BusyUtil.is_playing(self.player_path_label.text()):
            self.start_timer(1)

        # 电脑是否忙碌
        if BusyUtil.is_busy():
            self.start_timer()

        # 随机选择一个目录
        dir_list = []
        count = self.play_list_widget.count()
        for i in range(count):
            s = self.play_list_widget.item(i).text()
            dir_list.append(s)
        if len(dir_list) == 0:
            return
        while True:
            # 可能存在文件夹都被删除的情况
            if len(dir_list) == 0:
                return
            chosen_dir = choice(dir_list)
            if not os.path.exists(chosen_dir):
                dir_list.remove(chosen_dir)
            else:
                print("choose dir", chosen_dir)
                break

        # 随机选择一个文件
        name_list = os.listdir(chosen_dir)
        while True:
            file_name = choice(name_list)
            file_path = chosen_dir + "/" + file_name
            if os.path.isfile(file_path):
                break

        # 开启子线程，在子线程中启动 windows 程序（因为启动 windows 程序会阻塞）
        player = self.player_path_label.text()
        t = Thread(target=lambda: self.t_play(player, file_path))
        t.setDaemon(True)
        t.start()

    def t_play(self, player, file_path):
        """
        启动 windows 程序，打开指定文件
        :param player:
        :param file_path:
        :return:
        """
        print("player", player)
        print("file_path", file_path)
        if player != "default":
            exe = "\"%s\"" % (player.replace('\\', '/'))  # 指定的程序
            print("exe", exe)
            os.system("%s %s" % (exe, file_path))
        else:
            os.startfile(file_path)  # 模拟双击打开文件的效果
        print("t_play end")

    def initUI(self):
        """
        初始化界面
        """
        self.setWindowTitle("Relax Time")
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowMinimizeButtonHint & ~Qt.WindowMaximizeButtonHint)  # 取消最小化最大化按钮

        # 从 resource.py 文件中读取 logo.png
        self.setWindowIcon(QIcon(":/logo.png"))

        # 等待时间
        waiting_time_label = QLabel("等待时间：")
        self.waiting_time_edit = QLineEdit()
        self.waiting_time_edit.setText(str(self.config["waiting_time"]))
        self.waiting_time_edit.setValidator(QIntValidator(0, 65535))
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

        # 读取配置
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                try:
                    self.config = json.load(file)
                except Exception as e:
                    print("配置文件 json.load error，使用默认配置")
                    self.config = self.default_config.copy()
                    print(e)
                    return

                # 进行检查
                if type(self.config["waiting_time"]) != int or self.config["waiting_time"] <= 0:
                    self.config["waiting_time"] = self.default_config["waiting_time"]
                if not os.path.isfile(self.config["player"]):
                    self.config["player"] = "default"
                for i, play_dir in enumerate(self.config["play_list"]):
                    if not os.path.exists(play_dir):
                        self.config["play_list"].pop(i)
        else:
            self.config = self.default_config.copy()

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
        print("保存配置文件", self.get_config_file_path())

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
        self.save_config()
        event.ignore()  # 忽略该事件
        self.hide()  # 隐藏窗口

    def exit(self):
        """
        退出程序

        timer 必须自己手动关闭，不然 timer 线程不会结束（但是不清楚到时间了会不会退出），程序也不会结束
        """
        self.timer.stop()
        self.save_config()
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
