import cv2
import numpy as np


# 滑块的响应函数
def empty(a):
    pass

# 预处理提取边缘图像，imgCanny边缘提取
def preProcessing(img,edge_min=40,edge_max=50):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    imgCanny = cv2.Canny(imgBlur,edge_min,edge_max)
    kernel = np.ones((5,5))
    imgDial = cv2.dilate(imgCanny,kernel,iterations=2)
    imgEdge = cv2.erode(imgDial,kernel,iterations=1)
    return imgEdge


def det_circle(img):
     
    # 轮廓提取
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    # 对提取的各个轮廓进行遍历
    n_circle = 0
    list_contours = []
    for cnt in contours:        
        # 计算各个轮廓包围的面积
        area = cv2.contourArea(cnt)
        # 当面积大于300时进行处理
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

    # 创建参数调整滑块
    cv2.namedWindow("TrackBars")
    cv2.resizeWindow("TrackBars",640,60)
    cv2.createTrackbar("Edge Min","TrackBars",50,255,empty)
    cv2.createTrackbar("Edge Max","TrackBars",50,255,empty)

    
    # 读取摄像头
    cap = cv2.VideoCapture(0)
    
    while True:
        success, img = cap.read()

        if success:
            
            # 获取边缘检测参数
            edge_min = cv2.getTrackbarPos("Edge Min","TrackBars")
            edge_max = cv2.getTrackbarPos("Edge Max", "TrackBars")
            
            # 读取边缘
            img_edge = preProcessing(img,edge_min,edge_max)
            cv2.imshow("video2",img_edge)
            
            n_circle,list_contours = det_circle(img_edge)
            print(n_circle)

            for cnt in list_contours:
                cv2.drawContours(img, cnt, -1, (255, 0, 0), 3)
            
            cv2.imshow("video",img)
       
         
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break
    cap.release() 