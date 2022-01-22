import tkinter
import tkinter.messagebox
import cv2
import socket
import numpy as np
import time
import threading
from tkinter import ttk, scrolledtext,filedialog
from PIL import Image,ImageTk

#服务函数
def send_pic():

    def connect():
        # HOST = 'localhost'
        HOST = 'xxx.xxx.xxx.xxx'  # 服务器的公网IP
        PORT = 1154
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((HOST, PORT))
        return sock

    def updata(a):
        localtime = time.asctime(time.localtime(time.time()))
        print("send time: " + localtime)
        sock.send(str(a).encode())
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
    global cemera
    video = cv2.VideoCapture(cemera)
    i = 0
    global frameTwo,panel,status
    status = "go"
    while True:
        try:
            i += 1
            sock = connect()
            updata('up')
            sta, img = video.read()
            # img = cv2.COLOR_RGB2GRAY(img)
            # img = cv2.resize(img, (320,240))
            cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)#转换颜色从BGR到RGBA
            current_image = Image.fromarray(cv2image)#将图像转换成Image对象
            imgtk = ImageTk.PhotoImage(image=current_image)
            panel.config(image=imgtk)
            panel.imgtk = imgtk

            result, imgencode = cv2.imencode('.jpg', img, encode_param)
            data = np.array(imgencode)
            stringData = data.tobytes()
            buf = str(len(stringData))

            sock.send(buf.encode())
            sock.sendall(stringData)
            sock.close()
            if status == "stop":
                break
            print(i)
        except cv2.error as e:
            print(e)
            tkinter.messagebox.askokcancel(title = '警告',message='摄像头编号错误')
            break
        except Exception as e:
            print(e)
            continue

def receive_pic():
    def updata(a):
        localtime = time.asctime(time.localtime(time.time()))
        print("send time: " + localtime)
        sock.send(str(a).encode())

    def receivedata():
        while True:
            # print(sock.recv(1024).decode())
            leng = (sock.recv(1))

            leng = int(leng.decode())
            print("-" * 30)
            buf = (sock.recv(leng))
            print("-" * 30, buf)
            buf = buf.decode()
            if (len(buf) == leng):
                pic = (sock.recv(int(buf)))
                print("-" * 30)
                if (len(pic) == int(buf)):
                    # ock.send(str("correct").encode())
                    # print(sock.recv(1024).decode())
                    return pic
                else:
                    print("now:", len(pic))
                    while (True):
                        if (len(pic) == int(buf)):
                            break

                        pic1 = (sock.recv(204800))
                        pic = pic + pic1
                        # print(len(pic1))
                        if (len(pic1) == 0):
                            break
                    # sock.send(str("return").encode())
                    # print(sock.recv(1024))
                    return pic
            else:
                print("error")
                return 0

    def pic_decode(data):
        data = np.frombuffer(data, np.uint8)  # 将获取到的字符流数据转换成1维数组
        decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
        cv2.imwrite("test.jpg", decimg)

    def connect():
        # HOST = 'localhost'
        HOST = 'xxx.xxx.xxx.xxx'  # 服务器的公网IP
        PORT = 1155
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((HOST, PORT))
        return sock
    i = 0
    global panel2,status
    status = "go"
    while True:
        try:
            i += 1
            sock = connect()
            updata('dl')

            # updata(i)
            # print(sock.recv(1024).decode())
            # print(i)

            data = receivedata()
            if data != 0:
                pic_decode(data)
            else:
                pass
            sock.close()
            img = cv2.imread("test.jpg")
            cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)#转换颜色从BGR到RGBA
            current_image = Image.fromarray(cv2image)#将图像转换成Image对象
            imgtk = ImageTk.PhotoImage(image=current_image)
            panel2.config(image=imgtk)
            panel2.imgtk = imgtk
            if status == "stop":
                break

        except Exception as e:
            print(e)
            continue
def ui():
    global botton1,botton2
    #ui基本文字
    interaction = tkinter.Tk()
    interaction.title("socket通信监控")
    interaction.geometry("450x350")
    interaction.resizable(False, False)
    notebook = tkinter.ttk.Notebook(interaction,width=430,height=320)
    frameOne = tkinter.Frame()
    global frameTwo
    frameTwo = tkinter.Frame()
    frameThree = tkinter.Frame()
    notebook.add(frameOne, text='主菜单')
    notebook.add(frameTwo, text='发送窗口')
    notebook.add(frameThree, text='接收窗口')
    notebook.place(x=0,y=0)
    text1 = tkinter.Label(frameOne, text="         socket远程通信演示程序",font=20).place(x=10,y=25)
    tkinter.Label(frameOne,text="上传图像：",font=20).place(x=50,y=100)
    tkinter.Label(frameOne,text="接收图像：",font=20).place(x=50,y=150)
    tkinter.Label(frameOne,text="发送摄像头编号选择：",font=20).place(x=50,y=200)
    #按钮触发函数
    botton1 = tkinter.Button(frameOne, text="开始上传",command=t3_go).place(x=270,y=100)
    botton2 = tkinter.Button(frameOne, text="开始接收",command=t2_go).place(x=270,y=150)
    botton3 = tkinter.Button(frameOne, text="停止收发",command=stop).place(x=190,y=260)
    values1 = ['0','1','2','3','4','5']
    combobox1 = ttk.Combobox(
        master=frameOne,  # 父容器
        height=3,  # 高度,下拉显示的条目数量
        width=14,  # 宽度
        state='readonly',  # 设置状态 normal(可选可输入)、readonly(只可选)、 disabled
        cursor='arrow',  # 鼠标移动时样式 arrow, circle, cross, plus...
        font=('', 12),  # 字体
        values=values1,  # 设置下拉框的选项
            )
    def choose1(event):
        global cemera
        cemera = int(combobox1.get())
    combobox1.bind('<<ComboboxSelected>>', choose1)
    combobox1.place(x=270,y=205)
    global panel,panel2
    panel = tkinter.Label(frameTwo)  # initialize image panel
    panel.pack(padx=10, pady=10)
    panel2 = tkinter.Label(frameThree)  # initialize image panel
    panel2.pack(padx=10, pady=10)
    #帮助菜单栏
    def ar():
        tkinter.messagebox.showinfo('关于作者', '本程序来自balmung\n数据中转自私人服务器')
    def he():
        tkinter.messagebox.showinfo('帮助', '上传本地摄像头捕获的图像并供下载端下载')
    menubar = tkinter.Menu(interaction)
    helpmenu = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='帮助', menu=helpmenu)
    helpmenu.add_command(label='关于',command=lambda: ar())
    helpmenu.add_command(label='说明',command=lambda: he())
    interaction.config(menu = menubar)

    #开始主循环
    interaction.mainloop()

class myThread(threading.Thread):
    def __init__(self, threadID, name, function):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.function = function
        # self.lock = threading.RLock()

    def run(self):
        # self.lock.acquire()
        self.function()
        # self.lock.acquire()


def t1_go():
    thread1 = myThread(1, "Thread-1", ui)
    thread1.start()
def t2_go():
    global status
    status = "stop"
    thread2 = myThread(2, "Thread-2", receive_pic)
    thread2.daemon = True
    global botton2
    thread2.start()
def t3_go():
    global status
    status = "stop"
    thread3 = myThread(3, "Thread-3", send_pic)
    thread3.daemon = True
    thread3.start()
def stop():
    global status
    status = "stop"
if __name__ == '__main__':
    t1_go()
