import cv2
import numpy as np
from test_LCD import LCD_1602
import time
from pin_dic import pin_dic
import RPi.GPIO as GPIO

# 预处理提取边缘图像，imgCanny边缘提取
def preProcessing(img,edge_min=18,edge_max=30):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    imgCanny = cv2.Canny(imgBlur,edge_min,edge_max)
    kernel = np.ones((5,5))
    imgDial = cv2.dilate(imgCanny,kernel,iterations=2)
    imgEdge = cv2.erode(imgDial,kernel,iterations=1)
    return imgEdge
    
def ring_off(pin):
    GPIO.output(pin, GPIO.HIGH)

def ring_on(pin):
    GPIO.output(pin, GPIO.LOW)

def det_circle(img):
     
    # 轮廓提取
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    # 对提取的各个轮廓进行遍历
    n_circle = 0
    list_contours = []
    for cnt in contours:        
        # 计算各个轮廓包围的面积
        area = cv2.contourArea(cnt)
        # print(area)
        # print(area)
            
        # 当面积大于500时进行处理
        if area>300:
                
            # 将光滑的轮廓线折线化
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)
                     
            # 根据近似折线段的数目判断目标的形状
            objCor = len(approx)
            
            # 四条以上线段时为圆形
            if objCor>4: 
                n_circle = n_circle+1
                list_contours.append(cnt)
    return n_circle,list_contours
    
    
if __name__ == "__main__":
   
    # 读取摄像头
    cap = cv2.VideoCapture(0)
    
    # 蜂鸣器初始化
    pin_sig = pin_dic['G12']

    GPIO.setmode(GPIO.BOARD)       
    GPIO.setup(pin_sig, GPIO.OUT)   
    GPIO.output(pin_sig, GPIO.HIGH) 
    
    
    # LCD 1602 初始化
    m_lcd = LCD_1602(Address=0x27,bus_id=1,bl=1)
    flag =m_lcd.lcd_init()
    print(flag)
    try:
        while True:
            success, img = cap.read()

            if success:
                # 读取边缘
                img_edge = preProcessing(img)
               
                # 圆形检测 
                n_circle,list_contours = det_circle(img_edge)
                
                # 显示字符串
                str_led = 'circle %d     '%(n_circle) 
                m_lcd.lcd_display_string(0,0,str_led)
                
                # 小于4个报警
                if n_circle<4:
                    m_lcd.lcd_display_string(0,1,'Alarm')
                    ring_on(pin_sig)
                else:
                    m_lcd.lcd_display_string(0,1,'       ')
                    ring_off(pin_sig)
                
                time.sleep(0.1)
              
             
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break
        cap.release() 
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
        
    finally:
        
        GPIO.cleanup()  