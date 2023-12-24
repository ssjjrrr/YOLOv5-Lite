import cv2
import numpy as np  

if __name__ == '__main__':
    # 图像颜色转换 模糊处理 边缘提取  膨胀与 腐蚀细化
    #读取图像
    img = cv2.imread("lena.png")

    #颜色转换
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 图像模糊 简单去噪
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),0)

    # 边缘提取
    imgCanny = cv2.Canny(imgBlur,150,200) 

    # 图像的膨胀 对细小的边缘进行连接 
    kernel = np.ones((5,5),np.uint8)
    imgDialation = cv2.dilate(imgCanny,kernel, iterations=1) 

    # 图像的腐蚀细化 获取更为准确的边缘的定位
    imgEroded = cv2.erode(imgDialation,kernel,iterations = 1)

    # 各阶段图像像显示
    cv2.imshow("output",img)
    cv2.imshow("Gray",imgGray)
    cv2.imshow("Blur",imgBlur)
    cv2.imshow("Canny",imgCanny)
    cv2.imshow("Dialate",imgDialation)
    cv2.imshow("Erode",imgEroded)
    cv2.waitKey(0)