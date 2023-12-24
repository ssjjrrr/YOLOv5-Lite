import cv2
import numpy as np
import time
from threading import Thread

def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    """
    description: Plots one bounding box on image img,
                 this function comes from YoLov5 project.
    param: 
        x:      a box likes [x1,y1,x2,y2]
        img:    a opencv image object
        color:  color to draw rectangle, such as (0,255,0)
        label:  str
        line_thickness: int
    return:
        no return
    """
    tl = (
        line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1
    )  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(
            img,
            label,
            (c1[0], c1[1] - 2),
            0,
            tl / 3,
            [225, 255, 255],
            thickness=tf,
            lineType=cv2.LINE_AA,
        )

def post_process_opencv(outputs,model_h,model_w,img_h,img_w,thred_nms,thred_cond):
    
    conf = outputs[:,4].tolist()
    c_x = outputs[:,0]/model_w*img_w
    c_y = outputs[:,1]/model_h*img_h
    w  = outputs[:,2]/model_w*img_w
    h  = outputs[:,3]/model_h*img_h
    p_cls = outputs[:,5:]
    if len(p_cls.shape)==1:
        p_cls = np.expand_dims(p_cls,1)
    cls_id = np.argmax(p_cls,axis=1)

    p_x1 = np.expand_dims(c_x-w/2,-1)
    p_y1 = np.expand_dims(c_y-h/2,-1)
    p_x2 = np.expand_dims(c_x+w/2,-1)
    p_y2 = np.expand_dims(c_y+h/2,-1)
    areas = np.concatenate((p_x1,p_y1,p_x2,p_y2),axis=-1)
    # print(areas.shape) 
    areas = areas.tolist()
    ids = cv2.dnn.NMSBoxes(areas,conf,thred_cond,thred_nms)
    if len(ids)>0:
        return  np.array(areas)[ids],np.array(conf)[ids],cls_id[ids]
    else:
        return [],[],[]

def infer_image(net,img0,model_h,model_w,thred_nms=0.4,thred_cond=0.5):

    img = img0.copy()
    img = cv2.resize(img,[model_h,model_w])
    blob = cv2.dnn.blobFromImage(img, scalefactor=1/255.0, swapRB=True)
    net.setInput(blob)
    outs = net.forward()[0]
    
    det_boxes,scores,ids = post_process_opencv(outs,model_h,model_w,img0.shape[0],img0.shape[1],thred_nms,thred_cond)
    return det_boxes,scores,ids
   
global det_boxes_show

global scores_show

global ids_show

global FPS_show


def m_detection(net,cap,model_h,model_w):
    global det_boxes_show
    global scores_show
    global ids_show
    global FPS_show
    while True:
        success, img0 = cap.read()
        if success:
 
            t1 = time.time()
            det_boxes,scores,ids = infer_image(net,img0,model_h,model_w,thred_nms=0.4,thred_cond=0.4)
            t2 = time.time()
            str_fps = "FPS: %.2f"%(1./(t2-t1))
            
            
            det_boxes_show = det_boxes
            scores_show = scores
            ids_show = ids
            FPS_show = str_fps
            
            # time.sleep(5)

if __name__=="__main__":
    dic_labels= {0:'led',
            1:'buzzer',
            2:'teeth'}

    model_h = 640
    model_w = 640
    file_model = 'best-led-640.onnx'
    net = cv2.dnn.readNet(file_model)
    
    video = 0
    cap = cv2.VideoCapture(video)
    
    m_thread = Thread(target=m_detection, args=([net,cap,model_h,model_w]),daemon=True)
    m_thread.start()
    
    global det_boxes_show
    global scores_show
    global ids_show
    global FPS_show
    
    
    
    det_boxes_show = []

    scores_show = []

    ids_show  =[]

    FPS_show = ""
    
    while True:
        success, img0 = cap.read()
        if success:
            
            for box,score,id in zip(det_boxes_show,scores_show,ids_show):
                label = '%s:%.2f'%(dic_labels[id],score)
                plot_one_box(box, img0, color=(255,0,0), label=label, line_thickness=None)
                
            str_FPS = FPS_show
            
            cv2.putText(img0,str_FPS,(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),3)
            
            
            cv2.imshow("video",img0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release() 
    
    
    
    
    
    
    
    
    
    