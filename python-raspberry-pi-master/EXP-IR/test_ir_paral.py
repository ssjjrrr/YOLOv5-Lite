import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time
from test_DHT11 import DHT11
import lirc
import threading

class Runing_LED(threading.Thread):
    def __init__(self,pins,colors):
        super(Runing_LED, self).__init__() 
        
        self.pins = pins
        self.colors = colors
        self.f_running = False
        self.f_pause = False
    
    
    def dostart(self):
        
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)   
            GPIO.output(pin, GPIO.LOW)
            
         # 设置三个引脚为pwm对象，频率2000
        self.pwm_R = GPIO.PWM(self.pins[0], 2000)  
        self.pwm_G = GPIO.PWM(self.pins[1], 2000)
        self.pwm_B = GPIO.PWM(self.pins[2], 2000)
    
        # 初始占空比为0
        self.pwm_R.start(0)      
        self.pwm_G.start(0)
        self.pwm_B.start(0)
        
        
    def dostop(self):
        self.pwm_R.stop()
        self.pwm_G.stop()
        self.pwm_B.stop()
        for pin in self.pins:
            GPIO.output(pin, GPIO.HIGH)
    
    def color2ratio(self,x,min_color,max_color,min_ratio,max_ratio):
        return (x - min_color) * (max_ratio - min_ratio) / (max_color - min_color) + min_ratio

    def setColor(self,col):
        R_val,G_val,B_val = col
            
        R =self.color2ratio(R_val, 0, 255, 0, 100)
        G =self.color2ratio(G_val, 0, 255, 0, 100)
        B =self.color2ratio(B_val, 0, 255, 0, 100)
       
        # 改变占空比
        self.pwm_R.ChangeDutyCycle(R)     
        self.pwm_G.ChangeDutyCycle(G)
        self.pwm_B.ChangeDutyCycle(B)
        
    def run(self):
        
        self.dostart()
        self.f_running = True
        
        while True:
            for col in self.colors:
                
                if not self.f_running:
                    self.dostop()
                    self.f_running = False
                    return
                    
                while self.f_pause:
                    if not self.f_running:
                        self.dostop()
                        return
                    else:
                        pass
                
                # 设置颜色
                self.setColor(col)
                # 延时
                time.sleep(1)
    
    def stop(self):
        self.f_running = False
       
    def pause(self):
        self.f_pause = True

    def resume(self):
        self.f_pause = False
  
  
class Runing_Song(threading.Thread):
    def __init__(self,pin,notes,beats):
        super(Runing_Song, self).__init__() 
        
        # 设 置 蜂 鸣 器 引 脚 模 式
        self.pin_buzzer = pin
        GPIO.setup(self.pin_buzzer,GPIO.OUT)

        self.note2freq = {"cl1":131,"cl2":147 ,'cl3':165 ,"cl4":175 ,"cl5":196 ,"cl6":211 ,"cl7":248,
                          "cm1":262,"cm2":294 ,'cm3':330 ,"cm4":350 ,"cm5":393 ,"cm6":441 ,"cm7":495,
                          "ch1":525,"ch2":589 ,'ch3':661 ,"ch4":700 ,"ch5":786 ,"ch6":882 ,"ch7":990
                          }
        self.delay_beat = 0.3
        
        self.f_running = False
        self.f_pause = False


    def dostart(self):
        # 创 建PWM对 象 初 始 频 率 440 占 空 比 50%
        self.Buzzer = GPIO.PWM( pin_buzzer , 440)
        self.Buzzer.start(50)
        
    def dostop(self):
        self.Buzzer.stop()
        GPIO.output(self.pin_buzzer, GPIO.LOW)
    
    
    def run(self):
        self.dostart()
        self.f_running = True
        
        while True:
            for note,beat in zip(notes,beats):
            
                if not self.f_running:
                    self.dostop()
                    self.f_running = False
                    return
                    
                while self.f_pause:
                    if not self.f_running:
                        self.dostop()
                        return
                    else:
                        self.Buzzer.ChangeFrequency(0.1)
                        time.sleep(0.1)
                
                self.Buzzer.ChangeFrequency(self.note2freq[note])
                time.sleep(self.delay_beat*beat)
 
    def stop(self):
        self.f_running = False
       
    def pause(self):
        self.f_pause = True

    def resume(self):
        self.f_pause = False
        
 
        
        
  
if __name__ == "__main__":
    
    GPIO.setmode(GPIO.BOARD)
    
    # LED 小灯
    pin_R = pin_dic['G18']
    pin_G = pin_dic['G19']
    pin_B = pin_dic['G20']
    
   
   
    
    # runing 小灯
    # 定义显示的颜色（R，G，B）
    colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,197,204),(192,255,62),(148,0,211),(118,238,200)];
    pins_LED = [pin_R,pin_G,pin_B]
    m_runing_LED = Runing_LED(pins_LED,colors)
    m_runing_LED.setDaemon(True)
    flag_first_run_LED = True
    
    
    # 测试蜂鸣器
    pin_buzzer = pin_dic['G27']

    notes = ['cm1' ,'cm1' , 'cm1' , 'cl5' , 'cm3' , 'cm3' , 'cm3' , 'cm1' ,
             'cm1' , 'cm3' , 'cm5' , 'cm5' , 'cm4' , 'cm3' , 'cm2' , 'cm2' ,
             'cm3' , 'cm4' , 'cm4' , 'cm3' , 'cm2' , 'cm3' , 'cm1' , 'cm1' ,
             'cm3' , 'cm2' , 'cl5' , 'cl7', 'cm2' , 'cm1']
    beats = [1 , 1 , 2 , 2 , 1 , 1 , 2 , 2 ,
            1 , 1 , 2 , 2 , 1 , 1 , 3 , 1 ,
            1 , 2 , 2 , 1 , 1 , 2 , 2 , 1 ,
            1 , 2 , 2 , 1 , 1 , 3]
    
    flag_first_run_Song = True
    m_runing_song = Runing_Song(pin_buzzer,notes,beats)
    m_runing_song.setDaemon(True)
   
    
    # 测试DHT11
    pin_DHT11 = pin_dic['G16']
    m_DHT11 =  DHT11(pin_DHT11)
    
  
    
    sockid = lirc.init("test_yu", "lircrc_2",blocking=False)
    
    try:
        while True:
            
            code_ir = lirc.nextcode()
            
            if code_ir == [u'DHT']:
                flag, result = m_DHT11.read_DHT()
            
                if flag:
                    print("温度: %-3.1f C\n" % result[0])
                    print("湿度: %-3.1f %% \n" % result[1])
                else:
                    print("ERROR") 
           
            elif code_ir == [u'Run_LED']:

                if  m_runing_LED.f_running:
                    print("stop runing LED")
                    m_runing_LED.stop()
                    
                else:
                    print("start runing LED")
                    
                    if flag_first_run_LED:                        
                        m_runing_LED.start()
                        flag_first_run_LED = False
                    else:
                        m_runing_LED = Runing_LED(pins_LED,colors)
                        m_runing_LED.setDaemon(True)
                        m_runing_LED.start()
              
            elif code_ir == [u'Pause_LED']:
                
                if m_runing_LED.f_pause:
                    print("Resume Runing LED")
                    m_runing_LED.resume()
                else:
                    print("Pause Runing LED")
                    m_runing_LED.pause()
                    
            elif code_ir == [u'Run_Song']:

                if  m_runing_song.f_running:
                    print("stop Song")
                    m_runing_song.stop()
                    
                else:
                    print("start Song")
                    if flag_first_run_Song:
                        m_runing_song.start()
                        flag_first_run_Song = False
                    else:
                        m_runing_song = Runing_Song(pin_buzzer,notes,beats)
                        m_runing_song.setDaemon(True)
                        m_runing_song.start()
              
            elif code_ir == [u'Pause_Song']:
                
                if m_runing_song.f_pause:
                    print("Resume Song")
                    m_runing_song.resume()
                else:
                    print("Pause Song")
                    m_runing_song.pause()
                    
                    
            
            
            # else:
                # print("key %s not find"%(code_ir))
            
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')               
    finally:
        lirc.deinit()
        GPIO.cleanup()   
        
        
    
        
    
    
    
    
    