import requests
import os
import uuid
import pygame
import time


def tts_baidu(text,lang='zh',volume = 0.5,speed = 3):
    
    # 调用baiud网页截取MP3音频文件啊
    # 随机生成文件
    mp3_file = str(uuid.uuid4())+'.mp3'
    flag = getaudio(text,mp3_file,speed=speed,type=lang)
    
    if flag: 
        play_music(os.path.join("audios",mp3_file),volume=volume)
        # os.remove(os.path.join("audios",mp3_file))
    else:
        return False

def play_music(file,volume = 0.5):
        pygame.mixer.init(frequency=44100)
      
        # 加载音乐
        pygame.mixer.music.load(file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(start=0.0)
        
        #播放时长，没有此设置，音乐不会播放，会一次性加载完
        while pygame.mixer.music.get_busy():
            pass
       
        pygame.mixer.quit()
        
        
        
        
def getaudio(content,saveto,speed=3,type='en'):
    '''
    saveto:保存文件名称
    type:
    'en'英文,'zh'中文
    speed:语速
    '''
    url='https://fanyi.baidu.com/gettts'
    header={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36 Edg/89.0.774.45'
    }
    params={
    'lan': type,#语言类型，zh中文，en英文
    'text': content,
    'spd': speed,#语速,经测试应填写1~6之内的数字
    'source': 'web',
    }
    if not os.path.exists('audios'):
        os.mkdir('audios')
    response=requests.get(url,params=params,headers=header)
    
    if response.status_code == 200 and response.content:#保存音频文件
        file_save = os.path.join("audios",saveto)
        
        with open(file_save,'wb') as f:
            f.write(response.content)
            
            return True
    else:
       
        raise Exception
        return False
        
if __name__ == "__main__":
        
    tts_baidu("你好，鲁东大学",lang='zh',volume = 1,speed = 3)
    
    tts_baidu("你好，请打开收音机",lang='zh',volume = 0.1,speed = 3)
    
    
    
    
    
    