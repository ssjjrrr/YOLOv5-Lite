import pyttsx3

if __name__ == "__main__":
    
    # 引擎初始化
    engin = pyttsx3.init("espeak")
    
    # 设置语言
    # engin.setProperty('voice',"zh-yue")  # 粤语
    
    engin.setProperty('voice',"en")    # 中文
    
    # 设置音量 取值 0-1
    engin.setProperty('volume',0.4)
    
    # 设置语速 不超过500
    # rate = engin.getProperty('rate') 
    # print(rate)
    engin.setProperty('rate', 175)
    
    # 输出语音 1
    engin.say("hello world")
    engin.runAndWait()
    
    # 输出语音2
    engin.say("open the light")
    engin.runAndWait()
    
   