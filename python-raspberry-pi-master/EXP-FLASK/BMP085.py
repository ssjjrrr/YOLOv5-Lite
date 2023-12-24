import logging
import time
import smbus

import threading
import RPi.GPIO as GPIO

# BMP085 默认地址.
BMP085_I2CADDR           = 0x77

# BMP085 读取气压的精度
BMP085_ULTRALOWPOWER     = 0 # 16bit
BMP085_STANDARD          = 1 # 17bit
BMP085_HIGHRES           = 2 # 18bit
BMP085_ULTRAHIGHRES      = 3 # 19bit

# BMP085 内部寄存器存储着用来对 温度 以及气压进行校正的系数
BMP085_CAL_AC1           = 0xAA  # R   Calibration data  int16
BMP085_CAL_AC2           = 0xAC  # R   Calibration data  int16
BMP085_CAL_AC3           = 0xAE  # R   Calibration data  int16
BMP085_CAL_AC4           = 0xB0  # R   Calibration data  unint16
BMP085_CAL_AC5           = 0xB2  # R   Calibration data  unint16
BMP085_CAL_AC6           = 0xB4  # R   Calibration data  unint16
BMP085_CAL_B1            = 0xB6  # R   Calibration data  int16 
BMP085_CAL_B2            = 0xB8  # R   Calibration data  int16
BMP085_CAL_MB            = 0xBA  # R   Calibration data  int16
BMP085_CAL_MC            = 0xBC  # R   Calibration data  int16
BMP085_CAL_MD            = 0xBE  # R   Calibration data  int16
# 控制字寄存器
BMP085_CONTROL           = 0xF4

# BMP085 命令字
BMP085_READTEMPCMD       = 0x2E
BMP085_READPRESSURECMD   = 0x34

# 数据寄存器 温度/气压
BMP085_TEMPDATA          = 0xF6
BMP085_PRESSUREDATA      = 0xF6

class BMP085(threading.Thread):
    def __init__(self, mode=BMP085_STANDARD, address=BMP085_I2CADDR,bus_id =1):
        super(BMP085, self).__init__() 
        # 检验模式是否正确.
        if mode not in [BMP085_ULTRALOWPOWER, BMP085_STANDARD, BMP085_HIGHRES, BMP085_ULTRAHIGHRES]:
            raise ValueError('Unexpected mode value {0}.  Set mode to one of BMP085_ULTRALOWPOWER, BMP085_STANDARD, BMP085_HIGHRES, or BMP085_ULTRAHIGHRES'.format(mode))
        self._mode = mode
        
        self._bus_id = bus_id
        
        self._device = smbus.SMBus(self._bus_id)
        
        self._address = address
       
        self._load_calibration()
        
        self.str_pressure = "    "
        self.str_altitude = "    "
        
    # 读取8位无符号数    
    def readU8(self, register):
        result = self._device.read_byte_data(self._address, register) & 0xFF
        return result    
    
    # 读取16位有符号数 大数在后   
    def readS16BE(self, register):
        result = self._device.read_word_data(self._address,register) & 0xFFFF
        result = ((result << 8) & 0xFF00) + (result >> 8)
        if result > 32767:
            result -= 65536
        return result
    
    # 读取16位无符号数 大数在后    
    def readU16BE(self, register):
        result = self._device.read_word_data(self._address,register) & 0xFFFF
        result = ((result << 8) & 0xFF00) + (result >> 8)
        return result
    
    # 写 8位无符号数
    def write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        value = value & 0xFF
        self._device.write_byte_data(self._address, register, value)
    
    # 读取标定值
    def _load_calibration(self):
        self.cal_AC1 = self.readS16BE(BMP085_CAL_AC1)   # INT16
        self.cal_AC2 = self.readS16BE(BMP085_CAL_AC2)   # INT16
        self.cal_AC3 = self.readS16BE(BMP085_CAL_AC3)   # INT16
        self.cal_AC4 = self.readU16BE(BMP085_CAL_AC4)   # UINT16
        self.cal_AC5 = self.readU16BE(BMP085_CAL_AC5)   # UINT16
        self.cal_AC6 = self.readU16BE(BMP085_CAL_AC6)   # UINT16
        self.cal_B1 = self.readS16BE(BMP085_CAL_B1)     # INT16
        self.cal_B2 = self.readS16BE(BMP085_CAL_B2)     # INT16
        self.cal_MB = self.readS16BE(BMP085_CAL_MB)     # INT16
        self.cal_MC = self.readS16BE(BMP085_CAL_MC)     # INT16
        self.cal_MD = self.readS16BE(BMP085_CAL_MD)     # INT16

    # 读取原始温度数据
    def read_raw_temp(self):
        # 写温度读取控制字
        self.write8(BMP085_CONTROL, BMP085_READTEMPCMD)
        # 延时5ms
        time.sleep(0.005)  # Wait 5ms
        # 读取温度值
        raw = self.readU16BE(BMP085_TEMPDATA)
        return raw
    
    # 读取原始压力数据  模式不同精度不同
    def read_raw_pressure(self):
        """Reads the raw (uncompensated) pressure level from the sensor."""
        self.write8(BMP085_CONTROL, BMP085_READPRESSURECMD + (self._mode << 6))
        if self._mode == BMP085_ULTRALOWPOWER:
            time.sleep(0.005)
        elif self._mode == BMP085_HIGHRES:
            time.sleep(0.014)
        elif self._mode == BMP085_ULTRAHIGHRES:
            time.sleep(0.026)
        else:
            time.sleep(0.008)
        msb = self.readU8(BMP085_PRESSUREDATA)
        lsb = self.readU8(BMP085_PRESSUREDATA+1)
        xlsb = self.readU8(BMP085_PRESSUREDATA+2)
        raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self._mode)
        
        return raw
    
    # 读取温度
    def read_temperature(self):
        """Gets the compensated temperature in degrees celsius."""
        UT = self.read_raw_temp()
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) // (X1 + self.cal_MD)
        B5 = X1 + X2
        temp = ((B5 + 8) >> 4) / 10.0
        
        return temp
    
    # 读取压力（单位Pa）
    def read_pressure(self):
       
        UT = self.read_raw_temp()
        UP = self.read_raw_pressure()
        
        # 计算温度系数 B5.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) // (X1 + self.cal_MD)
        B5 = X1 + X2
        
        # 压力计算
        B6 = B5 - 4000
        
        X1 = (self.cal_B2 * (B6 * B6) >> 12) >> 11
        X2 = (self.cal_AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.cal_AC1 * 4 + X3) << self._mode) + 2) // 4
        
        X1 = (self.cal_AC3 * B6) >> 13
        X2 = (self.cal_B1 * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.cal_AC4 * (X3 + 32768)) >> 15
        
        B7 = (UP - B3) * (50000 >> self._mode)
        
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        
        return p
    
    # 计算海拔高度
    def read_altitude(self, sealevel_pa=101325.0):
        pressure = float(self.read_pressure())
        altitude = 44330.0 * (1.0 - pow(pressure / sealevel_pa, (1.0/5.255)))
        return altitude
    
    # 计算海平面处大气压 （单位Pa）
    def read_sealevel_pressure(self, altitude_m=0.0):
        pressure = float(self.read_pressure())
        p0 = pressure / pow(1.0 - altitude_m/44330.0, 5.255)
        return p0
        
        
    def run(self):
        
        while True:
            pressure = self.read_pressure()
            self.str_pressure = "%d Pa"%(pressure)
            time.sleep(2)
            altitude = self.read_altitude()
            time.sleep(2)
            self.str_altitude = "%d m"%(altitude)
        
    def get_pressure(self):
        return self.str_pressure
    
    def get_altitude(self):
        return self.str_altitude
        
        
        
        
if __name__ == "__main__":
    sensor = BMP085(mode=1, address=0x77,bus_id =1)
    sensor.setDaemon(True)
    sensor.start()
    
    try:
        while True:
           
            time.sleep(2)
           
            print('气压 %s'%(sensor.get_pressure()))
            
            time.sleep(2)
            
            print('海拔 %s'%(sensor.get_altitude()))
            
            time.sleep(2)
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')

        
   