from flask import Flask, render_template, Response, request,jsonify,redirect,url_for
from pin_dic import pin_dic
from light import light
from BMP085 import BMP085
from PCF8591 import PCF8591
from dht11 import DHT11
from ds18b20 import  Ds18b20
from buzzer import Runing_Song
from videoprocessing import VideoCamera,gen,gen_effect,gen_face_recognition
import os
import time
from werkzeug.utils import secure_filename
from imgprocessing import img2gray,img2edge,img2cartoon,img2text,big_eyes,thin_face,face_effect,color_lip
import dlib
import cv2
import random
import numpy as np
import threading
# 定义小灯对象
m_light = light(pin_dic["G17"])

# 定义环境监测对象，并启动线程

# 温度检测
m_ds18b20 =  Ds18b20("28-0300a2794829")
m_ds18b20.setDaemon(True)
m_ds18b20.start()

# 光照度检测
m_PCF8591 = PCF8591(Address=0x48,bus_id=1)
m_PCF8591.setDaemon(True)
m_PCF8591.start()

# 湿度检测
m_dht11 = DHT11(pin_dic['G13'])
m_dht11.setDaemon(True)
m_dht11.start()

# 气压海拔检测 
m_BMP085 = BMP085(mode=1, address=0x77,bus_id =1)
m_BMP085.setDaemon(True)
m_BMP085.start()

#  蜂鸣器
global m_runing_song
m_runing_song = Runing_Song(pin_dic['G18'])

print("加载人脸检测器")
det_face = dlib.get_frontal_face_detector()

# 加载标志点检测器
det_landmark = dlib.shape_predictor("shape_predictor_68_face_landmarks_GTX.dat")  # 68点5
sp = dlib.shape_predictor("shape_predictor_5_face_landmarks.dat")  # 5点

# 加载人脸特征提取器
facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

# 加载训练好的人脸模型
model = np.load('trainer.npz')
face_vectors = model['face_vectors']
face_ids = model['ids']

opt_face = dict()
opt_face['detector'] = det_face  # 人脸检测器
opt_face['recongnizer'] = facerec # 人脸特征提取器
opt_face['sp']=sp                 # 关键点提取器
opt_face['face_ids'] = face_ids   # 已存储的人脸id 
opt_face['face_vectors']  = face_vectors # 已存储的人脸矢量
opt_face['face_allowed'] = ['yuhong']    # 允许通过认证的人脸ID
opt_face['flag'] = False                 # 认证成功标志







# 允许的图像格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 
app = Flask(__name__)


# 定义路由
@app.route('/light',methods=['GET', 'POST'])
def light():

    if request.method == 'GET':
        print("转小灯")
        return render_template('index.html')
    else:    
        if request.form.get('on', None) == "开灯":
            m_light.on()
            print('light on')
        
        elif request.form.get('off', None) == "关灯":
            m_light.off()
            print('ligh off')
    
    return render_template('index.html')


@app.route('/get_env_info')
def responds_env_all():
    dic_env_data = {
            'tem': m_ds18b20.get_temperature(),
            'hum': m_dht11.get_humidity(),
            'lux': m_PCF8591.get_LUX(),
            'press':m_BMP085.get_pressure(),
            'altitude':m_BMP085.get_altitude()
            }
    
    return jsonify(dic_env_data)

@app.route('/env',methods=['GET', 'POST'])
def env():
    
    print('t   ',m_ds18b20.get_temperature())
    print('h  ',m_dht11.get_humidity())
    print('lux  ',m_PCF8591.get_LUX())
    print('p  ',m_BMP085.get_pressure())
    print('al  ', m_BMP085.get_altitude())
    templateData = {
            'tem': m_ds18b20.get_temperature(),
            'hum': m_dht11.get_humidity(),
            'lux': m_PCF8591.get_LUX(),
            'press':m_BMP085.get_pressure(),
            'altitude':m_BMP085.get_altitude()
            }
          
    return render_template('env_timer.html', **templateData)
    
    
@app.route('/music',methods=['GET', 'POST'])    
def music():
    global m_runing_song
    if request.method == 'GET':
        return render_template('music.html')
    
    if request.form.get('music_stop', None) == "停止":

        print('music off')
        if m_runing_song.isAlive() == True:
            m_runing_song.dostop()
            time.sleep(0.1)
            m_runing_song.join()  
        return redirect(url_for('music'))
    
    
    
    # 进行文件验证
    # 如果文件存在
    if  request.files:
        # 验证文件类型
        f = request.files['file']
        f_name = f.filename
        ext = f_name.rsplit('.', 1)[1]
        # 报文件类型错误信息
        if not (f and ext=='txt'):
            return render_template('music.html',message_file_error="文件类型错误，只支持txt")
        
        # 没有问题进行文件存储
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'static', secure_filename(f.filename))
        f.save(upload_path)
    
    else:
        return render_template('music.html',message_file_error="文件为空")
   
    # 点击演奏按钮
    if request.form.get('music_play', None) == "演奏":
        
        print('music on ')
        if m_runing_song.isAlive() == False:
            # 没有线程 创建线程并启动
            m_runing_song = Runing_Song(pin_dic['G18'])
            m_runing_song.file_load(upload_path)
            
            m_runing_song.setDaemon(True)
            m_runing_song.start()
        
        else:
            
            # 如果正在演奏，先停止
            m_runing_song.dostop()
            time.sleep(0.1)
            m_runing_song.join()
            
            # 重新加载
            m_runing_song = Runing_Song(pin_dic['G18'])
            flag = m_runing_song.file_load(upload_path)
            m_runing_song.setDaemon(True)
            m_runing_song.start()
            
        return render_template('music.html',message_file_error = "正在演奏"+request.files['file'].filename)
    return render_template('music.html')    

@app.route('/images',methods=['GET', 'POST'])    
def image():
    # get 方式访问，返回页面
    if request.method == 'GET':
        return render_template('images.html')

    # pos 方式访问 首先进行文件的验证
    if request.method == 'POST':
         if  request.files:
             f = request.files['file']
             print(f)
             if not (f and allowed_file(f.filename)):
                  print("file error")
                  return render_template('images.html',message="上传文件格式错误")
         else:
             return render_template('images.html',message="文件为空")
            
    
    basepath = os.path.dirname(__file__)
    # upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))
    # f.save(upload_path)
    
    result_image_pid = str(int(time.time())) + str(random.randint(0, 10000)).zfill(5) + '.' + \
                           f.filename.split('.')[-1]
    upload_path = os.path.join(basepath, 'static/images',result_image_pid)
    f.save(upload_path)
    
    
    

      
    # 把输入的文件统一命名成test.jpg
    img = cv2.imread(upload_path)
    # 在这里加一段缩小图像的程序
    cv2.imwrite(os.path.join(basepath, 'static/images', 'test.jpg'), img)

    # 获取图像处理方式
    process_method = request.form.get("method_img_process")
    print('process_method',process_method)

    # # 所有处理后的文件都命名为dealed.jpg
    # result_img_file = os.path.join(basepath, 'static/images', 'dealed.jpg')
    
    # # 若文件存在，先删除
    # if os.path.exists(result_img_file):
        # os.remove(result_img_file)

    # 根据不同的处理方式进行处理
    if process_method == "gray":
        message = " 灰度转换"
        img_gray= img2gray(img)
        str_info = "转换成功"
        # 创建结果文件
        dealed_image_pid = str(int(time.time())) + str(random.randint(0, 10000)).zfill(5) + '.' + \
                           f.filename.split('.')[-1]
        dealed_path = os.path.join(basepath, 'static/images',dealed_image_pid)
        cv2.imwrite(dealed_path,img_gray)
        
       
        url_src = url_for('static', filename= './images/'+result_image_pid)
        url_dst = url_for('static', filename= './images/'+dealed_image_pid)
        return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)



    elif process_method == "edge":
        message = "边缘检测"
        th_min = int(request.form.get("th_edge_MIN"))
        th_max = int(request.form.get("th_edge_MAX"))
        img_edge = img2edge(img,th_min,th_max)
        str_info = "边缘提取成功"
        
        # 创建结果文件
        dealed_image_pid = str(int(time.time())) + str(random.randint(0, 10000)).zfill(5) + '.' + \
                           f.filename.split('.')[-1]
        dealed_path = os.path.join(basepath, 'static/images',dealed_image_pid)
        cv2.imwrite(dealed_path,img_edge)
        
       
        url_src = url_for('static', filename= './images/'+result_image_pid)
        url_dst = url_for('static', filename= './images/'+dealed_image_pid)
        return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)

    elif process_method == "effect_cartoon":
        message = "卡通效果"
        print("卡通效果")
        img_cartoon = img2cartoon(img)
     
        str_info = "卡通效果展示"
        
        # 创建结果文件
        dealed_image_pid = str(int(time.time())) + str(random.randint(0, 10000)).zfill(5) + '.' + \
                           f.filename.split('.')[-1]
        dealed_path = os.path.join(basepath, 'static/images',dealed_image_pid)
        cv2.imwrite(dealed_path,img_cartoon)
        
       
        url_src = url_for('static', filename= './images/'+result_image_pid)
        url_dst = url_for('static', filename= './images/'+dealed_image_pid)
        return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)

    elif process_method == "ocr":
        message = "文字识别"
        str_ocr = img2text(img)
        str_info = "识别结果为： " + str_ocr
        url_src = url_for('static', filename= './images/'+result_image_pid)
        url_dst = url_for('static', filename= './images/blank.bmp')
        return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)

    elif process_method == "face_det":
        message = "人脸特效  "

        dict_effect = dict()

#         dic_effect = {
# #                 "hat": ["Normal","hat1.bmp"],
# #                 "eye": ["glasses","glasses.bmp"],
# #                 # "eye": ["double","left-eye.bmp","left-eye.bmp"]
# #             }

        style_hat = request.form.get("face_hat")
        if style_hat == "hat1":
            message = message+ "  礼帽"
            dict_effect.update({'hat':[]})
            dict_effect['hat'].append("Normal")
            dict_effect['hat'].append(os.path.join(basepath,'static','img_processing','hat1.bmp'))
        elif style_hat == "hat2":     
            message = message+ "  魔法帽"
            dict_effect.update({'hat':[]})
            dict_effect['hat'].append("Normal")
            dict_effect['hat'].append(os.path.join(basepath,'static','img_processing','hat2.bmp'))
        
        print("message1",message)
        style_eye = request.form.get("face_eye")

        if style_eye == "eye1":
            message = message + "   眼镜"
            dict_effect.update({'eye':[]})
            dict_effect['eye'].append("glasses")
            dict_effect['eye'].append(os.path.join(basepath,'static','img_processing','glasses.bmp'))
       
        elif style_eye == "eye2":
            message = message + "   卡通眼"
            dict_effect.update({'eye':[]})
            dict_effect['eye'].append("double")
            dict_effect['eye'].append(os.path.join(basepath,'static','img_processing','left-eye.bmp'))
            dict_effect['eye'].append(os.path.join(basepath,'static','img_processing','right-eye.bmp'))
             
        flag,img_dealed = face_effect(img,dict_effect,det_face,det_landmark)
        if flag:
            str_info = "特效添加成功"
            
             # 创建结果文件
            dealed_image_pid = str(int(time.time())) + str(random.randint(0, 10000)).zfill(5) + '.' + \
                               f.filename.split('.')[-1]
            dealed_path = os.path.join(basepath, 'static/images',dealed_image_pid)
            cv2.imwrite(dealed_path,img_dealed)
           
            url_src = url_for('static', filename= './images/'+result_image_pid)
            url_dst = url_for('static', filename= './images/'+dealed_image_pid)
            return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)
        else:
            str_info = "没有找到人脸"
            url_src = url_for('static', filename= './images/'+result_image_pid)
            url_dst = url_for('static', filename= './images/blank.jpg')
            return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)
  
    elif process_method == "face_beauty":
            message = " 美颜特效   "
            style_beauty = request.form.get("Face_Beauti")
            print("style_beauty",style_beauty)
            if style_beauty == "bigeye":
                message = message + " 大眼 "
                flag,img_out= big_eyes(img,det_face,det_landmark)
            elif style_beauty == "thinface":
                message = message + "  瘦脸"
                flag,img_out = thin_face(img,det_face,det_landmark)
            elif style_beauty == "colorLip":
                print("-----------lip in -----------------")
                message = message + "烈焰红唇"
                flag,img_out = color_lip(img)
                print("-------flag---------------",flag)

            if flag:
                str_info = "美颜添加成功"
                 # 创建结果文件
                dealed_image_pid = str(int(time.time())) + str(random.randint(0, 10000)).zfill(5) + '.' + \
                               f.filename.split('.')[-1]
                dealed_path = os.path.join(basepath, 'static/images',dealed_image_pid)
                cv2.imwrite(dealed_path,img_out)
           
                url_src = url_for('static', filename= './images/'+result_image_pid)
                url_dst = url_for('static', filename= './images/'+dealed_image_pid)
                return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)
            else:
                str_info = "没有找到人脸"
                url_src = url_for('static', filename= './images/'+result_image_pid)
                url_dst = url_for('static', filename= './images/blank.jpg')
                return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)
  
    return render_template('images.html',message=message)
    




m_camera = VideoCamera(0)

@app.route('/video',methods=['GET', 'POST'])
def videoshow():
    # get 方式访问，返回原始效果
    if request.method == 'GET':
        return render_template('video_effect.html',videourl=url_for('video_feed'),mess_effect="原始")
    
    # 获取视频显示方式
    video_effect = request.form.get("method_video_effect")
    
    if video_effect == "original":
        return render_template('video_effect.html',videourl=url_for('video_feed'),mess_effect="原始")
    elif video_effect == "edge":
        return render_template('video_effect.html',videourl=url_for('video_feed_edge'),mess_effect="边缘")
    elif video_effect == "gray":
        return render_template('video_effect.html',videourl=url_for('video_feed_gray'),mess_effect="灰度")
    elif video_effect == "cartoon":
        return render_template('video_effect.html',videourl=url_for('video_feed_cartoon'),mess_effect="灰度")
    
    return render_template('video_effect.html',videourl=url_for('video_feed'),mess_effect="原始")
        
  
     

# 原始效果
@app.route('/video_feed')
def video_feed():
    return Response(gen_effect(m_camera,'original'),mimetype='multipart/x-mixed-replace; boundary=frame')

# 灰度
@app.route('/video_feed_gray')
def video_feed_gray():
    return Response(gen_effect(m_camera,'gray'),mimetype='multipart/x-mixed-replace; boundary=frame')

# 边缘
@app.route('/video_feed_edge')
def video_feed_edge():
    return Response(gen_effect(m_camera,'edge'),mimetype='multipart/x-mixed-replace; boundary=frame')

# 卡通
@app.route('/video_feed_cartoon')
def video_feed_cartoon():
    return Response(gen_effect(m_camera,'cartoon'),mimetype='multipart/x-mixed-replace; boundary=frame')




      

@app.route('/',methods=['GET', 'POST'])
def face():
    if request.method == 'GET':

        opt_face['flag'] =False
        return render_template('video_face.html',videourl=url_for('video_face_rec'))
    
    
@app.route('/video_face_rec')
def video_face_rec():
    return Response(gen_face_recognition(m_camera,opt_face),mimetype='multipart/x-mixed-replace; boundary=frame')
    
    
@app.route('/checkFace',methods=['GET', 'POST'])
def checkFace():
    print(opt_face['flag'])
    if opt_face['flag'] == True:
        print("跳转")
        
        return jsonify({'flag':'True'})
    else:
        return jsonify({'flag':'Flase'})
    
    

if __name__ == '__main__':
    app.run(host='192.168.1.55', port=8080)    





