# 目标
电脑空闲超过设定时间时，随机播放视频。

# 文件说明
- resource.py：根据 resource.qrc 生成的图片文件，工具为 pyrcc5(PyQt5 自带)，这样图片文件就变成了 *.py，方便 pyinstaller 打包。
例如，pyrcc5 -o resource.py ./img/resource.qrc

- MainWindow.spec：pyinstaller 自动生成的
- requirement.txt: 依赖项，安装本项目依赖使用命令 pip install requirement.txt


# 思路
问：如何定义电脑空闲状态？
答：一段时间内无鼠标、键盘操作 + CPU<10% + DISK<10% + Network<10% + GPU<10%，同时满足条件就算作空闲



问：电脑空闲时间过长，会不会触发休眠？触发休眠条件是什么？如何阻止休眠？
答：


问：已经在播放视频了，用户没有操作，定时器计时，到时间了又打开新的文件进行播放？
这样的设定带来的问题就是一个视频只能播放定时器触发时常的时间。
想要实现的目标是播放完一个视频接着播放下一个视频。
答：进入检测模式，1s 检测 1 次是否空闲，停止播放了（也就是进入了空闲状态）就立即开始新的播放。

问：如何定义正在播放？
答：播放器进程存在 && 播放器进程 CPU 利用率 > 0.1%

问：要是用户正在用其它播放器播放视频怎么办？
答：判断是否处于空闲状态即可


# 难点（具体实现）
[] 如何读取 GPU 利用率？
[] 如何判断是否有音频输出？

# 其它问题
当其它窗口置于顶层时，pynput 捕捉不到鼠标和键盘活动


# 啰里啰唆
之前电脑空闲加入了音频输入输出检测，但仔细想了想，要是挂机，有 QQ 提示音怎么办？还是取消音频检测吧。

使用 PyInstaller 生成的 exe 文件实在是太大了，居然有 37M，感觉就这么点功能应该就几 M。
