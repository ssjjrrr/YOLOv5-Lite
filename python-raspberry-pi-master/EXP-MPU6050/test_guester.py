import numpy as np 
import os
import uuid
from MPU6050 import MPU6050
import time

def MIN(a,b,c):
    return np.min([a,b,c])

def dis_abs(x, y):
    return abs(x-y)[0]
    
def NORM(x):
    return np.math.sqrt(np.dot(x,x))
    
def dis_ACC(x,y):
    scale = 0.5
    diff = x-y
    dis = np.dot(x,y)/( NORM(x) * NORM(y) + 1e-8)
    
    dis = (1-scale*dis) * NORM(diff)
    
    return dis
    
def estimate_dtw(A,B,dis_func=dis_ACC):
    
    N_A = len(A)
    N_B = len(B)
    
    D = np.zeros([N_A,N_B])
    D[0,0] = dis_func(A[0],B[0])
    
    # 左边一列
    for i in range(1,N_A):
        D[i,0] = D[i-1,0]+dis_func(A[i],B[0])
    # 下边一行
    for j in range(1,N_B):
        D[0,j] = D[0,j-1]+dis_func(A[0],B[j])
    # 中间部分
    for i in range(1,N_A):
        for j in range(1,N_B):        
            D[i,j] = dis_func(A[i],B[j])+min(D[i-1,j],D[i,j-1],D[i-1,j-1])
            
    # 路径回溯
    i = N_A-1
    j = N_B-1
    count =0
    d = np.zeros(max(N_A,N_B)*3)
    path = []
    while True:
        if i>0 and j>0:
            path.append((i,j))
            m = min(D[i-1, j],D[i, j-1],D[i-1,j-1])
            if m == D[i-1,j-1]:
                d[count] = D[i,j] - D[i-1,j-1]
                i = i-1
                j = j-1
                count = count+1
                
            elif m == D[i,j-1]:
                d[count] = D[i,j] - D[i,j-1]
                j = j-1
                count = count+1
    
            elif m == D[i-1, j]:
                d[count] = D[i,j] - D[i-1,j]
                i = i-1
                count = count+1
                
        elif i == 0 and j == 0:
            path.append((i,j))
            d[count] = D[i,j]
            count = count+1
            break
        
        elif i == 0:
            path.append((i,j))
            d[count] = D[i,j] - D[i,j-1]
            j = j-1
            count = count+1
        
        elif j == 0:
            path.append((i,j))
            d[count] = D[i,j] - D[i-1,j]
            i = i-1
            count = count+1
            
    mean = np.sum(d) / count
    return mean, path[::-1],D
    

def mov_record(MPU):
    data_record = []
    print('请在1.5s内完成动作')
    for i in range(50):
        time.sleep(0.03)
        accs=MPU.get_ACC()
        data_record.append(accs)
    print('动作结束')    
    return data_record

def get_mov_list(path):
    list_files = []
    list_labs = []
    
    if os.path.exists(path):
        
        # 遍历文件夹，找到.npy文件
        for root, ds, fs in os.walk(path):
            for f in fs:
                if f.endswith('.npy'):
                    fullname = os.path.join(root, f)
                    list_files.append(fullname)
        
        for file in list_files:
            lab = os.path.split(os.path.split(file)[0])[-1]
            list_labs.append(lab)
   
    else:
        print('this path not exist')
    
    return list_files,list_labs




if __name__ == "__main__":
    
    m_MPU = MPU6050(address = 0x68)
    data_path = "mov_record"
    try:
        while True:
            print('1 录制 2 测试 3 退出')
            opt = input()
            
            if opt == '1':
                str_mov = input('请输入动作名称')
                print('5 秒后开始录制动作 %s'%(str_mov))
                time.sleep(5)
                # 录制动作
                mov_data = mov_record(m_MPU)
                
                # 进行保存
                path = os.path.join(data_path,str_mov)
                os.makedirs(path,exist_ok = True)
                file_name = os.path.join(path,str(uuid.uuid4())+".npy")
                np.save(file_name,np.array(mov_data))
                continue
            
            elif opt == '2':
                print('5 秒后开始录制测试动作')
                time.sleep(5)
                test_mov = mov_record(m_MPU)
                
              
                scores = []
                files,labs = get_mov_list(data_path)
                
                if len(files)<1:
                    print('没有找到存储动作，请先进行动作录制')
                    continue
                
                # 计算捕捉的动作与存储动作的距离
                for file in files:
                    # 加载动作数据
                    data_train = np.load(file)
                    # 计算测试动作与存储动作之间的距离
                    score,_,_ = estimate_dtw(np.array(test_mov),data_train)
                    scores.append(score)
                
                # 找到最小值的距离
                print(scores)
                index = np.where(scores == np.min(scores))[0][0]
                print('测试动作为 '+labs[index])
               
                continue
                
            elif opt == '3':
                break
                
    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')            
                




    
    
    
    
    
    
    