import smbus
import time
import threading
import RPi.GPIO as GPIO
class PCF8591(threading.Thread):
    # 初始化输入器件的物理地址Address，以及I2C的通道编号
    def __init__(self,Address=0x48,bus_id=1):
        super(PCF8591, self).__init__() 
        self.bus_id = bus_id
        self.Address = Address
        self.bus = smbus.SMBus(self.bus_id)
        self.str_LUX = "     "
    
    # 读取对一个模拟通道的输入进行采样 chn为通道号 
    def AD_read(self,chn):
        
        # 写控制字
        if chn ==0:
            self.bus.write_byte(self.Address,0x00)
        if chn ==1:
            self.bus.write_byte(self.Address,0x01)
        if chn ==2:
            self.bus.write_byte(self.Address,0x02)
        if chn ==3:
            self.bus.write_byte(self.Address,0x03)
        
        # 读数据 如果通道号不在0-3之间那么会继续读上一个通道的数据
        return self.bus.read_byte(self.Address)
    
    # 进行DA输出，val为输入的数字量    
    def DA_write(self,val):
        # val的取值应当在0-255之间
        temp = int(val)
        if temp>255:
            temp =255
        if temp<0:
            temp=0
        # 写控制字 写数据    
        self.bus.write_byte_data(self.Address, 0x40, temp)

    def compute_LUX(self,N):

        if N == 255:
            N= N-1
            
        R = N/(255-N)*1000

        LUX = 40000*pow(R,-0.6021)

        return LUX
        
    
    def run(self):
        self.AD_read(0)
        while True:
            N = self.AD_read(10)
            LUX = self.compute_LUX(N)

            self.str_LUX = "%d"%(LUX)
            
            time.sleep(1)
        
    def get_LUX(self):
        return self.str_LUX
        
    
 
        
if __name__ == "__main__":
    
    m_AD_DA = PCF8591(Address=0x48,bus_id=1)
    m_AD_DA.setDaemon(True)
    m_AD_DA.start()
    
    try:
        while True:
            print(m_AD_DA.get_LUX(),' LUX')
        
            time.sleep(1)
     
    except KeyboardInterrupt:
        GPIO.cleanup()   
        print("\n Ctrl + C Quite")
    
    
    
    
    
    
 