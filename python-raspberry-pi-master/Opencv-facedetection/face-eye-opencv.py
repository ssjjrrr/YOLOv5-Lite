import cv2


# 加载训练好的人脸检测器
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
# eye 
eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
# 打开摄像头
cap = cv2.VideoCapture(0)
while True:
    
    # 读取一帧图像
    success, img = cap.read()
    
    # 转换为灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 进行人脸检测
    faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(50, 50),flags=cv2.CASCADE_SCALE_IMAGE)
    
    # 画框
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 3)
    
        roi = gray[y:y+h,x:x+w]
        
        eyes = eyeCascade.detectMultiScale(roi)
        
        for x_eye,y_eye,w_eye,h_eye in eyes:
        
            cv2.rectangle(img, (x+x_eye, y+y_eye), (x+x_eye+w_eye, y+y_eye+h_eye), (0, 255, 0), 3)
        
       
    # 显示检测结果
    cv2.imshow("FACE",img)
    
    # 按q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
cap.release() 