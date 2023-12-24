import cv2
import numpy as np

if __name__ == "__main__":
    
    
    model_file = "face_detection_yunet_2021dec.onnx"
    conf_Threshold = 0.9
    nms_Threshold = 0.3
    topK = 5000
    model = cv2.FaceDetectorYN.create(
            model=model_file,
            config="",
            input_size=[320,320],
            score_threshold=conf_Threshold,
            nms_threshold=nms_Threshold,
            top_k=topK,
            backend_id=0,
            target_id=0)
        
    freq = cv2.getTickFrequency() # 系统频率
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    model.setInputSize([w, h])
    
    while True:

        # 读取一帧图像
        success, img = cap.read()

        if not success:
            break
            
        # 获得结果
        t1 = cv2.getTickCount()
        
        faces = model.detect(img)
        results = faces[1]
        
        t2 = cv2.getTickCount()
        
       
        
        fps = freq/(t2-t1)
        
       
        
        # 显示速度
        cv2.putText(img, 'FPS: %.2f'%(fps), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))
        
        # 绘图
        for det in (results if results is not None else []):
            
            # 获得检测区域
            x,y,w,h = det[0:4].astype(np.int32)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)
            
            #  获得分数
            score = det[-1]
            cv2.putText(img, '%.4f'%(score), (x, y+12), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,255))
            
            # 显示 关键点
            
            landmarks = det[4:14].astype(np.int32).reshape((5,2))
            
            for idx, landmark in enumerate(landmarks):
                cv2.circle(img, landmark, 2, (0,255,0), 2)
                
            
         # 显示检测结果
        cv2.imshow("FACE",img)
        
        # 按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release() 
            
            
            
            
            
            
            
            
            
            

        
        
        
        
        
            
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # model_file = "opencv_face_detector_uint8.pb"
    # config_file = "opencv_face_detector.pbtxt" 
    # net = cv2.dnn.readNetFromTensorflow(model_file,config_file)
                  
    # threshold = 0.7
    
    # # 打开摄像头
    # cap = cv2.VideoCapture(0)
    
    # while True:
    
        # # 读取一帧图像
        # success, img = cap.read()
        
        # if not success:
            # break
        
        # blob = cv2.dnn.blobFromImage(img,1.0,(300,300),[104,117,123],False,False)
        # H,W = img.shape[:2]
        
        # net.setInput(blob)
        
        # detections = net.forward()
        
        # print(detections.shape)
        
        # for i in range(detections.shape[2]):
            
            # #  获取分数
            # sorce = detections[0,0,i,2]
            # if sorce < threshold:
                # continue
            
            # # 获取位置
            # left = int(detections[0,0,i,3]*W)
            # top = int(detections[0,0,i,4]*H)
            # right = int(detections[0,0,i,5]*W)
            # down = int(detections[0,0,i,6]*H)
            
            # # 画框
            # cv2.rectangle(img,(left,top),(right,down),(0,255,0),3)
      
    
        # # 显示检测结果
        # cv2.imshow("FACE",img)
        
        # # 按q退出
        # if cv2.waitKey(1) & 0xFF == ord('q'):
            # break
            
    # cap.release() 