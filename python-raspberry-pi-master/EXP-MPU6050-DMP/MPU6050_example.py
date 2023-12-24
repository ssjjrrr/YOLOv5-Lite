from MPU6050 import MPU6050
import time

if __name__ == "__main__":
    i2c_bus = 1
    device_address = 0x68

    x_accel_offset = int(926)
    y_accel_offset = int(2136)
    z_accel_offset = int(-856)
    x_gyro_offset = int(36)
    y_gyro_offset = int(-8)
    z_gyro_offset = int(-28)

    # x_avg_read: 0.08 x_avg_offset: 926.423499999996
    # y_avg_read: -0.72 y_avg_offset: 2136.152999999997
    # z_avg_read: 0.34 z_avg_offset: -856.0713749999996
    # x_avg_read: 0.16 x_avg_offset: 35.570499999999996
    # y_avg_read: -0.07 y_avg_offset: -8.081437499999883
    # z_avg_read: -0.01 z_avg_offset: -28.00306249999999

    enable_debug_output = True
    mpu = MPU6050(i2c_bus, device_address, x_accel_offset, y_accel_offset,z_accel_offset, x_gyro_offset, y_gyro_offset, z_gyro_offset,enable_debug_output)

    mpu.dmp_initialize()
    mpu.set_DMP_enabled(True)
    mpu_int_status = mpu.get_int_status()
    print(hex(mpu_int_status))

    packet_size = mpu.DMP_get_FIFO_packet_size()
    print(packet_size)
    FIFO_count = mpu.get_FIFO_count()
    print(FIFO_count)

    FIFO_buffer = [0]*64
    try:
        while True:
            try:
                FIFO_count = mpu.get_FIFO_count()
                mpu_int_status = mpu.get_int_status()
            except:
                continue
            # If overflow is detected by status or fifo count we want to reset
            if (FIFO_count == 1024) or (mpu_int_status & 0x10):
                mpu.reset_FIFO()
                print('overflow!')
            # Check if fifo data is ready
            elif (mpu_int_status & 0x02):
                # Wait until packet_size number of bytes are ready for reading, default
                # is 42 bytes
                while FIFO_count < packet_size:
                    FIFO_count = mpu.get_FIFO_count()
                FIFO_buffer = mpu.get_FIFO_bytes(packet_size)
                accel = mpu.DMP_get_acceleration_int16(FIFO_buffer)
                quat = mpu.DMP_get_quaternion_int16(FIFO_buffer)
                grav = mpu.DMP_get_gravity(quat)
                roll_pitch_yaw = mpu.DMP_get_euler_roll_pitch_yaw(quat, grav)
                
                str_show = "roll: %.2f  pitch: %.2f  yaw: %.2f        "%(roll_pitch_yaw.x,roll_pitch_yaw.y,roll_pitch_yaw.z)
              
                print("\r %s"%(str_show),end='')
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')
           

    