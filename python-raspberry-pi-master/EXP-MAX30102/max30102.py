
from time import sleep
import smbus
# register addresses
REG_INTR_STATUS_1 = 0x00
REG_INTR_STATUS_2 = 0x01

REG_INTR_ENABLE_1 = 0x02
REG_INTR_ENABLE_2 = 0x03

REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_FIFO_CONFIG = 0x08

REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C

REG_LED2_PA = 0x0D
REG_PILOT_PA = 0x10
REG_MULTI_LED_CTRL1 = 0x11
REG_MULTI_LED_CTRL2 = 0x12

REG_TEMP_INTR = 0x1F
REG_TEMP_FRAC = 0x20
REG_TEMP_CONFIG = 0x21
REG_PROX_INT_THRESH = 0x30
REG_REV_ID = 0xFE
REG_PART_ID = 0xFF


class MAX30102():
    # by default, this assumes that the device is at 0x57 on channel 1
    def __init__(self, channel=1, address=0x57):
        # I2C初始化
        self.address = address
        self.channel = channel
        self.bus = smbus.SMBus(self.channel)
        
        # 芯片复位
        self.reset()
        sleep(1)  # wait 1 sec

        # 读取中断状态
        reg_data = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_1, 1)
        print("reset state",reg_data)
        
        # 进行初始化
        self.setup()
       
    def shutdown(self):
        """
        设备关闭
        """
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [0x80])

    def reset(self):
        """
        芯片复位
        """
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [0x40])

    def setup(self, led_mode=0x03):
        """
        芯片设置
        """
        # 中断设置
        self.bus.write_i2c_block_data(self.address, REG_INTR_ENABLE_1, [0xc0])
        self.bus.write_i2c_block_data(self.address, REG_INTR_ENABLE_2, [0x00])

        # FIFO写指针
        self.bus.write_i2c_block_data(self.address, REG_FIFO_WR_PTR, [0x00])
        # OVF_COUNTER[4:0]
        self.bus.write_i2c_block_data(self.address, REG_OVF_COUNTER, [0x00])
        # FIFO_读指针
        self.bus.write_i2c_block_data(self.address, REG_FIFO_RD_PTR, [0x00])

        # sample avg = 4, fifo rollover = false, fifo almost full = 15
        self.bus.write_i2c_block_data(self.address, REG_FIFO_CONFIG, [0x4f])

        # 0x02 for read-only, 0x03 for SpO2 mode, 0x07 multimode LED
        self.bus.write_i2c_block_data(self.address, REG_MODE_CONFIG, [led_mode])
        # 0b 0010 0111
        # SPO2_ADC range = 4096nA, SPO2 sample rate = 100Hz, LED pulse-width = 411uS
        self.bus.write_i2c_block_data(self.address, REG_SPO2_CONFIG, [0x27])

        # choose value for ~7mA for LED1
        self.bus.write_i2c_block_data(self.address, REG_LED1_PA, [0x24])
        # choose value for ~7mA for LED2
        self.bus.write_i2c_block_data(self.address, REG_LED2_PA, [0x24])
        # choose value fro ~25mA for Pilot LED
        self.bus.write_i2c_block_data(self.address, REG_PILOT_PA, [0x7f])

    # this won't validate the arguments!
    # use when changing the values from default
    def set_config(self, reg, value):
        self.bus.write_i2c_block_data(self.address, reg, value)

    def get_data_present(self):
        read_ptr = self.bus.read_byte_data(self.address, REG_FIFO_RD_PTR)
        write_ptr = self.bus.read_byte_data(self.address, REG_FIFO_WR_PTR)
        if read_ptr == write_ptr:
            return 0
        else:
            num_samples = write_ptr - read_ptr
            # account for pointer wrap around
            if num_samples < 0:
                num_samples += 32
            return num_samples

    def read_fifo(self):
        """
        从数据寄存器中读取一个样本.
        """
        red_led = None
        ir_led = None

        # read 1 byte from registers (values are discarded)
        reg_INTR1 = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_1, 1)
        reg_INTR2 = self.bus.read_i2c_block_data(self.address, REG_INTR_STATUS_2, 1)

        # read 6-byte data from the device
        d = self.bus.read_i2c_block_data(self.address, REG_FIFO_DATA, 6)

        # mask MSB [23:18]
        red_led = (d[0] << 16 | d[1] << 8 | d[2]) & 0x03FFFF
        ir_led = (d[3] << 16 | d[4] << 8 | d[5]) & 0x03FFFF

        return red_led, ir_led

    def read_sequential(self, amount=100):
        """
        This function will read the red-led and ir-led `amount` times.
        This works as blocking function.
        """
        red_buf = []
        ir_buf = []
        count = amount
        while count > 0:
            num_bytes = self.get_data_present()
            while num_bytes > 0:
                red, ir = self.read_fifo()

                red_buf.append(red)
                ir_buf.append(ir)
                num_bytes -= 1
                count -= 1

        return red_buf, ir_buf
        
        
def draw_pic(data,h=2500,w=1020):
    
    if  max(data)-min(data)>2500:
        print(max(data),min(data))
        return np.zeros((h,w,3),np.uint8)
    else:
        h = max(data)-min(data)
    
    img = np.zeros((h,w,3),np.uint8)
    h,w,_ = np.shape(img)
    N  = len(data)
    
    for i in range(1,N):
        p1_x = (i-1)*10+20
        p2_x = i*10+20
        
        p1_y = -(data[i-1] - min(data)) + h
        p2_y = -(data[i] - min(data)) + h
        
        if p1_y<0:
            p1_y = 0
        elif p1_y>h-1:
            p1_y = h-1
            
        if p2_y<0:
            p2_y = 0
        elif p2_y>h-1:
            p2_y = h-1
        
        cv2.line(img,(int(p1_x),int(p1_y)),(int(p2_x),int(p2_y)),(255,255,255),3)
    return img
        
    
    
    

if __name__ == "__main__":
    
    import numpy as np
    import cv2
    buff_size = 100
   
    
    # 定义传感器
    sensor = MAX30102()
    flag_finger = False
    ir_data = []
    red_data = []
    
    try:
        while True:
            
            # 获得FIFO中的样本数目
            num_bytes = sensor.get_data_present()
            if num_bytes > 0:
                # 依次读取数据   
                while num_bytes > 0:
                    red, ir = sensor.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)
                    # print("ir: %d  red :%d"%(ir,red))
                    
                    # 大于100个样本则删除开头的样本
                    while len(ir_data) > buff_size:
                        ir_data.pop(0)
                        red_data.pop(0)
                    if len(ir_data) == buff_size:
                        if (np.mean(ir_data) < 50000 and np.mean(red_data) < 50000):
                            flag_finger = False
                        else:
                            flag_finger = True
                            
            sleep(1)
            if not flag_finger:
                print("flag_finger not find")
            else:
                img = draw_pic(ir_data)
                h,w,_ = np.shape(img)
                print(np.shape(img))
                if h<2500:
                    np.save("ir.npy", np.array(ir_data), allow_pickle=True)
                    cv2.imwrite("img.jpg",img)
                
            
            
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')               
    finally:
        sensor.shutdown()




