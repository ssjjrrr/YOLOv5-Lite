import cv2
import numpy as np


if __name__ == "__main__":
    # 读取图像
    img = cv2.imread("shapes.png")
    # 打印尺寸
    print(img.shape)

    # 图像缩放
    imgResize = cv2.resize(img,(1000,500))
    #打印尺寸
    print(imgResize.shape)

    #图像剪裁
    imgCropped = img[46:119,352:495]

    # 图像显示
    cv2.imshow("Image",img)
    cv2.imshow("Image Resize",imgResize)
    cv2.imshow("Image Cropped",imgCropped)
    cv2.waitKey(0)