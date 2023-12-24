
import threading
import RPi.GPIO as GPIO
from pin_dic import pin_dic
import numpy as np
import time
class Runing_Song(threading.Thread):
    def __init__(self,pin):
        super(Runing_Song, self).__init__() 
        
        # 设 置 蜂 鸣 器 引 脚 模 式
        self.pin_buzzer = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_buzzer,GPIO.OUT)
        
        self.delay_beat = 0.2
        
        self.freqs = []
        self.beats = []
        
        self.flag_stop = False
       

    def file_load(self,file_music):
        
        # 从文件中加载乐谱数据
        data = np.loadtxt(file_music,dtype = 'str')
        [n,d] = np.shape(data)
    
        # 必须是3列
        if not d==3:
            return False,0,0 
        # 预先定义好的音符频率
        CL = [0, 131, 147, 165, 175, 196, 211, 248]        
        CM = [0, 262, 294, 330, 349, 392, 440, 494]       
        CH = [0, 525, 589, 661, 700, 786, 882, 990] 
            
    
        # 第一列音高 第二列音频 第三列音长
        levels = data[:,0]
        beats = data[:,2]
        beats = beats.astype('int32')
        labs =  data[:,1]
        labs = labs.astype('int32')

        # 生成乐谱
        self.freqs  = []
        for i in range(n):
            if levels[i]=='H':
                self.freqs.append(CH[labs[i]])
            elif levels[i] == 'M':    
                self.freqs.append(CM[labs[i]])
            elif levels[i] == 'L':
                self.freqs.append(CL[labs[i]])

        self.beats = beats.tolist()
        
        if not len(self.freqs)==len(self.beats):
            return False
        else:
            return True
    
    
    def dostop(self):
        self.flag_stop = True
        

    def run(self):
        
        self.flag_stop = False
        
        # 定义PWM对象
        Buzzer = GPIO.PWM( self.pin_buzzer , 440)
        Buzzer.start(50)
        while True:
            if self.flag_stop:
                break
            for freq,beat in zip(self.freqs,self.beats):
                if self.flag_stop:
                    break
                Buzzer.ChangeFrequency(freq)
                time.sleep(self.delay_beat*beat)
                
        Buzzer.stop()        
        GPIO.output(self.pin_buzzer, GPIO.LOW)
        
        self.flag_stop = False
        

if __name__ == "__main__":
    
    file = "music.txt"
    
    
    m_runing_song = Runing_Song(pin_dic['G18'])
    
    print(" runing  1")
    if m_runing_song.isAlive() == False:
        # 没有线程 创建线程并启动
        m_runing_song = Runing_Song(pin_dic['G18'])
        flag = m_runing_song.file_load(file)
        m_runing_song.setDaemon(True)
        m_runing_song.start()
        
    else:
        # 如果正在演奏，先停止
        m_runing_song.dostop()
        time.sleep(0.1)
        m_runing_song.join()
        
        # 重新加载
        m_runing_song = Runing_Song(pin_dic['G18'])
        flag = m_runing_song.file_load(file)
        m_runing_song.setDaemon(True)
        m_runing_song.start()
        
    time.sleep(5)
    
    
    print(" runing  2")
    if m_runing_song.isAlive() == False:
        # 没有线程 创建线程并启动
        m_runing_song = Runing_Song(pin_dic['G18'])
        flag = m_runing_song.file_load(file)
        m_runing_song.setDaemon(True)
        m_runing_song.start()
        
    else:
        # 如果正在演奏，先停止
        m_runing_song.dostop()
        time.sleep(0.1)
        m_runing_song.join()
        
        # 重新加载
        m_runing_song = Runing_Song(pin_dic['G18'])
        flag = m_runing_song.file_load(file)
        m_runing_song.setDaemon(True)
        m_runing_song.start()
        
    time.sleep(5)
    
    print("stop 1")
    if m_runing_song.isAlive() == True:
        m_runing_song.dostop()
        time.sleep(0.1)
        m_runing_song.join()
        
    time.sleep(5)
    
    print("stop 2")
    if m_runing_song.isAlive() == True:
        m_runing_song.dostop()
        time.sleep(0.1)
        m_runing_song.join()  

    time.sleep(5)
    print(" runing  3")
    if m_runing_song.isAlive() == False:
        # 没有线程 创建线程并启动
        m_runing_song = Runing_Song(pin_dic['G18'])
        flag = m_runing_song.file_load(file)
        m_runing_song.setDaemon(True)
        m_runing_song.start()
        
    else:
        # 如果正在演奏，先停止
        m_runing_song.dostop()
        time.sleep(0.1)
        m_runing_song.join()
        
        # 重新加载
        m_runing_song = Runing_Song(pin_dic['G18'])
        flag = m_runing_song.file_load(file)
        m_runing_song.setDaemon(True)
        m_runing_song.start()
        
    time.sleep(5)
    
    

        
         
    
    
    
    
    
    
        
        
        
        
    
    
    
    
    # print("first runing")
    # if m_runing_song.get_running_state() == True:
        
        # # 如果正在演奏，先停止
        # print(1)
        # m_runing_song.dostop()
        # time.sleep(0.1)
        # m_runing_song.join()
        # m_runing_song.start()
    # else:
        # print(2)
        # m_runing_song.start()
        
    # time.sleep(5)

    # print("second runing")
    # if m_runing_song.get_running_state() == True:
        # print(3)
        # # 如果正在演奏，先停止
        # m_runing_song.dostop()
        # time.sleep(0.1)
        # m_runing_song.join()
        
        # # 重新加载
        # print(m_runing_song.isAlive())
        # m_runing_song = Runing_Song(pin_dic['G18'])
        # flag = m_runing_song.file_load(file)
        # m_runing_song.setDaemon(True)
        # m_runing_song.start()
       
    # else:
        # print(4)
        # m_runing_song.start()
    
    # time.sleep(5)
    # print('stop')
    
    # m_runing_song.dostop()
    # time.sleep(0.1)
    # m_runing_song.join()
    
    
    
    # time.sleep(3)
    
    # print("third runing")
    # print(m_runing_song.isAlive())
    # if m_runing_song.isAlive() == True:
        # print(3)
        # # 如果正在演奏，先停止
        # m_runing_song.dostop()
        # time.sleep(0.1)
        # m_runing_song.join()
        
        # # 重新加载
        # print(m_runing_song.isAlive())
        # m_runing_song = Runing_Song(pin_dic['G18'])
        # flag = m_runing_song.file_load(file)
        # m_runing_song.setDaemon(True)
        # m_runing_song.start()
       
    # else:
        # print(4)
        # m_runing_song.start()
    
    
    


        
        
        
    
    
    # print("开始奏乐1")
    # if flag_play_first:
        
        # m_runing_song.start()
        # flag_play_first = False
    # else:
        # m_runing_song.dostop()
        # id_thread = m_runing_song.run()
        
        
    
    # time.sleep(5)
    
    # print("开始奏乐2")
    

    # if flag_play_first:
        
        # m_runing_song.start()
    # else:
        # print(1)
        # m_runing_song.dostop()
        # print(2)
        # id_thread = m_runing_song.run()
        # print(3)
        # flag_play_first = False
    
        
    
        
        
        
        
    
    
    
    
 
    