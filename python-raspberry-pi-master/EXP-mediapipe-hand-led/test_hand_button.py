import mediapipe as mp
import cv2
import numpy as np
import RPi.GPIO as GPIO
from pin_dic import pin_dic


class RGB_LED(object):
    def __init__(self,pin_R,pin_G,pin_B):
        self.pins = [pin_R,pin_G,pin_B]
        
        # 设置为输出引脚，初始化第电平，灯灭
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)   
            GPIO.output(pin, GPIO.LOW)
            
        # 设置三个引脚为pwm对象，频率2000
        self.pwm_R = GPIO.PWM(pin_R, 2000)  
        self.pwm_G = GPIO.PWM(pin_G, 2000)
        self.pwm_B = GPIO.PWM(pin_B, 2000)
    
        # 初始占空比为0
        self.pwm_R.start(0)      
        self.pwm_G.start(0)
        self.pwm_B.start(0)

    def color2ratio(self,x,min_color,max_color,min_ratio,max_ratio):
        return (x - min_color) * (max_ratio - min_ratio) / (max_color - min_color) + min_ratio

    def setColor(self,col):
        R_val,G_val,B_val = col
   
        R =self.color2ratio(R_val, 0, 255, 0, 100)
        G =self.color2ratio(G_val, 0, 255, 0, 100)
        B =self.color2ratio(B_val, 0, 255, 0, 100)
        # 改变占空比
        self.pwm_R.ChangeDutyCycle(R)     
        self.pwm_G.ChangeDutyCycle(G)
        self.pwm_B.ChangeDutyCycle(B)
        
    def destroy(self):    
        self.pwm_R.stop()
        self.pwm_G.stop()
        self.pwm_B.stop()
        for pin in self.pins:
            GPIO.output(pin, GPIO.HIGH)    
        GPIO.cleanup()



def draw_button(img):
    
    colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,197,204),(192,255,62),(148,0,211),(118,238,00)]
    h = 50
    w = 200 
    for i,color in enumerate(colors):

        pos1 = (w+i*50,h)
        pos2 = (w+(i+1)*50,h+50)
        
       
        cv2.rectangle(img,pos1,pos2,(color[2],color[1],color[0]),cv2.FILLED)


    return((w,h),pos2) 
    
def color_pick_up(img,pos_f,color_area):
    
    pos1 = color_area[0]
    pos2 = color_area[1]
    
    if pos_f[0]>pos1[0] and pos_f[0]<pos2[0] and pos_f[1] > pos1[1] and pos_f[1] < pos2[1]:
        
        color = (img[pos_f[1],pos_f[0],2],img[pos_f[1],pos_f[0],1],img[pos_f[1],pos_f[0],0])
    else:
        color = None
    
    return color
    
    
    
    
    
    
    


if __name__ == "__main__":
    
    # 设置引脚编号模式
    GPIO.setmode(GPIO.BOARD)
    
    # 定义三个引脚 
    pin_R = pin_dic['G17']
    pin_G = pin_dic['G16']
    pin_B = pin_dic['G13']
    
    # 定义 RGB_LED 对象
    m_RGB_LED = RGB_LED(pin_R,pin_G,pin_B)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    # 定义手 检测对象
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()

    color_p = (0,0,0)
    
    while True:
     
        # 读取一帧图像
        success, img = cap.read()
        if not success:
            continue
            
        img=cv2.flip(img, 1)    
        image_height, image_width, _ = np.shape(img)
      
        # 转换为RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 画按键
        color_area = draw_button(img)
        
        # 得到检测结果
        results = hands.process(imgRGB)
      
        if results.multi_hand_landmarks:
            
            hand = results.multi_hand_landmarks[0]
            pos_x = hand.landmark[8].x*image_width
            pos_y = hand.landmark[8].y*image_height
            pos_f = (int(pos_x),int(pos_y))
            
            color_c = color_pick_up(img,pos_f,color_area)
            
            if not color_c is None:
                
                if color_c != color_p: 
                
                    print(color_c)
                    m_RGB_LED.setColor(color_c)
                    color_p = color_c
            
            
            cv2.circle(img, pos_f, 10, (180,180,180),-1)
        
        
        
  #      cv2.imshow("hands",img_button)
        cv2.imshow("hands",img)

        key =  cv2.waitKey(1) & 0xFF   

        # 按键 "q" 退出
        if key ==  ord('q'):
            break
    cap.release()
    m_RGB_LED.destroy()
       
    
    
    
    
    
    
    
    
    
    
    
    
    
