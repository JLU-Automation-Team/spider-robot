from machine import I2C, Pin
from ssd1306 import SSD1306_I2C
import utime
import mpu6050
import network, time, _thread
import usocket as socket


#基本定义和初始化
i2c_mpu = I2C(scl=Pin(5), sda=Pin(4))
imu = mpu6050.accel(i2c_mpu)
i2c_oled = I2C(sda=Pin(13), scl=Pin(14)) 
oled = SSD1306_I2C(128, 64, i2c_oled, addr=0x3c) #前两个参数是分辨率，后两个是i2c地址

#水平校准常量
gyro_calib_Z = 1.28/4
gyro_calib_Y = 0.04/4
gyro_calib_X = -5.46/4
accel_calib_X = 0
accel_calib_Y = 0
accel_calib_Z = 0
earth_G = 11

# 响应头
responseHeaders = b'''
HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

'''



def get_gyro_rad():
    """ 删除无关项，仅保留换算后的角加速度，并延迟100ms(没什么用，因为不计算yaw)
    """
    
    imu_dict_gyro = imu.get_values()
    del imu_dict_gyro['Tmp']
    del imu_dict_gyro['AcX']
    del imu_dict_gyro['AcY']
    del imu_dict_gyro['AcZ']
    imu_dict_gyro['GyX'] = imu_dict['GyX']*0.03051757812/4-gyro_calib_X
    imu_dict_gyro['GyY'] = imu_dict['GyY']*0.03051757812/4-gyro_calib_Y
    imu_dict_gyro['GyZ'] = imu_dict['GyZ']*0.03051757812/4-gyro_calib_Z
    utime.sleep_ms(100)
    return imu_dict_gyro

def get_tilt():
    """
    利用与重力夹角求得两个倾斜角，并延迟10ms,
    tilt_X, tilt_Y是cos值，正向正半轴低头，负向正半轴仰头。
    tilt_Z是绕z轴角速度
    """
    
    imu_dict_accel = imu.get_values()
    del imu_dict_accel['Tmp']
    del imu_dict_accel['GyX']
    del imu_dict_accel['GyY']
    #del imu_dict_accel['GyZ']
    imu_dict_accel['AcX'] = imu_dict_accel['AcX']*0.00059814453-accel_calib_X
    imu_dict_accel['AcY'] = imu_dict_accel['AcY']*0.00059814453-accel_calib_Y
    #imu_dict_accel['AcZ'] = imu_dict_accel['AcZ']*0.00059814453-accel_calib_Z
    imu_dict_accel['GyZ'] = imu_dict_accel['GyZ']*0.03051757812/4-gyro_calib_Z

    tilt_X = (imu_dict_accel['AcX']/earth_G)
    tilt_Y = (imu_dict_accel['AcY']/earth_G)
    tilt_Z = (imu_dict_accel['GyZ'])
    del imu_dict_accel['AcZ']
    tilt_angle = {"tilt_X": tilt_X, "tilt_Y": tilt_Y, "rot_Z": tilt_Z}
    utime.sleep_ms(10)
    return tilt_angle

def judge_instruct():
    """取最新的五个重力角余弦求平均,统计得到方向。X正为B，负为F。Y正为R，负为L. C是顺时针，A是逆时针。
    """
    
    avg_tilt_X = 0
    samp_X = 1
    while samp_X <= 5:
        avg_tilt_X = get_tilt()["tilt_X"] + avg_tilt_X
        samp_X = samp_X + 1
    avg_tilt_X = avg_tilt_X/5
    
    avg_tilt_Y = 0
    samp_Y = 1
    while samp_Y <= 5:
        avg_tilt_Y = get_tilt()["tilt_Y"] + avg_tilt_Y
        samp_Y = samp_Y + 1
    avg_tilt_Y = avg_tilt_Y/5

    avg_tilt_Z = 0
    samp_Z = 1
    while samp_Z <= 5:
        avg_tilt_Z = get_tilt()["rot_Z"] + avg_tilt_Z
        samp_Z = samp_Z + 1
    avg_tilt_Z = avg_tilt_Z/5

    #等级判断
    instruction_X = "X"
    if avg_tilt_X <= 0.1 and avg_tilt_X > 0:
        instruction_X = "F0"
    elif avg_tilt_X <= 0.2 and avg_tilt_X > 0.1:
        instruction_X = "F1"
    elif avg_tilt_X <= 0.3 and avg_tilt_X > 0.2:
        instruction_X = "F2"
    elif avg_tilt_X <= 0.4 and avg_tilt_X > 0.3:
        instruction_X = "F3"
    elif avg_tilt_X <= 0.5 and avg_tilt_X > 0.4:
        instruction_X = "F4"
    elif avg_tilt_X <= 0.6 and avg_tilt_X > 0.5:
        instruction_X = "F5"
    elif avg_tilt_X <= 0.7 and avg_tilt_X > 0.6:
        instruction_X = "F6"
    elif avg_tilt_X <= 0.8 and avg_tilt_X > 0.7:
        instruction_X = "F7"
    elif avg_tilt_X <= 0.9 and avg_tilt_X > 0.8:
        instruction_X =  "F8"
    elif avg_tilt_X <= 1 and avg_tilt_X > 0.9:
        instruction_X =  "F9"
    elif avg_tilt_X > 1:
        instruction_X =  "F10"    
    elif avg_tilt_X >= -0.1 and avg_tilt_X < 0:
        instruction_X =  "B0"
    elif avg_tilt_X >= -0.2 and avg_tilt_X < -0.1:
        instruction_X =  "B1"
    elif avg_tilt_X >= -0.3 and avg_tilt_X < -0.2:
        instruction_X =  "B2"
    elif avg_tilt_X >= -0.4 and avg_tilt_X < -0.3:
        instruction_X =  "B3"
    elif avg_tilt_X >= -0.5 and avg_tilt_X < -0.4:
        instruction_X =  "B4"
    elif avg_tilt_X >= -0.6 and avg_tilt_X < -0.5:
        instruction_X =  "B5"
    elif avg_tilt_X >= -0.7 and avg_tilt_X < -0.6:
        instruction_X =  "B6"
    elif avg_tilt_X >= -0.8 and avg_tilt_X < -0.7:
        instruction_X =  "B7"
    elif avg_tilt_X >= -0.9 and avg_tilt_X < -0.8:
        instruction_X =  "B8"
    elif avg_tilt_X >= -1 and avg_tilt_X < -0.9:
        instruction_X =  "B9"
    elif avg_tilt_X < -1:
        instruction_X =  "B10"
    else:
        instruction_X =  "X"
    

    #等级判断
    instruction_Y = "Y"
    if avg_tilt_Y <= 0.1 and avg_tilt_Y > 0:
        instruction_Y =  "L0"
    elif avg_tilt_Y <= 0.2 and avg_tilt_Y > 0.1:
        instruction_Y =  "L1"
    elif avg_tilt_Y <= 0.3 and avg_tilt_Y > 0.2:
        instruction_Y =  "L2"
    elif avg_tilt_Y <= 0.4 and avg_tilt_Y > 0.3:
        instruction_Y =  "L3"
    elif avg_tilt_Y <= 0.5 and avg_tilt_Y > 0.4:
        instruction_Y =  "L4"
    elif avg_tilt_Y <= 0.6 and avg_tilt_Y > 0.5:
        instruction_Y =  "L5"
    elif avg_tilt_Y <= 0.7 and avg_tilt_Y > 0.6:
        instruction_Y =  "L6"
    elif avg_tilt_Y <= 0.8 and avg_tilt_Y > 0.7:
        instruction_Y =  "L7"
    elif avg_tilt_Y <= 0.9 and avg_tilt_Y > 0.8:
        instruction_Y =  "L8"
    elif avg_tilt_Y <= 1 and avg_tilt_Y > 0.9:
        instruction_Y =  "L9"
    elif avg_tilt_Y > 1:
        instruction_Y =  "L10"    
    elif avg_tilt_Y >= -0.1 and avg_tilt_Y < 0:
        instruction_Y =  "R0"
    elif avg_tilt_Y >= -0.2 and avg_tilt_Y < -0.1:
        instruction_Y =  "R1"
    elif avg_tilt_Y >= -0.3 and avg_tilt_Y < -0.2:
        instruction_Y =  "R2"
    elif avg_tilt_Y >= -0.4 and avg_tilt_Y < -0.3:
        instruction_Y =  "R3"
    elif avg_tilt_Y >= -0.5 and avg_tilt_Y < -0.4:
        instruction_Y =  "R4"
    elif avg_tilt_Y >= -0.6 and avg_tilt_Y < -0.5:
        instruction_Y =  "R5"
    elif avg_tilt_Y >= -0.7 and avg_tilt_Y < -0.6:
        instruction_Y =  "R6"
    elif avg_tilt_Y >= -0.8 and avg_tilt_Y < -0.7:
        instruction_Y =  "R7"
    elif avg_tilt_Y >= -0.9 and avg_tilt_Y < -0.8:
        instruction_Y =  "R8"
    elif avg_tilt_Y >= -1 and avg_tilt_Y < -0.9:
        instruction_Y =  "R9"
    elif avg_tilt_Y < -1:
        instruction_Y =  "R10"     
    else:
        instruction_Y =  "Y"
    
    #等级判断
    instruction_Z = "Z"
    if avg_tilt_Z <= 25 and avg_tilt_Z > 0:
        instruction_Z =  "A0"
    elif avg_tilt_Z <= 50 and avg_tilt_Z > 25:
        instruction_Z =  "A1"
    elif avg_tilt_Z <= 75 and avg_tilt_Z > 50:
        instruction_Z =  "A2"
    elif avg_tilt_Z <= 100 and avg_tilt_Z > 75:
        instruction_Z =  "A3"
    elif avg_tilt_Z <= 125 and avg_tilt_Z > 100:
        instruction_Z =  "A4"
    elif avg_tilt_Z <= 150 and avg_tilt_Z > 125:
        instruction_Z =  "A5"
    elif avg_tilt_Z <= 175 and avg_tilt_Z > 150:
        instruction_Z =  "A6"
    elif avg_tilt_Z <= 200 and avg_tilt_Z > 175:
        instruction_Z =  "A7"
    elif avg_tilt_Z <= 225 and avg_tilt_Z > 200:
        instruction_Z =  "A8"
    elif avg_tilt_Z <= 256 and avg_tilt_Z > 225:
        instruction_Z =  "A9"
    elif avg_tilt_Z >= -25 and avg_tilt_Z < 0:
        instruction_Z =  "C0"
    elif avg_tilt_Z >= -50 and avg_tilt_Z < -25:
        instruction_Z =  "C1"
    elif avg_tilt_Z >= -75 and avg_tilt_Z < -50:
        instruction_Z =  "C2"
    elif avg_tilt_Z >= -100 and avg_tilt_Z < -75:
        instruction_Z =  "C3"
    elif avg_tilt_Z >= -125 and avg_tilt_Z < -100:
        instruction_Z =  "C4"
    elif avg_tilt_Z >= -150 and avg_tilt_Z < -125:
        instruction_Z =  "C5"
    elif avg_tilt_Z >= -175 and avg_tilt_Z < -150:
        instruction_Z =  "C6"
    elif avg_tilt_Z >= -200 and avg_tilt_Z < -175:
        instruction_Z =  "C7"
    elif avg_tilt_Z >= -225 and avg_tilt_Z < -200:
        instruction_Z =  "C8"
    elif avg_tilt_Z >= -256 and avg_tilt_Z < -225:
        instruction_Z =  "C9" 
    else:
        instruction_Z =  "C"

    
    
    instructions = {"instruct_X": instruction_X, "instruct_Y": instruction_Y, "instruct_Z": instruction_Z}
    return instructions

def WIFI_Connect():
    """连接wifi并且打印信息
    """

    wlan = network.WLAN(network.STA_IF) #STA模式
    wlan.active(True)                   #激活接口
    start_time=time.time()              #记录时间做超时判断

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Uz', 'ufp0-0-1') #输入WIFI账号密码

        while not wlan.isconnected():
            #15S超时判断
            if time.time()-start_time > 15 :
                print('WIFI Connected Timeout!')
                break

    if wlan.isconnected():
        print('network information:', wlan.ifconfig())

def oled_display(ur_command, wifi_config):
    """ 分别打印三行信息：指令、wifi地址、spiderbot
    """

    first_line = "Command: " + ur_command['instruct_X'] + ur_command['instruct_Y'] + ur_command['instruct_Z']
    second_line = "Address: " + wifi_config[0]
    third_line = "SpiderBot"
    #在指定像素坐标分别写入三行后执行显示
    oled.text(first_line, 0,  0)      
    oled.text(second_line,  0, 20)      
    oled.text(third_line,  0, 40)     
    oled.show()


def webserver():
    """实现一个简单的webserver用来接受get请求，返回和oled的第一行同样显示内容
    """
    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # (重要)设置端口释放后立即就可以被再次使用
    s.bind(socket.getaddrinfo("0.0.0.0", 80)[0][-1])  # 绑定地址
    s.listen(5)  # 开启监听（最大连接数5）
    while True:
        client_sock, client_addr = s.accept()  # 接收来自客户端的请求与客户端地址

        while True:
            h = client_sock.readline()
            if h == b'' or h == b'\r\n':
                break
        ur_command = judge_instruct()
        client_sock.write(responseHeaders) # 向客户端发送响应头
        client_sock.write(ur_command['instruct_X'] + ur_command['instruct_Y'] + ur_command['instruct_Z']) # 向客户端发送网页内容
        client_sock.close()

def main():
    """让oled屏幕显示内容
    """
    while 1:
        print(judge_instruct())
        ur_command = judge_instruct()
        oled_display(ur_command, wifi_config)
        


WIFI_Connect()

wlan = network.WLAN(network.STA_IF)    
wifi_config = wlan.ifconfig()


#多线程
_thread.start_new_thread(main, ())
_thread.start_new_thread(webserver, ())


    #读入指令，调用显示函数，显示当前指令和wifi状态
    #ur_command = judge_instruct()
    #oled_display(ur_command, wifi_config)
    
    #测试打印
    #print(wifi_config)
    #print(judge_instruct())
    
    
#webserver()
#main()
    




