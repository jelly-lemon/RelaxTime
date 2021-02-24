import json
import os
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, \
    QPushButton, QListWidget, QListWidgetItem, QFileDialog, QMenu, QAction, QMessageBox

from TrayIcon import TrayIcon


class DirListItem(QListWidgetItem):
    def __init__(self):
        super().__init__()


class RelaxWindow(QMainWindow):
    config = {"waiting_time": 300, "player": "default", "play_list": ["test1", "test2"]}

    def __init__(self):
        super().__init__()

        self.read_config()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Relax Time")

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
        self.player_change_btn = QPushButton("更换")
        self.player_change_btn.clicked.connect(self.show_choose_player_dialog)
        player_layout = QHBoxLayout()
        player_layout.addWidget(player_label)
        player_layout.addWidget(self.player_path_label)
        player_layout.addWidget(self.player_change_btn)

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
        self.play_list_widget.customContextMenuRequested[QPoint].connect(self.show_menu)

        # 保存配置
        save_btn = QPushButton("保存配置")
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
        item = self.play_list_widget.currentItem()
        row = self.play_list_widget.row(item)
        self.config["play_list"].pop(row)
        self.play_list_widget.takeItem(row)

    def show_choose_player_dialog(self):
        # 两个返回值分别是什么呢？
        filename, _ = QFileDialog.getOpenFileName()
        self.player_path_label.setText(filename)

    def show_choose_play_dir_dialog(self):
        dir = QFileDialog.getExistingDirectory()
        self.config["play_list"].append(dir)
        self.play_list_widget.addItem(dir)

    def read_config(self):
        config_path = self.get_config_file_path()

        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                self.config = json.load(file)

    def get_config_file_path(self):
        config_dir = os.environ['TEMP']
        return config_dir + "/relax_time.config"

    def save_config(self):
        self.config["waiting_time"] = self.waiting_time_edit.text()
        self.config["player"] = self.player_path_label.text()
        self.config["play_list"] = []

        count = self.play_list_widget.count()
        for i in range(count):
            self.config["play_list"].append(self.play_list_widget.item(i).text())
        config_path = self.get_config_file_path()
        with open(config_path, "w") as file:
            json.dump(self.config, file)

    def show_menu(self):
        popMenu = QMenu()
        delete_action = QAction("删除")
        delete_action.triggered.connect(self.delete_play_dir)
        popMenu.addAction(delete_action)
        popMenu.exec_(QCursor.pos())

    def closeEvent(self, event):
        # reply = QMessageBox.question(self,
        #                              '提示',
        #                              "是否保存配置？",
        #                              QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        #                              QMessageBox.Yes)
        # if reply == QMessageBox.Yes:
        #     self.save_config()
        #     event.accept()
        #     sys.exit(0)
        # elif reply == QMessageBox.No:
        #     event.accept()
        #     sys.exit(0)
        # else:
        #     event.ignore()
        event.ignore()
        self.showMinimized()    # 最小化



if __name__ == '__main__':
    app = QApplication(sys.argv)
    relaxWindow = RelaxWindow()
    relaxWindow.show()

    tray_icon = TrayIcon(relaxWindow)
    tray_icon.show()

    sys.exit(app.exec_())
