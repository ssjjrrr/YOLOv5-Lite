import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time

count =0

# 回调函数 必须有一个输入就是引脚编号
# def button_push(pin):
    # global count
    # count = count+1
    # print(pin,count)
    # print("Button was pushed!")


def button_push(pin):
    
    if GPIO.input(pin) == GPIO.HIGH:

        global count
        count = count+1
        print(pin,count)
        print("Button was pushed!")




if __name__ == "__main__":
    
    # 设置引脚
    pin_Btn = pin_dic['G16']
    
    # 设置引脚编号模式
    GPIO.setmode(GPIO.BOARD) 
    
    # 设置按键引脚工作方式，
    GPIO.setup(pin_Btn,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # 定义回调函数
    # GPIO.add_event_detect(pin_Btn, GPIO.RISING, callback=button_push, bouncetime=200)
    GPIO.add_event_detect(pin_Btn, GPIO.BOTH, callback=button_push, bouncetime=200)
    
   
    
    try:
        while True: # Run forever
            pass 
            
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
    finally:
        GPIO.cleanup()
            
    