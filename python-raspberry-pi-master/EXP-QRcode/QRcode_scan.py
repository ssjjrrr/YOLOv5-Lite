import cv2
import os
import time
import RPi.GPIO as GPIO
from pin_dic import pin_dic

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
            
class light(object):
    
    def __init__(self,pin):
        
        # 初始化
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)       
        GPIO.setup(self.pin, GPIO.OUT)   
        GPIO.output(self.pin, GPIO.LOW)
    
    # 开灯
    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
    # 关灯    
    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
        
class Buzzer(object):
    
    def __init__(self,pin):
        
        # 初始化
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)       
        GPIO.setup(self.pin, GPIO.OUT)   
        GPIO.output(self.pin, GPIO.HIGH)
    
    # 响
    def on(self):
        GPIO.output(self.pin, GPIO.LOW)
    # 不响    
    def off(self):
        GPIO.output(self.pin, GPIO.HIGH)        

if __name__ == "__main__":
    
    # flag_list = ["light-on","light-off","temperature","buzzer-on","buzzer-off"]
    
    # 构造温度采集对象
    m_ds18b20 = Ds18b20('28-0300a27926e3')
    
    # 构造小灯对象
    m_light = light( pin_dic['G17'])
    
    # 构造蜂鸣器对象
    m_buzzer = Buzzer(pin_dic['G16'])
   
    flag_pass = " "
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    # 二维码 检测器
    QR_detector = cv2.QRCodeDetector()
 
    try :
        while True:
            success, img = cap.read()
            if not success:
                print('error input')
                continue
                
            # cv2.imshow("img",img)
            # if cv2.waitKey(5) & 0xFF == ord('q'):
                # break
                
            # 二维码检测
            flag_now,_,_ =QR_detector.detectAndDecode(img) 
            
            if flag_now:
                
                if flag_now == flag_pass:
                    continue
                flag_pass = flag_now
                                
                if flag_pass == "light-on":
                    m_light.on()
                    print("light on")
                    
                elif flag_pass == "light-off":
                    m_light.off()
                    print("ligh off")
                    
                elif flag_pass == "buzzer-on":
                    m_buzzer.on()
                    print("buzzer on")
                    
                elif flag_pass == "buzzer-off":
                    m_buzzer.off()
                    print("buzzer off")
                    
                elif flag_pass == "temperature":
                    t = m_ds18b20.read()
                    print(t)
            
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
        
    finally:
        
        GPIO.cleanup()  
    
    cap.release() 