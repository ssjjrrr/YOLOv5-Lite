
# 采样率
SAMPLE_FREQ = 25
# 均值滤波
MA_SIZE = 4
# 缓冲区大小
BUFFER_SIZE = 100

def calc_hr(ir_data):
    # 计算均值
    ir_mean = int(np.mean(ir_data))
    
    # 减均值，前面加- ，为了计算波谷
    x = -1 * (np.array(ir_data) - ir_mean)
    
    # 进行均值滤波
    for i in range(x.shape[0] - MA_SIZE):
        x[i] = np.sum(x[i:i+MA_SIZE]) / MA_SIZE
        
    # 计算阈值，将阈值设置在30-60之间
    n_th = int(np.mean(x))
    n_th = 30 if n_th < 30 else n_th  # min allowed
    n_th = 60 if n_th > 60 else n_th  # max allowed
    
    # 获取信号中波谷的个数，以及波谷的位置
    ir_valley_locs, n_peaks = find_peaks(x, BUFFER_SIZE, n_th, min_dist=4, max_num=15)
    
    # 计算各个波谷的间距之和
    peak_interval_sum = 0
    
    if n_peaks >= 2:
        for i in range(1, n_peaks):
            peak_interval_sum += (ir_valley_locs[i] - ir_valley_locs[i-1])
        peak_interval_sum = int(peak_interval_sum / (n_peaks - 1))
        
        hr = int(SAMPLE_FREQ * 60 / peak_interval_sum)
        hr_valid = True
    else:
        hr = -999  # unable to calculate because # of peaks are too small
        hr_valid = False
    
    return hr_valid, hr

# 寻找峰值，峰值的高度>min_height, 峰值最多 max_num 个
#  峰值之间的间隔要<min_dist
# 返回峰值（波谷）的位置以及峰值的个数
def find_peaks(x, size, min_height, min_dist, max_num):
    
    # 寻找峰值
    ir_valley_locs, n_peaks = find_peaks_above_min_height(x, size, min_height, max_num)
    
    # 消除较大的峰值
    ir_valley_locs, n_peaks = remove_close_peaks(n_peaks, ir_valley_locs, x, min_dist)

    n_peaks = min([n_peaks, max_num])

    return ir_valley_locs, n_peaks

# 寻找大于min_height的峰值
def find_peaks_above_min_height(x, size, min_height, max_num):
    
    i = 0
    n_peaks = 0
    ir_valley_locs = []  # [0 for i in range(max_num)]
    while i < size - 1:
        
        # 寻找上升的潜在峰值
        if x[i] > min_height and x[i] > x[i-1]:  
            n_width = 1
            
            # 判断平台的情况
            while i + n_width < size - 1 and x[i] == x[i+n_width]:  # find flat peaks
                n_width += 1
            
            # x[i]>x[i-1] 且 x[i] > x[i+n_width] 说明发现峰值
            if x[i] > x[i+n_width] and n_peaks < max_num:  # find the right edge of peaks
                ir_valley_locs.append(i)
                n_peaks += 1  
                i += n_width + 1
            else:
                i += n_width
        else:
            i += 1

    return ir_valley_locs, n_peaks
    
def remove_close_peaks(n_peaks, ir_valley_locs, x, min_dist):
    
    # 根据幅度值进行排序
    sorted_indices = sorted(ir_valley_locs, key=lambda i: x[i])
    sorted_indices.reverse()

    i = -1
    while i < n_peaks:
        old_n_peaks = n_peaks
        n_peaks = i + 1
        
        # 以i为基准 j逐渐增加
        # 判断i，j 之间的距离 小于min_dist，则去掉该点，后面的点依次前移动
        
        # i 从-1 开始，表示距离起始位置小于 min_dist 的点都清除
        j = i + 1
        while j < old_n_peaks:
            n_dist = (sorted_indices[j] - sorted_indices[i]) if i != -1 else (sorted_indices[j] + 1)  # lag-zero peak of autocorr is at index -1
            if n_dist > min_dist or n_dist < -1 * min_dist:
                sorted_indices[n_peaks] = sorted_indices[j]
                n_peaks += 1  
            j += 1
        i += 1

    sorted_indices[:n_peaks] = sorted(sorted_indices[:n_peaks])

    return sorted_indices, n_peaks  


# 测试部分
if __name__ == "__main__":
    from max30102 import MAX30102
    import numpy as np
    import time
    buff_size = 100
   
    
    # 定义传感器
    sensor = MAX30102()
    flag_finger = False
    ir_data = []
    red_data = []
    bpms = []
    
    hr_mean = None
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
                            hr_mean = None
                        else:
                            flag_finger = True
                            # 计算心率
                            hr_valid, hr = calc_hr(red_data)
                            if hr_valid:
                                bpms.append(hr)
                            while len(bpms)>4:
                                bpms.pop(0)
                            
                                hr_mean = np.mean(bpms)
          
            time.sleep(1)
            if not flag_finger:
                print("flag_finger not find")
            else:
                if not hr_mean is None:
                    print("BPM: %.2f"%(hr_mean))
                
            
            
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')               
    finally:
        sensor.shutdown()

    
    
    