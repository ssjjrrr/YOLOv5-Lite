import snowboydecoder
import sys
import signal
from pin_dic import pin_dic
from light import light
import threading
from buzzer import Runing_Song
import time

# 定义小灯对象
global m_light
m_light = light(pin_dic["G17"])

#  蜂鸣器
global m_runing_song
m_runing_song = Runing_Song(pin_dic['G18'])


def callbakck_light_on():
    global m_light
    m_light.on()
    print("light_on")

def callbakck_light_off():
    global m_light
    m_light.off()
    print("light_off")


def callbakck_music_on():
    global m_runing_song
    if m_runing_song.isAlive() == False:
        # 没有线程 创建线程并启动
        m_runing_song = Runing_Song(pin_dic['G18'])
        m_runing_song.file_load('music.txt')

        m_runing_song.setDaemon(True)
        m_runing_song.start()
        
    else: 
        # 如果正在演奏，先停止
        m_runing_song.dostop()
        time.sleep(0.1)
        m_runing_song.join()

        # 重新加载
        m_runing_song = Runing_Song(pin_dic['G18'])
        flag = m_runing_song.file_load('music.txt')
        m_runing_song.setDaemon(True)
        m_runing_song.start()
    print("music_on")


def callbakck_music_off():
    global m_runing_song
    if m_runing_song.isAlive() == True:
        m_runing_song.dostop()
        time.sleep(0.1)
        m_runing_song.join()  
    print("music_off")


interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
  
    return interrupted


if __name__ == "__main__":
    
    # 定义模型以及相应的相应函数
    models = ['lighton.pmdl','lightoff.pmdl','music_on.pmdl','music_off.pmdl']
    callbacks = [lambda:callbakck_light_on(),
                lambda:callbakck_light_off(),
                lambda:callbakck_music_on(),
                lambda:callbakck_music_off()]

    # 定义检测器
    signal.signal(signal.SIGINT, signal_handler)
    sensitivity = [0.5]*len(models)
    detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
    print('开始检测')

    # 主循环，每隔一段时间检测一次
    detector.start(detected_callback=callbacks,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

    detector.terminate()
    
