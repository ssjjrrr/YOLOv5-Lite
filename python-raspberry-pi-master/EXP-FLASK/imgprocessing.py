import cv2
import pytesseract
import dlib
import numpy as np
import mediapipe as mp
import os

def img2gray(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray

def img2edge(img,th_min=150,th_max=200):
    #颜色转换
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 图像模糊 简单去噪
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),0)

    # 边缘提取
    imgCanny = cv2.Canny(imgBlur,th_min,th_max) 

    # 图像的膨胀 对细小的边缘进行连接 
    kernel = np.ones((5,5),np.uint8)
    imgDialation = cv2.dilate(imgCanny,kernel, iterations=1) 

    # 图像的腐蚀细化 获取更为准确的边缘的定位
    imgEroded = cv2.erode(imgDialation,kernel,iterations = 1)
    return imgEroded

def img2text(img):
    # 识别文字
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    imgWarped_Gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # 识别结果打印
    str_result = pytesseract.image_to_string(imgWarped_Gray, lang='chi_sim')
    return str_result

def img2cartoon(img):
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
    return cartoon
def get_face_detector():
    # 创建人脸检测器
    detector_face = dlib.get_frontal_face_detector()
    basepath = os.path.dirname(__file__)
    file_detector = os.path.join(basepath,"shape_predictor_68_face_landmarks_GTX.dat")
    # 加载标志点检测器
    detector_landmarks = dlib.shape_predictor(file_detector)  # 68点

    return detector_face,detector_landmarks

# 利用dlib获取脸部关键点
def get_landmarks_dlib(img,detector_face,detector_landmarks):

    # 转换为灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 检测人脸区域
    face_rects = detector_face(gray, 0)
    
    # 获取68个关键点
    landmarks = detector_landmarks(gray, face_rects[0])
    
    # 获取关键点的坐标
    landmarks_points = []
    parts = landmarks.parts()
    for part in parts:
        landmarks_points.append((part.x,part.y))
    return landmarks_points

# 双线性差值   
def BilinearInsert(src,pt_U):
    ux = pt_U[0]
    uy = pt_U[1]
    
    x1=np.float32(int(ux))
    x2=x1+1
    y1=np.float32(int(uy))
    y2=y1+1
    
    v1 = np.float32(src[int(y1),int(x1)])
    v2 = np.float32(src[int(y1),int(x2)])
    v3 = np.float32(src[int(y2),int(x1)])
    v4 = np.float32(src[int(y2),int(x2)])
    
    part1 = v1 * (x2 - ux) * (y2 - uy)
    part2 = v2 * (ux - x1) * (y2 - uy)
    part3 = v3 * (x2 - ux) * (uy - y1)
    part4 = v4 * (ux - x1) * (uy - y1)
 
    insertValue=part1+part2+part3+part4
    return insertValue.astype(np.uint8)

# 大眼用的算法
def localScaleWap(img,pt_C,R,scaleRatio):
    
    h,w,c = img.shape
    # 文件拷贝
    copy_img = np.zeros_like(img)
    copy_img = img.copy()
    
    # 创建蒙板
    mask = np.zeros((h,w),dtype = np.uint8)
    cv2.circle(mask,pt_C,np.int32(R),255,cv2.FILLED)

    pt_C = np.float32(pt_C)
   
    for i in range(w):
        for j in range(h): 
            
            # 只计算半径内的像素
            if mask[j,i] ==0:
                continue
            
            pt_X = np.array([i,j],dtype = np.float32)
           
            
            dis_C_X = np.sqrt(np.dot((pt_X-pt_C),(pt_X-pt_C)))
            
            alpha = 1.0 - scaleRatio * pow(dis_C_X / R - 1.0, 2.0)
            
            pt_U = pt_C + alpha*(pt_X-pt_C)
            
            # 利用双线性差值法，计算U点处的像素值
            value = BilinearInsert(img,pt_U)
            copy_img[j,i] = value
     
    return copy_img

def big_eyes(img,detector_face,detector_landmarks):
    landmarks = get_landmarks_dlib(img,detector_face,detector_landmarks)
    if len(landmarks)==0:
        return False,img
    
    landmarks = np.array(landmarks)
     # 大眼调节参数
    scaleRatio =0.5 
    # 右眼
    index = [37,38,40,41]
    pts_right_eyes = landmarks[index]
    crop_rect = cv2.boundingRect(pts_right_eyes)
    (x,y,w,h) = crop_rect
    pt_C_right = np.array([x+w/2,y+h/2],dtype = np.int32)
    
    r1 = np.sqrt(np.dot(pt_C_right-landmarks[36],pt_C_right-landmarks[36])) 
    r2 = np.sqrt(np.dot(pt_C_right-landmarks[39],pt_C_right-landmarks[39])) 
    R_right  =  1.5*np.max([r1,r2])
    
    # 左眼
    index = [43,44,45,47]
    pts_left_eyes = landmarks[index]
    crop_rect = cv2.boundingRect(pts_left_eyes)
    (x,y,w,h) = crop_rect
    pt_C_left = np.array([x+w/2,y+h/2],dtype = np.int32)
    r1 = np.sqrt(np.dot(pt_C_left-landmarks[42],pt_C_left-landmarks[42])) 
    r2 = np.sqrt(np.dot(pt_C_left-landmarks[46],pt_C_left-landmarks[46])) 
    R_left  =  1.5*np.max([r1,r2])
    
    # 大右眼
    img_bigeye = localScaleWap(img,pt_C_right,R_right,scaleRatio)
    
    # 大左眼
    img_bigeye = localScaleWap(img_bigeye,pt_C_left,R_left,scaleRatio)

    return True,img_bigeye

# 瘦脸用的函数
def localTranslationWap(img,pt_C,pt_M,r,a):
    
    h,w,c = img.shape
    # 文件拷贝
    copy_img = np.zeros_like(img)
    copy_img = img.copy()
    
    # 创建蒙板
    mask = np.zeros((h,w),dtype = np.uint8)
    cv2.circle(mask,pt_C,np.int32(r),255,cv2.FILLED)
    
    # 计算 CM 之间的距离
    pt_C = np.float32(pt_C)
    pt_M = np.float32(pt_M)
    dis_M_C = np.dot((pt_C-pt_M),(pt_C-pt_M))

    # 只对蒙板内大于0的数进行处理
    for i in range(w):
        for j in range(h):
            
            # 只计算半径内的像素
            if mask[j,i] ==0:
                continue
                
            # 计算 XC之间的距离            
            pt_X = np.array([i,j],dtype = np.float32)
            dis_X_C = np.dot((pt_X-pt_C),(pt_X-pt_C))
            
            # 计算缩放比例
            radio = (r*r-dis_X_C)/(r*r-dis_X_C+a*dis_M_C)
            radio = radio*radio
            
            # 计算 目标图像（i，j）处由源图像U点替换
            pt_U = pt_X-radio*(pt_M-pt_C)
            
            # 利用双线性差值法，计算U点处的像素值
            # value = BilinearInsert(img,pt_U)
            # copy_img[j,i] = value
            
            # 直接获取U点的值
            pt_u = np.int32(pt_U)
            copy_img[j,i] = img[pt_u[1],pt_u[0]]
 
    return copy_img


def thin_face(img,detector_face,detector_landmarks):
    landmarks = get_landmarks_dlib(img,detector_face,detector_landmarks)
    if len(landmarks)==0:
        return False,img
    landmarks = np.array(landmarks)
    # 瘦脸程度调节 
    a = 1
    
    # 右脸参数
    pt_C_right = landmarks[3]
    pt_M = landmarks[30]
    r_right = np.sqrt(np.dot(landmarks[3]-landmarks[5],landmarks[3]-landmarks[5])) 
    
    # 左脸参数
    pt_C_left = landmarks[13]   
    r_left = np.sqrt(np.dot(landmarks[13]-landmarks[11],landmarks[13]-landmarks[11]))
    
    # 减右脸
    img_thin = localTranslationWap(img,pt_C_right,pt_M,r_right,a)
    # 减左脸
    img_thin = localTranslationWap(img_thin,pt_C_left,pt_M,r_left,a)
    
    return True,img_thin


# 图像叠加
def img_overlayer(img,img_fg,pos_fg,bk_fg):
    
    #把前景图变换为灰度
    fg_gray = cv2.cvtColor(img_fg,cv2.COLOR_BGR2GRAY)
    h_gf,w_fg = np.shape(fg_gray)
    
    # 获取前景图的mask 有图部分为 1 背景部分为 0 
    if bk_fg == 255:
        mask_fg = fg_gray<250
    elif bk_fg == 0:
        mask_fg = fg_gray>5
    
    mask_fg = mask_fg[:,:,np.newaxis]
    not_mask_fg = ~mask_fg
    
    # 截取背景图
    bk = img[pos_fg[1]:pos_fg[1]+h_gf,pos_fg[0]:pos_fg[0]+w_fg]
    
    img_overlayer = bk*not_mask_fg + img_fg*mask_fg
    img[pos_fg[1]:pos_fg[1]+h_gf,pos_fg[0]:pos_fg[0]+w_fg] = img_overlayer
    return img

def add_hat(img,img_hat,parts):
    

    # 获取帽子图像大小
    w_hat = np.shape(img_hat)[1]
    h_hat = np.shape(img_hat)[0]
    
    # 计算脸的宽度
    face_w = int(parts[16].x - parts[0].x)

    # 计算缩放尺度
    scale = face_w/w_hat
    
    # 帽子图像缩放
    resize_hat = cv2.resize(img_hat,(int(w_hat*scale*(1.2)),int(h_hat*scale*(1.2))))
    
    # 计算帽子图像的起始位置(左上坐标)
    pos_hat = (parts[0].x-int(face_w*0.1), max(0,int(parts[19].y-resize_hat.shape[0])))
    
    # 图像叠加
    img_out = img_overlayer(img,resize_hat,pos_hat,bk_fg=255)
    return img_out

def add_glasses(img,img_glasses,parts):
    
    # 获取眼镜图像大小
    w_glass = np.shape(img_glasses)[1]
    h_glass = np.shape(img_glasses)[0]
    
    # 计算缩放尺度
    scale = np.abs(parts[36].x-5 -parts[45].x-5)/w_glass
    
    # 眼镜图像缩放
    resize_glasses = cv2.resize(img_glasses,(int(w_glass*scale),int(h_glass*scale)))

    # 计算眼镜图像的起始位置(左上坐标)
    pos_glass = (parts[36].x-5,parts[36].y-int(h_glass*scale/2.0))
    
    # 图像叠加
    img_out = img_overlayer(img,resize_glasses,pos_glass,bk_fg=255)
    return img_out
# dic_effect = {
#                 "hat": ["Normal","hat1.bmp"],
#                 "eye": ["glasses","glasses.bmp"],
#                 # "eye": ["double","left-eye.bmp","left-eye.bmp"]
#             }
def add_cartoon_eye(img,img_left_eye,img_right_eye,parts):   
    # 计算左眼的区域
    pos_left = parts[36].x-3
    pos_up = min(parts[37].y,parts[38].y)-3
    pos_right = parts[39].x+3
    pos_down = max(parts[40].y,parts[41].y)+3
    
    img_left_eye_overlayer = cv2.resize(img_left_eye,(pos_right-pos_left,pos_down-pos_up))
    img = img_overlayer(img,img_left_eye_overlayer,(pos_left,pos_up),bk_fg=0)
    # 计算右眼的区域
    pos_left = parts[42].x-3
    pos_up = min(parts[43].y,parts[44].y)-3
    pos_right = parts[45].x+3
    pos_down = max(parts[46].y,parts[47].y)+3
    
    img_right_eye_overlayer = cv2.resize(img_right_eye,(pos_right-pos_left,pos_down-pos_up))
    
    img = img_overlayer(img,img_right_eye_overlayer,(pos_left,pos_up),bk_fg=0)
    return img

def face_effect(img,dic_effect,detector_face,detector_landmarks):
    
    # 转换为灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 检测人脸区域
    face_rects = detector_face(gray, 0)
    
    if len(face_rects) ==0:
        return False,img
    # 获取脸部关键点
    landmarks = detector_landmarks(gray, face_rects[0])
    parts = landmarks.parts()
    
    if "hat" in dic_effect:
        img_hat = cv2.imread(dic_effect["hat"][1])
        img = add_hat(img,img_hat,parts)

    if "eye" in dic_effect:
        if dic_effect["eye"][0]=="glasses":
            img_glasses = cv2.imread(dic_effect["eye"][1])
            img = add_glasses(img,img_glasses,parts)
        elif dic_effect["eye"][0]=="double":
            t_left_eye = cv2.imread(dic_effect["eye"][1])
            t_right_eye = cv2.imread(dic_effect["eye"][2])
            img = add_cartoon_eye(img,t_left_eye,t_right_eye,parts)
    return True,img
    
def change_color_lip(img,list_lms,index_lip_up,index_lip_down,color):
    
    mask = np.zeros_like(img)
    
    points_lip_up = list_lms[index_lip_up,:]
    mask = cv2.fillPoly(mask,[points_lip_up],(255,255,255))
    
    
    points_lip_down = list_lms[index_lip_down,:]
    mask = cv2.fillPoly(mask,[points_lip_down],(255,255,255))
    
    img_color_lip = np.zeros_like(img)
    img_color_lip[:] = color
    img_color_lip = cv2.bitwise_and(mask,img_color_lip)
    img_color_lip = cv2.GaussianBlur(img_color_lip,(7,7),10)
    img_color_lip = cv2.addWeighted(img,1,img_color_lip,0.8,0)
    
    return img_color_lip

def color_lip(img):
    mp_face_mesh = mp.solutions.face_mesh
    
    
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True,
                                       max_num_faces=1,
                                       refine_landmarks=True,
                                       min_detection_confidence=0.5)
    
    image_height, image_width, _ = np.shape(img)
    img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(img_RGB)
    list_lms = []  
    if  results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]
        
        for i in range(478):
            pos_x = int(face_landmarks.landmark[i].x * image_width)
            pos_y = int(face_landmarks.landmark[i].y * image_height)
            list_lms.append((pos_x,pos_y))
            
    if len(list_lms) ==0:
        return  False,img
    list_lms = np.array(list_lms,dtype=np.int32)  
    index_lip_up = [61, 185, 40, 39, 37,0, 267, 269, 270, 409, 291,308,415,310,311,312,13,82,80,191,78,61]
    index_lip_down = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308,291,375,321,405,314,17,84,181,91,146,61,78]
    
    img_show = change_color_lip(img,list_lms,index_lip_up,index_lip_down,(30,30,213))
    return True,img_show



    





    

    


        