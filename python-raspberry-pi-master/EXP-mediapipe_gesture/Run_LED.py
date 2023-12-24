import threading
import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time


class Color_LED(object):
    def __init__(self,pins):
        
        self.pins = pins
        
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        
        self.pwm_R = GPIO.PWM(self.pins[0], 2000)  
        self.pwm_G = GPIO.PWM(self.pins[1], 2000)
        self.pwm_B = GPIO.PWM(self.pins[2], 2000)
        
        # 初始占空比为0
        self.pwm_R.start(0)      
        self.pwm_G.start(0)
        self.pwm_B.start(0)
        
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
    

        
    
        
class Run_LED(threading.Thread):
    
    def __init__(self,pins,colors):
        super(Run_LED, self).__init__()

        self.m_led = Color_LED(pins)
        self.flag_run = 0
        self.colors = colors
        self.flag_beak = 0
        
    def dobreak(self):
        self.flag_beak = 1
        
    def dostart(self):
        self.flag_run = 1
        
    def dostop(self):
        self.flag_run = 0
        
    def getState(self):
        return self.flag_run
        
    def run(self):
        
        while True:
            for col in self.colors:
                
                if self.flag_beak:
                    break
                
                if not self.flag_run:
                    col_show=(0,0,0)
                else: 
                    col_show= col 
                
                # 设置颜色
                self.m_led.setColor(col_show)
                # 延时
                time.sleep(1)
        
        
if __name__ == "__main__":
    
    GPIO.setmode(GPIO.BOARD)
    
    # LED 小灯
    pin_R = pin_dic['G12']
    pin_G = pin_dic['G6']
    pin_B = pin_dic['G5']
    colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,197,204),(192,255,62),(148,0,211),(118,238,200)];
    pins_LED = [pin_R,pin_G,pin_B]
    
    m_runing_LED = Run_LED(pins_LED,colors)
    m_runing_LED.setDaemon(True)
    
    if not m_runing_LED.getState():
        m_runing_LED.dostart()
        m_runing_LED.start()
        
    
    print("run")    
    time.sleep(10)
    
    print("stop")
    m_runing_LED.dostop()
    time.sleep(5)
    
    
    print("run")    
    m_runing_LED.dostart()
    time.sleep(10)
    
    m_runing_LED.dobreak()
    time.sleep(5)
    GPIO.cleanup() 
        
        
        
        
    
    
        
        
        
        