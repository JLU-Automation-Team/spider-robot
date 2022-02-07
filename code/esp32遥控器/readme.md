# 基于esp32的体感手势遥控器
## 程序基本思路
### mpu6050数据处理
 * 从水平静置调零后的传感器获取三轴线加速度数据和三轴角加速度数据
 * 利用三轴线加速度数据和当地重力加速度计算出左右前后相对水平面的倾角
 * 利用z轴角速度计得到水平旋转角速度
 * 根据传感器数值分级输出移动指令和转向指令
 

### oled屏幕显示
 * 前两行内容分别是指令信息、局域网ip地址

### webserver的简单实现
 * 定义好响应头之后进入死循环开始监听，响应来自客户端的GET请求
 * 返回内容是一个与oled屏幕第一行内容相同的字符串

## 食用方法
 * 接好供电，连好引脚（mpu和oled都是3v3供电；mpu的接gpio5, sda接gpio4；oled的sda接gpio13, scl接gpio14）
 * 晃动遥控器
 * 树莓派的运控程序向esp32的ip地址(80端口)发送GET请求，得到遥控器产生的指令(同时指令会在oled上显示)


## 可能存在的问题
 * oled与mpu6050直接并联在esp32的3v3和gnd管脚之间可能导致mpu6050烧毁

## 参考来源：

>mpu6050的驱动来源: https://github.com/macalencar/micropython-mpu6050/blob/main/mpu6050.py

>ssd1306 oled屏幕的驱动来源: https://github.com/adafruit/micropython-adafruit-ssd1306/blob/master/ssd1306.py

