import RPi.GPIO as GPIO


class light():
    def __init__(self,pin):
        
        # 初始化
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin,GPIO.OUT)
        GPIO.output(self.pin,GPIO.LOW)
        
    def on(self):
        GPIO.output(self.pin,GPIO.HIGH)
        
    def off(self):
        GPIO.output(self.pin,GPIO.LOW)
        
        