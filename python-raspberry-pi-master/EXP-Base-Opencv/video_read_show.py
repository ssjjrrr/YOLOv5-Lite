import cv2

if __name__ == "__main__":
    # 读取视频并显示
    # 读取视频文件
    # cap = cv2.VideoCapture('test.mp4')

    # 读取摄像头
    # cap = cv2.VideoCapture(0)

    # 读取视频流
    video = "http://admin:123456@192.168.1.17:8081/"
    cap = cv2.VideoCapture(video)

    while True:
        success, img = cap.read()
        if success:
            cv2.imshow("video",img)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    cap.release() 