"""
判断电脑是否忙碌的相关函数
"""
import ctypes
import winreg
from time import sleep

import psutil
import wmi


def get_cpu_usage(exe_name=None):
    """
    获取 cpu 占用率

    :param exe_name: 进程名
    :return: cpu 占用率，0~100
    """
    w = wmi.WMI()
    if exe_name is None:
        cpu = w.Win32_Processor()[0]    # 默认第一颗 CPU
        cpu_usage = cpu.LoadPercentage
        print("cpu usage", cpu_usage)
        if cpu_usage is not None:
            return cpu_usage
        else:
            return 0
    else:
        # 获取特定进程的 cpu 占用率
        exe_cpu_usage = 0
        for proc in psutil.process_iter():
            if proc.name().lower() == exe_name.lower():
                try:
                    # 如果该进程是多线程，cpu_percent 返回值可能 > 100，返回值是每个逻辑核占用率的累加值
                    # 简单化处理，只获取同名进程里第一个进程的 cpu 占用率
                    exe_cpu_usage += proc.cpu_percent(interval=0.1)
                    break
                except Exception as e:
                    print(e)
        # 保证返回值 0~1 范围内
        if exe_cpu_usage > 100:
            exe_cpu_usage = 100

        return exe_cpu_usage

def get_disk_usage():
    """
    TODO 获取磁盘占用率（指忙碌程度，而不是空间大小）

    如果有多个磁盘，选第一个
    """
    return 0

def get_gpu_usage():
    """
    TODO 获取 GPU 占用率

    如果有多个 GPU，选第一个
    """
    return 0

def get_network_usage():
    """
    TODO 获取网卡占用率
    """
    # 获取正在使用的网卡（如果有多张正在使用的网卡，选第一个）
    return 0

def is_voice():
    """
    TODO 是否正在播放音频
    """
    return False


def is_busy():
    """
    电脑是否忙碌
    """
    threshold = 10 # 忙碌阈值

    if get_cpu_usage() > threshold:
        return True
    if get_disk_usage() > threshold:
        return True
    if get_gpu_usage() > threshold:
        return True
    if get_network_usage() > threshold:
        return True
    if is_voice():
        return True

    return False

def is_playing(player):
    """
    是否正在播放视频

    :param player: 播放器名字
    """
    # 获取系统默认播放器名
    if player == "default":
        player = get_default_player()
        if player is None:
            return False

    # 检测是否存在该进程、是否正在使用 CPU
    if is_running(player) and get_cpu_usage(player) > 0:
        return True

    return False

def is_running(exe_name):
    """
    进程是否正在运行

    :param exe_name: 进程名
    """
    for proc in psutil.process_iter():
        if proc.name().lower() == exe_name.lower():
            return True

    return False

def get_default_player():
    """
    获取默认播放器名字
    """
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"WMP11.AssocFile.MP4\shell\open\command") as key:
        name, value, type = winreg.EnumValue(key, 0)
        print("default player", "name:", name, "value:", value, "type:", type)
        # 按 \ 进行分割，得到文件名开头的字串
        for s in value.split('\\'):
            end = s.find(".exe")  # 得到文件名结束下标
            if end != -1:
                # 提取文件名切片
                return s[:end] + ".exe"
    print("没有提取到播放器名")
    return None


def wakeup():
    """
    避免电脑进入休眠模式，每隔一分钟唤醒一次

    TODO 还未测试是否可行
    """
    while True:
        print("wakeup")
        ctypes.windll.kernel32.SetThreadExecutionState(0x00000002)
        sleep(60)