import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time


class HC_SR04(object):
    
    def __init__(self,pin_trig,pin_echo):
        self.pin_trig = pin_trig
        self.pin_echo = pin_echo
        
        GPIO.setup(self.pin_trig, GPIO.OUT)
        GPIO.setup(self.pin_echo, GPIO.IN)
        self.time_tol = 3
        
    def get_distance(self):
        s_time = time.time()
        # 在TRIG引脚上输出一个正向脉冲
        GPIO.output(self.pin_trig, 0)
        time.sleep(0.000002)

        GPIO.output(self.pin_trig, 1)
        time.sleep(0.00001)
        
        GPIO.output(self.pin_trig, 0)
    
        # 等待ECHO引脚上高电平出现
        while GPIO.input(pin_echo) == 0:
            if time.time()-s_time > self.time_tol:
                return False
        
        # 记录高电平出现时间    
        time1 = time.time()
        
        # 等待ECHO引脚上高电平结束
        while GPIO.input(pin_echo) == 1:
            if time.time()-s_time > self.time_tol:
                return False
                
        # 记录高电平结束时间    
        time2 = time.time()
       
        # 计算ECHO引脚上高电平持续时间
        during = time2 - time1
        
        # 计算距离 单位cm
        dis = during * 344 / 2 * 100
        return dis
        
    def destory(self):
        GPIO.cleanup() 
        
if __name__ == "__main__":
    
    pin_trig = pin_dic['G6']
    pin_echo = pin_dic['G5']
    
    GPIO.setmode(GPIO.BOARD)
    
    m_HC_SR04 = HC_SR04(pin_trig,pin_echo)
    
    try:
        # 主循环
        while True:
            dis = m_HC_SR04.get_distance()
            if dis:
                print('%.2f cm'%(dis))
                print (' ')
            else:
                print("Error")
            
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')    
    finally:
        m_HC_SR04.destory()

    
    
    
    
    
    
    
    
    
    
        
    
    