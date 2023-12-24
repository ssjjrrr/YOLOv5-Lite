from test_LCD import LCD_1602
from test_ds1302 import DS1302
import RPi.GPIO as GPIO
from pin_dic import pin_dic
from datetime import datetime
import time


if __name__ == "__main__":
    
    # ds1302 初始化
    pin_clk = pin_dic['G4']
    pin_dat = pin_dic['G5']
    pin_rst = pin_dic['G6']
    
    GPIO.setmode(GPIO.BOARD)
    
    m_ds1302 = DS1302(pin_clk,pin_dat,pin_rst)
    # 写入当前时间
    x = datetime.now()
    m_ds1302.write_DateTime(x)
    
    # LCD 1602 初始化
    m_lcd = LCD_1602(Address=0x27,bus_id=1,bl=1)
    flag =m_lcd.lcd_init()
    print(flag)
    
    
    try:
        while True:
            dt = m_ds1302.read_DateTime()
            
            if not dt:
                continue
            else:
                str_time1 = dt.strftime("%a %Y-%m-%d")
                str_time2 = dt.strftime("%H:%M:%S")
                # print("\r%s"%(str_time),end="")
                m_lcd.lcd_display_string(0,0,str_time1)
                m_lcd.lcd_display_string(0,1,str_time2)
                
            
        
        
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
    
    finally:
    
        GPIO.cleanup()
    