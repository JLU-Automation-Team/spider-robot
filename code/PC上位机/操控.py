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
def send_code(code):
    def connect():
        # HOST = 'localhost'
        HOST = 'xxx.xxx.xxx.xxx'  # 服务器的公网IP
        PORT = 1177
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((HOST, PORT))
        return sock

    def update(data):
        sock.send("up".encode())
        sock.send(str(data).encode())
        print(sock.recv(100))
    sock = connect()
    update(code)


def ui():
    #ui基本文字
    interaction = tkinter.Tk()
    interaction.title("远程操控")
    interaction.geometry("450x350")
    interaction.resizable(False, False)
    notebook = tkinter.ttk.Notebook(interaction,width=430,height=320)
    frameOne = tkinter.Frame()
    global frameTwo
    frameTwo = tkinter.Frame()
    frameThree = tkinter.Frame()
    notebook.add(frameOne, text='主菜单')
    notebook.place(x=0,y=0)
    botton1 = tkinter.Button(frameOne, text="↑",height=1,width=3,command=lambda:send_code(1)).place(x=200,y=50)
    botton2 = tkinter.Button(frameOne, text="↓",height=1,width=3,command=lambda:send_code(5)).place(x=200,y=150)
    botton3 = tkinter.Button(frameOne, text="←",height=1,width=3,command=lambda:send_code(7)).place(x=150,y=100)
    botton4 = tkinter.Button(frameOne, text="→",height=1,width=3,command=lambda:send_code(3)).place(x=250,y=100)
    botton5 = tkinter.Button(frameOne, text="🛑",height=1,width=3,command=lambda:send_code(0)).place(x=200,y=100)
    botton6 = tkinter.Button(frameOne, text="↖",height=1,width=3,command=lambda:send_code(8)).place(x=150,y=50)
    botton7 = tkinter.Button(frameOne, text="↗",height=1,width=3,command=lambda:send_code(2)).place(x=250,y=50)
    botton8 = tkinter.Button(frameOne, text="↙",height=1,width=3,command=lambda:send_code(6)).place(x=150,y=150)
    botton9 = tkinter.Button(frameOne, text="↘",height=1,width=3,command=lambda:send_code(4)).place(x=250,y=150)
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

def stop():
    global status
    status = "stop"
if __name__ == '__main__':
    t1_go()

