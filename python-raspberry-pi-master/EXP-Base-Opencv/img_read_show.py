import cv2

if __name__ == "__main__":
    # 读取图像并显示
    img= cv2.imread("face.bmp")
    print(img.shape)
    cv2.imshow("output",img)
    cv2.waitKey(0)