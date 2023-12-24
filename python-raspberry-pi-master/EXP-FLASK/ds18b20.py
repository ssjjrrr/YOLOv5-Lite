import RPi.GPIO as GPIO
import os
import time
import threading


class Ds18b20(threading.Thread):
    
    def __init__(self,str_id):
        super(Ds18b20, self).__init__() 
        self.str_id = str_id
        self.str_temperature = " "
      
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
         
    def run(self):
        
        while True:
            
            t = self.read()
            
            if t:
                self.str_temperature = "%.2f"%(t) 
            time.sleep(1)
    
    def get_temperature(self):
        return self.str_temperature
        
        
            


if __name__ == "__main__":
              
    str_id = "28-0300a2794829"
    m_ds18b20 =  Ds18b20(str_id)
    m_ds18b20.setDaemon(True)
    m_ds18b20.start()
    
    try:
        while True:
            print(m_ds18b20.get_temperature())
        
            time.sleep(1)
     
    except KeyboardInterrupt:
        print("\n Ctrl + C Quite")
           
    

            
            
            
            
            
            
            
    
    
    
    
    