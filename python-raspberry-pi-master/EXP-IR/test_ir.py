import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time
from test_pwm_led import RGB_LED
from test_pwm_buzzer_song import Buzzer_Song
from test_DHT11 import DHT11
import lirc






if __name__ == "__main__":
    
    GPIO.setmode(GPIO.BOARD)
    
    # LED 小灯
    pin_R = pin_dic['G18']
    pin_G = pin_dic['G19']
    pin_B = pin_dic['G20']
    
    # 蜂鸣器
    pin_buzzer = pin_dic['G27']
    
    # DHT11
    pin_DHT11 = pin_dic['G16']
    
    
    # 测试小灯
    m_RGB_LED = RGB_LED(pin_R,pin_G,pin_B)
    
    
    # 测试蜂鸣器
    m_buzzer_song = Buzzer_Song(pin_buzzer,0.3)
    
    notes = ['cm1' ,'cm1' , 'cm1' , 'cl5' , 'cm3' , 'cm3' , 'cm3' , 'cm1' ,
             'cm1' , 'cm3' , 'cm5' , 'cm5' , 'cm4' , 'cm3' , 'cm2' , 'cm2' ,
             'cm3' , 'cm4' , 'cm4' , 'cm3' , 'cm2' , 'cm3' , 'cm1' , 'cm1' ,
             'cm3' , 'cm2' , 'cl5' , 'cl7', 'cm2' , 'cm1']
    beats = [1 , 1 , 2 , 2 , 1 , 1 , 2 , 2 ,
            1 , 1 , 2 , 2 , 1 , 1 , 3 , 1 ,
            1 , 2 , 2 , 1 , 1 , 2 , 2 , 1 ,
            1 , 2 , 2 , 1 , 1 , 3]
   
    
    # 测试DHT11
  
    m_DHT11 =  DHT11(pin_DHT11)
    
   
        
    sockid = lirc.init("test_yu", "lircrc",blocking=False)
    # sockid = lirc.init("test_yu", "lircrc")

    try:
        while True:
            
            code_ir = lirc.nextcode()
           
            if code_ir == [u'red']:
                print("红灯")
                m_RGB_LED.setColor((255,0,0))
            
            elif code_ir == [u'green']:
                print("绿灯")
                m_RGB_LED.setColor((0,255,0))
            
            elif code_ir == [u'blue']:
                print("蓝灯")
                m_RGB_LED.setColor((0,0,255))
            
            elif code_ir == [u'DHT']:
                flag, result = m_DHT11.read_DHT()
        
                if flag:
                    print("温度: %-3.1f C\n" % result[0])
                    print("湿度: %-3.1f %% \n" % result[1])
                else:
                    print("ERROR") 
                    
            elif code_ir == [u'Song']:
                m_buzzer_song.play_song(notes,beats)
                
            else:
                print("key %s not find"%(code_ir))          
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')               
    finally:
        lirc.deinit()
        GPIO.cleanup()   
        
        
    
        
    
    
    
    
    