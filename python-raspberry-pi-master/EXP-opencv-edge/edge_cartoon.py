import cv2
import numpy as np  


if __name__ == "__main__":
    # 打开摄像头
    cap = cv2.VideoCapture(0)

    while True:
        # 读取图像帧
        success, img = cap.read()
        
        #颜色转换
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 中值滤波图像去噪
        imgBlur = cv2.medianBlur(imgGray,5)

        # 边缘提取
        imgCanny = cv2.Canny(imgBlur,50,50)
        
        # 图像平滑
        color = cv2.bilateralFilter(img, 9, 300, 300)
        
        # 平滑图像与边缘图像的融合 
        img_edge = cv2.cvtColor(255-imgCanny, cv2.COLOR_GRAY2RGB)
        cartoon = cv2.bitwise_and(color, img_edge)
        
        # 卡通图像显示
        cv2.imshow("Cartoon",cartoon)
        cv2.imshow("img",img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()    