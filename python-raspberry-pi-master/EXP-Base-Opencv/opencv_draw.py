import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def paint_chinese_opencv(im,chinese,pos,color,font_size=20):
    img_PIL = Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype('NotoSansCJK-Bold.ttc',font_size,encoding="utf-8")
    fillColor = color #(255,0,0)
    position = pos #(100,100)
    draw = ImageDraw.Draw(img_PIL)
    draw.text(position,chinese,fillColor,font)
    img = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)
    return img


if __name__ == "__main__":
    
    # 创建一个纯黑的图像用来进行绘图展示
    img = np.zeros((512,512,3),np.uint8)

    # 画直线
    cv2.line(img,(0,0),(img.shape[1],img.shape[0]),(0,255,0),3)

    # 画矩形 空心
    cv2.rectangle(img,(0,0),(250,350),(0,0,255),2)

    # 画矩形 实心
    cv2.rectangle(img,(100,100),(200,200),(255,0,0),cv2.FILLED )

    # 画圆形 空心
    cv2.circle(img,(400,50),30,(255,255,0),5)

    # 画圆形 实心
    cv2.circle(img,(450,80),30,(0,255,255),cv2.FILLED)

    #英文文字输出
    #          图像   文字     位置（左下）      字体             字号  颜色  线宽
    cv2.putText(img," OPENCV  ",(300,200),cv2.FONT_HERSHEY_COMPLEX,1,(0,150,0),3)

    # 中文文字输出                              位置         颜色       字号
    img = paint_chinese_opencv(img, "这是中文", (350,200), (0, 255,255), 20)

    cv2.imshow("Image",img)
    cv2.waitKey(0)