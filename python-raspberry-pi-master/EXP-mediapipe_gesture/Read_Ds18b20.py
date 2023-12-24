import time
import threading
import os
import RPi.GPIO as GPIO

class Ds18b20(object):
    
    def __init__(self,str_id):
        self.str_id = str_id
        
    def read(self):
        # 读取温度传感器的数值
        location = os.path.join( "/sys/bus/w1/devices",self.str_id,"w1_slave") 

        if os.path.exists(location):
            with open(location) as tf:
                lines = tf.read().splitlines()
            
            text = lines[-1]
            temperaturedata = text.split(" ")[-1]
            
            temperature = float(temperaturedata[2:])
            
            return temperature/1000.0
        else:
            return False
            
class Read_Ds18b20(threading.Thread):
    
    def __init__(self,str_id):
        super(Read_Ds18b20, self).__init__() 
        self.str_id = str_id
        
        self.m_ds18b20 =  Ds18b20(self.str_id)
        self.temperature = None
        self.flag_run = 0
        self.flag_break =0
        
    def dostart(self):
        self.flag_run = 1
        
    def dostop(self):
        self.flag_run = 0
        
    def dobreak(self):
        self.flag_break = 1
        
    def getState(self):
        return self.flag_run
        
    def run(self):
        
        while True:
            
            if  self.flag_break:
                break
            
            if self.flag_run:
                
                t = self.m_ds18b20.read()
                
                if t:
                    self.temperature = t
                else:
                    self.temperature = None
            else:
                self.temperature = None
            
            time.sleep(0.5)
            
    def get_temperature(self):
        return self.temperature
        
            
if __name__ == "__main__":
    
    #定义线程对象 
    str_id = "28-0300a2794829"
    m_read_Ds18b20 =  Read_Ds18b20(str_id)
    m_read_Ds18b20.setDaemon(True)
    
    # 启动温度读取线程
    if not m_read_Ds18b20.getState():
        m_read_Ds18b20.dostart()
        m_read_Ds18b20.start()
        
    print("run")
    result = m_read_Ds18b20.get_temperature()
    print(result)
    time.sleep(1)
    
    result = m_read_Ds18b20.get_temperature()
    print(result)
    time.sleep(1)
    
    
    result = m_read_Ds18b20.get_temperature()
    print(result)
    time.sleep(1)
    
    
    result = m_read_Ds18b20.get_temperature()
    print(result)
    time.sleep(1)
    
    print("stop")
    m_read_Ds18b20.dostop()
    
    result = m_read_Ds18b20.get_temperature()
    print(result)
    time.sleep(1)
    
    result = m_read_Ds18b20.get_temperature()
    print(result)
    time.sleep(1)
    
    
    result = m_read_Ds18b20.get_temperature()
    print(result)
    time.sleep(1)
    
    print("break")
    m_read_Ds18b20.dobreak()
    time.sleep(2)
    # GPIO.cleanup()   
    
    
    
                
                
                
            
            
            
        
        
        
        
        
        
        
        