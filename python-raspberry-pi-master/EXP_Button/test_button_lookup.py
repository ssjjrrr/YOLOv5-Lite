import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time


if __name__ == "__main__":
    
    # 设置引脚
    pin_Btn = pin_dic['G17']
    
    # 设置引脚编号模式
    GPIO.setmode(GPIO.BOARD) 
    
    
    # 设置按键引脚工作方式，
    # 注意 pull_up_down=GPIO.PUD_DOWN 参数表示没有操作时引脚的状态，
    GPIO.setup(pin_Btn,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    try:
        while True: # Run forever
            # 如果获取按键是
            if GPIO.input(pin_Btn) == GPIO.HIGH:
                # 消除抖动
                time.sleep(0.2)
                print("按键按下")
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
    
    finally:
        
        GPIO.cleanup()
            
    