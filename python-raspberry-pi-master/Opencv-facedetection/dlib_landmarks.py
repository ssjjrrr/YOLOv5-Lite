import cv2
import dlib

# 创建人脸检测器
det_face = dlib.get_frontal_face_detector()

# 加载标志点检测器
det_landmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # 68点
# det_landmark = dlib.shape_predictor("shape_predictor_5_face_landmarks.dat")  # 5点

# 打开摄像头
cap = cv2.VideoCapture(0)
freq = cv2.getTickFrequency() # 系统频率
while True:
    # 读取一帧图像
    success, img = cap.read()

    # 转换为灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    t1 = cv2.getTickCount()
    # 检测人脸区域
    face_rects = det_face(gray, 0)
    
    
    
    for ret in face_rects:
        # 画出人脸区域
        cv2.rectangle(img, (ret.left(),ret.top()), (ret.right(),ret.bottom()), (255, 0, ), 3)

        # 标志点检测
        landmarks = det_landmark(gray, ret)

        # 遍历标志点并画圆标记
        for part in landmarks.parts():
            pt = (part.x,part.y)
            cv2.circle(img, pt, 2, (0,0,255),-1)
    
    
    t2 = cv2.getTickCount()   
  
    fps = freq/(t2-t1)
    # 显示速度
    cv2.putText(img, 'FPS: %.2f'%(fps), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))
    
    # 显示检测结果
    cv2.imshow("Face",img)

    # 按q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release() 