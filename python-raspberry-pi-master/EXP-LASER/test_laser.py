import RPi.GPIO as GPIO
import time
from pin_dic import pin_dic


if __name__ == "__main__":
    pin_sig = pin_dic['G17']

    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(pin_sig, GPIO.OUT)   # Set LedPin's mode is output
    GPIO.output(pin_sig, GPIO.HIGH) #

    try:
        while True:
            print('...Laser on')
            GPIO.output(pin_sig, GPIO.HIGH)  # led on
            time.sleep(3)
            print('Laser off...')
            GPIO.output(pin_sig, GPIO.LOW) # led off
            time.sleep(3)
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
        
    finally:
        
        GPIO.cleanup()  