from flask import Flask, render_template, Response, request,jsonify,redirect,url_for
from imgprocessing import img2gray,img2edge,img2cartoon,img2text,big_eyes,thin_face,face_effect,color_lip,get_face_detector
import os
import time
from werkzeug.utils import secure_filename
import cv2
import dlib

print("加载人脸检测器")
det_face = dlib.get_frontal_face_detector()

    # 加载标志点检测器
det_landmark = dlib.shape_predictor("shape_predictor_68_face_landmarks_GTX.dat")  # 68点

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 
app = Flask(__name__)


# 定义路由
@app.route('/',methods=['GET', 'POST'])
def imgprocessing():

    # get 方式访问，返回页面
    if request.method == 'GET':
        return render_template('images.html')

    # pos 方式访问 首先进行文件的验证
    if request.method == 'POST':
         f = request.files['file']
         if not (f and allowed_file(f.filename)):
              return render_template('images.html',message="上传文件格式错误")
    
    basepath = os.path.dirname(__file__)
    upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))
    f.save(upload_path)

      
    # 把输入的文件统一命名成test.jpg
    img = cv2.imread(upload_path)
    # 在这里加一段缩小图像的程序
    cv2.imwrite(os.path.join(basepath, 'static/images', 'test.jpg'), img)

    # 获取图像处理方式
    process_method = request.form.get("method_img_process")
    print('process_method',process_method)

    # 所有处理后的文件都命名为dealed.jpg
    result_img_file = os.path.join(basepath, 'static/images', 'dealed.jpg')
    
    # 若文件存在，先删除
    if os.path.exists(result_img_file):
        os.remove(result_img_file)

    # 根据不同的处理方式进行处理
    if process_method == "gray":
        message = " 灰度转换"
        img_gray= img2gray(img)
        cv2.imwrite(result_img_file,img_gray)
        str_info = "转换成功"
        url_src = url_for('static', filename= './images/test.jpg')
        url_dst = url_for('static', filename= './images/dealed.jpg')
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
        cv2.imwrite(result_img_file,img_edge)
        str_info = "边缘提取成功"
        url_src = url_for('static', filename= './images/test.jpg')
        url_dst = url_for('static', filename= './images/dealed.jpg')
        return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)

    elif process_method == "effect_cartoon":
        message = "卡通效果"
        print("卡通效果")
        img_cartoon = img2cartoon(img)
        cv2.imwrite(result_img_file,img_cartoon)
        str_info = "卡通效果展示"
        url_src = url_for('static', filename= './images/test.jpg')
        url_dst = url_for('static', filename= './images/dealed.jpg')
        return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)


    elif process_method == "ocr":
        message = "文字识别"
        str_ocr = img2text(img)
        str_info = "识别结果为： " + str_ocr
        url_src = url_for('static', filename= './images/test.jpg')
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
            cv2.imwrite(result_img_file,img_dealed)
            url_src = url_for('static', filename= './images/test.jpg')
            url_dst = url_for('static', filename= './images/dealed.jpg')
            return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)
        else:
            str_info = "没有找到人脸"
            url_src = url_for('static', filename= './images/test.jpg')
            url_dst = url_for('static', filename= './images/dealed.jpg')
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
                cv2.imwrite(result_img_file,img_out)
                url_src = url_for('static', filename= './images/test.jpg')
                url_dst = url_for('static', filename= './images/dealed.jpg')
                return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)
            else:
                str_info = "没有找到人脸"
                url_src = url_for('static', filename= './images/test.jpg')
                url_dst = url_for('static', filename= './images/dealed.jpg')
                return render_template('img_ok.html',
                                method=message,
                                url_src=url_src,
                                url_dst=url_dst,
                                info_result =str_info)
  

            
    
    return render_template('images.html',message=message)
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)    





