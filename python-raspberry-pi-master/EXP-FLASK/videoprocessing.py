import cv2
import time 
from imgprocessing import img2gray,img2edge,img2cartoon 
from flask import Flask, render_template, Response, request,jsonify,redirect,url_for
import numpy as np
flag_face = False

class VideoCamera(object):
    def __init__(self,path):
        # 打开一个视频源
        self.video = cv2.VideoCapture(path)
        
    def __del__(self):
        self.video.release()
          
    def get_frame(self):
        success, image = self.video.read()
        return image


def gen(camera):
    while True:
        img = camera.get_frame()
        ret, jpeg = cv2.imencode('.jpg',img)
        # 对图像进行编码输出
        yield(b'--frame\r\n'+b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

def gen_effect(camera,method):
    while True:
        img = camera.get_frame()
        if img is None:
            time.sleep(0.1)
            continue
            
        if method == 'gray':
            img = img2gray(img)
        elif method == 'edge':
            img = img2edge(img,20,20)
        elif method == 'cartoon':
            img = img2cartoon(img)
            
            
        ret, jpeg = cv2.imencode('.jpg',img)
        # 对图像进行编码输出
        yield(b'--frame\r\n'+b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')





def face_recognize(face_vec,face_dataset,ids):
    N = face_dataset.shape[0]
    diffMat = np.tile(face_vec,(N,1))-face_dataset
    
    # 计算欧式距离
    distances = np.linalg.norm(diffMat,axis=1)
    
    # 找到最小距离
    idx = np.argmin(distances)
    
    # 返回id编号与距离
    return ids[idx],distances[idx] 
    
    
def face_recognize_cos(face_vec,face_dataset,ids):
    N = face_dataset.shape[0]
    a = np.tile(face_vec,(N,1))
    b = face_dataset
    
    # 计算cos 距离 
    dis_cos = np.sum(a*b,axis=1)/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1))
    
    # 找到最大距离
    idx = np.argmax(dis_cos)
    
    # 返回id编号与距离
    return ids[idx],dis_cos[idx] 
    
        
        
    

def gen_face_recognition(camera,opts):
    
    detector = opts['detector']
    sp = opts['sp']
    facerec = opts['recongnizer']
    face_vectors = opts['face_vectors'] 
    face_ids = opts['face_ids']    
    face_allowed = opts['face_allowed']
   
    
    while True:
       
        img = camera.get_frame()
        if img is None:
            time.sleep(0.1)
            continue
        
        # BGR 转 gray
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # BGR 转 RGB
        img_rgb = cv2.cvtColor(img, cv2. COLOR_BGR2RGB)
        
        # 进行人脸检测
        dets = detector(img_gray, 1)
       
        # 遍历检测的人脸
        for k, d in enumerate(dets):
            
            # 画框
            cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (255, 0, 0), 3)
            
            # 标志点检测
            shape = sp(img_rgb, d)
            
            # 获取人脸特征
            face_vector = facerec.compute_face_descriptor(img_rgb, shape)
            
            # # 进行识别返回ID与距离
            face_id, dis = face_recognize(np.array(face_vector),face_vectors,face_ids)
            
            if (dis < 0.45):
                str_out = "%s  %.2f"%(face_id,dis)
                
                if face_id in face_allowed:
                    opts['flag'] = True
        
            else:
                str_out = "unknown %.2f"%(dis)
        
            # # 进行识别返回ID与距离
            # face_id, dis = face_recognize_cos(np.array(face_vector),face_vectors,face_ids)
            
            # if (dis > 0.95):
                # str_out = "%s  %.2f"%(face_id,dis)
            # else:
                # str_out = "unknown %.2f"%(dis)
           
            # 检测结果文字输出
            cv2.putText(img, str_out, (d.left()+5,d.top()), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
           
        
        ret, jpeg = cv2.imencode('.jpg',img)
        # 对图像进行编码输出
        yield(b'--frame\r\n'+b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
  
       
        
        
    
    

    
