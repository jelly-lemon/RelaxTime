"""
判断电脑是否忙碌的相关函数
"""
import ctypes
from time import sleep

import wmi


def get_cpu_usage(exe_name=None):
    """
    获取 cpu 占用率

    :param exe_name: 进程名
    :return: cpu 占用率，0~1
    """
    w = wmi.WMI()
    if exe_name is None:
        cpu = w.Win32_Processor()[0]    # 默认第一颗 CPU
        print("cpu usage", cpu.LoadPercentage)
        return cpu.LoadPercentage
    else:
        # TODO 获取特定进程的 cpu 占用率
        return 0

def get_disk_usage():
    """
    TODO 获取磁盘占用率（指忙碌程度，而不是空间大小）
    """
    return 0

def get_gpu_usage():
    """
    TODO 获取 GPU 占用率
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
    threshold = 0.1 # 忙碌阈值

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
    TODO 是否正在播放视频

    :param player: 播放器名字
    """
    if player == "default":
        player = get_default_player()

    return False

def get_default_player():
    """
    TODO 获取默认播放器名字
    """
    pass

def wakeup():
    """
    避免电脑进入休眠模式
    TODO 还未测试是否可行
    """
    while True:
        print("wakeup")
        ctypes.windll.kernel32.SetThreadExecutionState(0x00000002)
        sleep(60)