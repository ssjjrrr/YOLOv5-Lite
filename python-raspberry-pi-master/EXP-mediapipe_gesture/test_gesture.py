import mediapipe as mp
import cv2
import numpy as np
from PIL import Image,ImageFont,ImageDraw

import threading
import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time

from Run_LED import Run_LED
from Read_Ds18b20 import Read_Ds18b20
from Read_DHT11 import Read_DHT11
from Play_Buzzer import Play_Buzzer
    

def get_guester(img,list_lms):

    hull_index = [0,1,2,3,6,10,14,19,18,17]
    hull = cv2.convexHull(list_lms[hull_index,:])
    # 绘制凸包
    cv2.polylines(img,[hull], True, (0, 255, 0), 2)

    # 查找外部的点数
    n_fig = -1
    ll = [4,8,12,16,20] 
    up_fingers = []
    
    for i in ll:
        pt = (int(list_lms[i][0]),int(list_lms[i][1]))
        dist= cv2.pointPolygonTest(hull,pt,True)
        if dist <0:
            up_fingers.append(i)
            
    guester = None
    
    if len(up_fingers)==1 and up_fingers[0]==8:
        guester = 1
    elif len(up_fingers)==2 and up_fingers[0]==8 and up_fingers[1]==12:
        guester = 2

    elif len(up_fingers)==3 and up_fingers[0]==8 and up_fingers[1]==12 and up_fingers[2]==16:
        guester = 3
     
    elif len(up_fingers)==4 and up_fingers[0]==8 and up_fingers[1]==12 and up_fingers[2]==16 and up_fingers[3]==20:
        guester = 4
        
    elif len(up_fingers)==5:
        guester = 5
        
    elif len(up_fingers)==2 and up_fingers[0]==4 and up_fingers[1]==20:
        guester = 6  
    elif len(up_fingers)==2 and up_fingers[0]==4 and up_fingers[1]==8:
        guester = 8
    
    elif len(up_fingers)==0:
        guester = 10
    
    return  guester
    

        
def paint_chinese_opencv(im,chinese,pos,color,font_size = 20):
    img_PIL = Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype('NotoSansCJK-Bold.ttc',font_size,encoding="utf-8")
    fillColor = color 
    position = pos 
   
    draw = ImageDraw.Draw(img_PIL)
    draw.text(position,chinese,fillColor,font)
    img = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)
    return img     

if __name__ == "__main__":
    
    # 硬件部分初始化
    GPIO.setmode(GPIO.BOARD)
    
    # LED 小灯 初始化
    pin_R = pin_dic['G12']
    pin_G = pin_dic['G6']
    pin_B = pin_dic['G5']
    colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,197,204),(192,255,62),(148,0,211),(118,238,200)];
    pins_LED = [pin_R,pin_G,pin_B]
    
    m_runing_LED = Run_LED(pins_LED,colors)
    m_runing_LED.setDaemon(True)
    
    # 启动小灯线程
    m_runing_LED.dostop()
    m_runing_LED.start()
    
    # 蜂鸣器初始化
    pin_buzzer = pin_dic['G27']
    
    notes = ['cm1' ,'cm1' , 'cm1' , 'cl5' , 'cm3' , 'cm3' , 'cm3' , 'cm1' ,
             'cm1' , 'cm3' , 'cm5' , 'cm5' , 'cm4' , 'cm3' , 'cm2' , 'cm2' ,
             'cm3' , 'cm4' , 'cm4' , 'cm3' , 'cm2' , 'cm3' , 'cm1' , 'cm1' ,
             'cm3' , 'cm2' , 'cl5' , 'cl7', 'cm2' , 'cm1']
    beats = [1 , 1 , 2 , 2 , 1 , 1 , 2 , 2 ,
            1 , 1 , 2 , 2 , 1 , 1 , 3 , 1 ,
            1 , 2 , 2 , 1 , 1 , 2 , 2 , 1 ,
            1 , 2 , 2 , 1 , 1 , 3]
            
    m_play_buzzer = Play_Buzzer(pin_buzzer,notes,beats)
    m_play_buzzer.setDaemon(True)
    
    # 启动蜂鸣器线程
    m_play_buzzer.dostop()
    m_play_buzzer.start()
    
    
    # 湿度传感器初始化
    pin_dht=  pin_dic['G18']
    m_read_DHT11 =  Read_DHT11(pin_dht)
    m_read_DHT11.setDaemon(True)
    
    # 启动湿度读取线程
    m_read_DHT11.dostart()
    m_read_DHT11.start()
    
    
    # 温度传感器初始化
    str_id = "28-0300a2794829"
    m_read_Ds18b20 =  Read_Ds18b20(str_id)
    m_read_Ds18b20.setDaemon(True)
    
    # 启动温度读取线程
    m_read_Ds18b20.dostart()
    m_read_Ds18b20.start()
    
    
    
    
    dic_guester= {1:"开灯",2:"关灯",3:"开音乐",4:"关音乐",5:"温度",6:"湿度",10:"退出",8:" "}
    
    
    cap = cv2.VideoCapture(0)
    # 定义手 检测对象
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    
    c_guester = None
    p_guester = None
    str_show = ""
    while True:
     
        # 读取一帧图像
        success, img = cap.read()
        if not success:
            continue
        image_height, image_width, _ = np.shape(img)
        
        # 转换为RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 得到检测结果
        results = hands.process(imgRGB)
        
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            
            mpDraw.draw_landmarks(img,hand,mpHands.HAND_CONNECTIONS)
            
            # 采集所有关键点的坐标
            list_lms = []    
            for i in range(21):
                pos_x = hand.landmark[i].x*image_width
                pos_y = hand.landmark[i].y*image_height
                list_lms.append([int(pos_x),int(pos_y)])
            
            # 获取手势
            list_lms = np.array(list_lms,dtype=np.int32)
            c_guester = get_guester(img,list_lms)
            
            # print("c_guester",c_guester)
            # print("p_guester",p_guester)
            
            if not c_guester is None and c_guester != p_guester:
                p_guester = c_guester
                
            
            
        # 根据动作进行处理
        if p_guester == 1:# 开灯
            m_runing_LED.dostart()
            
        elif p_guester == 2:  # 关灯
            m_runing_LED.dostop()
            
        elif p_guester == 3: # 开音乐
            m_play_buzzer.dostart()
            
        elif p_guester == 4: # 关音乐
            m_play_buzzer.dostop()
            
        elif p_guester == 5: # 温度
            
            temperature = m_read_Ds18b20.get_temperature()
            if not temperature is None:
                print("temperature=%.2f"%(temperature))
        elif p_guester == 6: # 湿度
            humidity = m_read_DHT11.get_humidity()
            if not humidity is None:
                print("humidity = %.2f"%(humidity))
        
       
          
        if  not p_guester is None:           
            str_show = ' %s'%(dic_guester[p_guester])
                
            
        img = paint_chinese_opencv(img,str_show,(10,10),(0,255,255),font_size=30)
        
        cv2.imshow("hands",img)
        
        
        key =  cv2.waitKey(1) & 0xFF   

        # 按键 "q" 退出
        if key ==  ord('q') or  p_guester == 10:
            m_play_buzzer.dobreak()
            m_read_DHT11.dobreak()
            m_read_Ds18b20.dobreak()
            m_runing_LED.dobreak()
            time.sleep(2)
            GPIO.cleanup()
            
            break
    cap.release() 
       
    
    
    
    
    
    
    
    
    
    
    
    
    