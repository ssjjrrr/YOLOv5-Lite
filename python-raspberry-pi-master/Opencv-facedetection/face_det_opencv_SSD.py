import cv2

if __name__ == "__main__":
    
    model_file = "opencv_face_detector_uint8.pb"
    config_file = "opencv_face_detector.pbtxt" 
    net = cv2.dnn.readNetFromTensorflow(model_file,config_file)
                  
    threshold = 0.7
    
    freq = cv2.getTickFrequency() # 系统频率
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    while True:
    
        # 读取一帧图像
        success, img = cap.read()
        
        if not success:
            break
        
        blob = cv2.dnn.blobFromImage(img,1.0,(300,300),[104,117,123],False,False)
        H,W = img.shape[:2]
        
        # 获得结果
        # 获取起始时间
        t1 = cv2.getTickCount()
        
        net.setInput(blob)
        
        detections = net.forward()
        
        t2 = cv2.getTickCount()
        fps = freq/(t2-t1)
        
        # 显示执行速度
        cv2.putText(img, 'FPS: %.2f'%(fps), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))
        
        # 结果打印
        for i in range(detections.shape[2]):
            
            #  获取分数
            score = detections[0,0,i,2]
            if score < threshold:
                continue
            
            # 获取位置
            left = int(detections[0,0,i,3]*W)
            top = int(detections[0,0,i,4]*H)
            right = int(detections[0,0,i,5]*W)
            down = int(detections[0,0,i,6]*H)
            
            # 画框
            cv2.rectangle(img,(left,top),(right,down),(0,255,0),3)
            
            # 写分数
            cv2.putText(img, '%.4f'%(score), (left, top+12), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,255))
            
      
        # 显示检测结果
        cv2.imshow("FACE",img)
        
        # 按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release() 