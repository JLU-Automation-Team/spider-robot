import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12,GPIO.OUT)#设置12号引脚为输出模式
p=GPIO.PWM(12,50)#将12号引脚初始化为PWM实例，频率为50Hz
p.start(0)#开始脉宽调制，参数范围为：（0.0《=dc《=100.0）

try:
    while True:
        for dc in range(0,13,1):
            p.ChangeDutyCycle(dc)#修改占空比参数范围为：（0.0《=dc《=100.0）
            time.sleep(1)

except KeyboardInterrupt:
    pass
    p.stop()#停止输出PWM波
    GPIO.cleanup()

