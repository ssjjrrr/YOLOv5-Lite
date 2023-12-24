import threading
import RPi.GPIO as GPIO
from pin_dic import pin_dic
import time

class Buzzer(object):
    
    def __init__(self,pin):
        
        self.pin_buzzer = pin
        GPIO.setup(self.pin_buzzer,GPIO.OUT)
        
        self.Buzzer = GPIO.PWM(self.pin_buzzer , 440)
        self.Buzzer.start(0)
        
        self.note2freq = {"cl1":131,"cl2":147 ,'cl3':165 ,"cl4":175 ,"cl5":196 ,"cl6":211 ,"cl7":248,
                          "cm1":262,"cm2":294 ,'cm3':330 ,"cm4":350 ,"cm5":393 ,"cm6":441 ,"cm7":495,
                          "ch1":525,"ch2":589 ,'ch3':661 ,"ch4":700 ,"ch5":786 ,"ch6":882 ,"ch7":990
                          }
        self.delay_beat = 0.3
        
    
    def play_one_note(self,note,beat):
        self.Buzzer.ChangeDutyCycle(50)
        self.Buzzer.ChangeFrequency(self.note2freq[note])
        time.sleep(self.delay_beat*beat)
    # def delay_one_beat(self,beat)
        # time.sleep(self.delay_beat*beat)
        
    def play_silce(self):
        self.Buzzer.ChangeDutyCycle(0)
        
        
class Play_Buzzer(threading.Thread):
    def __init__(self,pin,notes,beats):
        super(Play_Buzzer, self).__init__()
        
        
        self.m_buzzer =  Buzzer(pin)
        self.notes = notes
        self.beats = beats
        
        self.flag_run = 0
        self.flag_beak = 0
        
    def dobreak(self):
        self.flag_beak = 1
        
        
    def dostart(self):
        self.flag_run = 1
        
    def dostop(self):
        self.flag_run = 0
        
    
    def getState(self):
        return self.flag_run
        
    
    def run(self):
        
        while True:
            for note,beat in zip(self.notes,self.beats):
                
                if self.flag_beak:
                    break
                
                if not self.flag_run:
                    self.m_buzzer.play_silce()
                else: 
                    self.m_buzzer.play_one_note(note,beat)
                
if __name__ == "__main__":
    
    GPIO.setmode(GPIO.BOARD)
    
    pin_buzzer = pin_dic['G27']
    
    notes = ['cm1' ,'cm1' , 'cm1' , 'cl5' , 'cm3' , 'cm3' , 'cm3' , 'cm1' ,
             'cm1' , 'cm3' , 'cm5' , 'cm5' , 'cm4' , 'cm3' , 'cm2' , 'cm2' ,
             'cm3' , 'cm4' , 'cm4' , 'cm3' , 'cm2' , 'cm3' , 'cm1' , 'cm1' ,
             'cm3' , 'cm2' , 'cl5' , 'cl7', 'cm2' , 'cm1']
    beats = [1 , 1 , 2 , 2 , 1 , 1 , 2 , 2 ,
            1 , 1 , 2 , 2 , 1 , 1 , 3 , 1 ,
            1 , 2 , 2 , 1 , 1 , 2 , 2 , 1 ,
            1 , 2 , 2 , 1 , 1 , 3]
            
    m_play_buzzer = Play_Buzzer(pin_buzzer,notes,beats)
    
    m_play_buzzer.setDaemon(True)
    
    print("run")
    if not m_play_buzzer.getState():
        m_play_buzzer.dostart()
        m_play_buzzer.start()
        
    time.sleep(10)
    
    print("stop")
    m_play_buzzer.dostop()
    time.sleep(10)
    print("run")
    m_play_buzzer.dostart()
    time.sleep(10)
    
    
    m_play_buzzer.dobreak()
    GPIO.cleanup()
    
    
    
    
    
    
    
    
    
    
    
    
    
                    
        
        



        
        
        
        
        
        
        
        
        
        
        
        
        
        
