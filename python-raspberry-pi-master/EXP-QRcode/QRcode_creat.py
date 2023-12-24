
import qrcode
import cv2
import numpy as np

# 创建二维码图像
# s 二维码的内容
# file_img: 保存的二维码文件的名字
# label : 在生成的二维码图片上加标签
def creat_QRcode(s,file_img,label=None):
    
    # 生成二维码图像并保存
    img = qrcode.make(s)
    img.save(file_img)
    
    if not label is None:
        # 为 QRcode 加上文字说明
        img= cv2.imread(file_img)
        cv2.putText(img,label,(0,20),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
        cv2.imwrite(file_img,img)


if __name__ == "__main__":
    
    flag_list = ["light-on","light-off","temperature","buzzer-on","buzzer-off"]
    
    for flag in flag_list:
        s = flag
        file_img = flag+'.png'
        label = flag
        print("Creat QR code for %s"%(s))
        creat_QRcode(s,file_img,label)
    
    
    
    # 生成QRcode
    
    
    
    
    
    # s = 'light-on'
    # img_file = '%s.png'%(s)
    # img = qrcode.make(s)
    # img.save(img_file)
    
    # 为 QRcode 加上文字说明
    # img= cv2.imread(img_file)
    # cv2.putText(img,s,(0,20),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
    # cv2.imwrite(img_file,img)
    
