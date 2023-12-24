import smbus
import math
import time
# MPU6050 I2C 物理地址
MPU6050_ADDR=0x68

# MPU6050 采样率的设置寄存器
MPU6050_SMPLRT_DIV=0x19

# MPU6050配置寄存器用来设置是否需要外置同步帧
# 设置对3轴加速度输出以及3轴陀螺仪输出进行数字低通滤波的方式
MPU6050_CONFIG=0x1a

#设置3轴陀螺仪输出量程的寄存器
MPU6050_GYRO_CONFIG=0x1b

# 设置3轴加速度输出量程的寄存器
MPU6050_ACCEL_CONFIG=0x1c

# 设置MPU6050的工作方式的寄存器 睡眠/循环/ 内部时钟。。。
MPU6050_PWR_MGMT_1=0x6b


# MPU6050 3轴加速计的数据地址
MPU6050_ACCX_DATA=0x3b
MPU6050_ACCY_DATA=0x3d
MPU6050_ACCZ_DATA=0x3f

# MPU6050 3轴陀螺仪的数据地址
MPU6050_GYROX_DATA=0x43
MPU6050_GYROY_DATA=0x45
MPU6050_GYROZ_DATA=0x47

class MPU6050(object):
    def __init__(self, address = MPU6050_ADDR, bus = 1,scal_acc=4,scal_gyro=1000):
        self.bus = smbus.SMBus(bus)
        self.address = address
        
        # 设置工作在默认的8kHZ下
        self.bus.write_byte_data(self.address,MPU6050_SMPLRT_DIV,0x00)
        # 不需要外置帧同步、滤波器工作在方式0
        self.bus.write_byte_data(self.address,MPU6050_CONFIG,0x00)
        # 设置陀螺仪的工作量程为  +- 500°/s
        self.bus.write_byte_data(self.address,MPU6050_GYRO_CONFIG,0x08)
        # 设置加速度计的量程为 +- 2g
        self.bus.write_byte_data(self.address,MPU6050_ACCEL_CONFIG,0x00)
        # 设置MPU6050的工作方式为采用内部8k时钟
        self.bus.write_byte_data(self.address,MPU6050_PWR_MGMT_1,0x00)
        
        self.scal_acc = 65536.0/scal_acc/9.8
        self.scal_gyro = 65536.0/scal_gyro
  
    def red_word_2c(self,address):
        high = self.bus.read_byte_data(self.address,address)
        low = self.bus.read_byte_data(self.address,address+1)
        val = (high<<8)+low
        if (val>=0x8000):
            return -((65535-val)+1)
        else: 
            return val
                
    def get_rawAcc(self):
        rawAccX = self.red_word_2c(MPU6050_ACCX_DATA);
        rawAccY = self.red_word_2c(MPU6050_ACCY_DATA);
        rawAccZ = self.red_word_2c(MPU6050_ACCZ_DATA);
        return rawAccX,rawAccY,rawAccZ
        
    def get_ACC(self):
        rawAccX,rawAccY,rawAccZ = self.get_rawAcc()
        accX = rawAccX/self.scal_acc
        accY = rawAccY/self.scal_acc
        accZ = rawAccZ/self.scal_acc
        return accX,accY,accZ
        
    def get_rawGyro(self):
        rawGyroX = self.red_word_2c(MPU6050_GYROX_DATA);
        rawGyroY = self.red_word_2c(MPU6050_GYROY_DATA);
        rawGyroZ = self.red_word_2c(MPU6050_GYROZ_DATA);
        return rawGyroX,rawGyroY,rawGyroZ
    
    def get_Gyro(self):
        rawGyroX,rawGyroY,rawGyroZ =self.get_rawGyro()        
        GyroX = rawGyroX/self.scal_gyro
        GyroY = rawGyroY/self.scal_gyro
        GyroZ = rawGyroZ/self.scal_gyro    
        return GyroX,GyroY,GyroZ
        
    def calc_GyroOffsets(self):
        x =0
        y =0
        z =0
        for i in range(3000):
            rx,ry,rz = self.get_Gyro()
            x = x + rx
            y = y + ry
            z = z + rz
            
        gyroXoffset = x/3000
        gyroYoffset = y/3000
        gyroZoffset = z/3000
        
        return gyroXoffset,gyroYoffset,gyroZoffset
        
    def  calc_angleAcc(self):
        accX,accY,accZ  = self.get_ACC()
        
        angleAccX = math.degrees(math.atan2(accY, math.sqrt(accZ * accZ + accX * accX)))
        angleAccY = math.degrees(math.atan2(accX, math.sqrt(accZ * accZ + accY * accY)))
        
        return angleAccX,angleAccY
        
if __name__ == "__main__":
    time.sleep(0.1)
    print('开始计算Gyro偏置')
    m_MPU = MPU6050(address = 0x68)
    GyroOffsets=m_MPU.calc_GyroOffsets()
    print('Gyro偏置为：\n x_offset = %.2f y_offset = %.2f z_offset = %.2f'%(GyroOffsets[0],GyroOffsets[1],GyroOffsets[2]))
    try:
        while True:
            time.sleep(0.001)
            
            acc_x,acc_y,acc_z=m_MPU.get_ACC()
            print('acc_x = %.2f acc_y = %.2f  acc_z = %.2f'%(acc_x,acc_y,acc_z))
            
            # gyro_x,gyro_y,gyro_z=m_MPU.get_Gyro()
            
            # print('gyro_x = %.2f gyro_y = %.2f  gyro_z = %.2f'%(gyro_x,gyro_y,gyro_z))
            
            # angleAccX,angleAccY= m_MPU.calc_angleAcc()
            
            # print('angleAccX= %.2f,angleAccY=%.2f'%(angleAccX,angleAccY))
        
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
        
        
      
        
        