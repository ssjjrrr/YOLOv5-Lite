import RPi.GPIO as GPIO
import os
import time

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
            


if __name__ == "__main__":
    
    str_id = "28-0300a2794829"
    m_ds18b20 =  Ds18b20(str_id)
    
    try:
        while True:
            
            t = m_ds18b20.read()
            
            if t:
                print("\r温度：%2.2f"%(t),end="")
                # print(t)
            else:
                print("error")
            
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Ctrl + C Quite")
            
            
            
            
            
            
            
    
    
    
    
    