import socket
import time
import numpy as np
import cv2
import threading


# 1155
def socket_portA():
    def receive_data():
        buf = (connection.recv(5).decode())

        pic = (connection.recv(int(buf)))
        if (len(pic) == int(buf)):
            connection.send(str("correct").encode())
            print(connection.recv(20480).decode())
            return pic
        else:
            print("now:", len(pic))
            while (True):
                if (len(pic) == int(buf)):
                    break
                pic1 = (connection.recv(204800))
                pic = pic + pic1
                print(len(pic1))
                if (len(pic1) == 0):
                    break
            print(connection.recv(1024).decode())
            return pic

    def pic_decode(data):
        data = np.frombuffer(data, np.uint8)  # 将获取到的字符流数据转换成1维数组
        decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
        cv2.imwrite("test.jpg", decimg)

    HOST = 'xxx.xx.xx.xx'  # 服务器的私网IP
    PORT = 1155
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    num = 0
    while True:
        connection, address = sock.accept()
        connection.settimeout(5)  # 5s
        try:

            code = None
            code = connection.recv(1024)

            if code == b'ts':
                localtime = time.asctime(time.localtime(time.time()))
                text1 = "this is from balmung's server: "
                num = str(num)
                connection.send(text1.encode() + num.encode())

            if code == b'up':
                data = receive_data()
                pic_decode(data)
                connection.send("success".encode())
                num = num + 1

            # 重点
            if code == b'dl':
                try:
                    '''
                    localtime = time.asctime(time.localtime(time.time()))
                    text1 = "this is from balmung's server: "
                    connection.send(text1.encode() + localtime.encode())
                    '''
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]
                    img = cv2.imread("test.jpg")
                    result, imgencode = cv2.imencode('.jpg', img, encode_param)
                    data = np.array(imgencode)
                    stringData = data.tobytes()
                    buf = str(len(stringData))
                    leng = str(len(buf))
                    connection.send(leng.encode())
                    connection.send(buf.encode())
                    connection.sendall(stringData)
                    '''
                    status = connection.recv(1024).decode()
                    if status == "correct":
                        connection.send("finish".encode())

                    if status == "return":
                        connection.send("break".encode())
                    '''
                except Exception as e:
                    connection.send("x".encode())



            else:
                connection.send("get".encode)
        except Exception as e:
            pass


# 1154 服务程序完全同上
def socket_portB():
    def receive_data():
        buf = (connection.recv(5).decode())

        pic = (connection.recv(int(buf)))
        if (len(pic) == int(buf)):
            connection.send(str("correct").encode())
            print(connection.recv(20480).decode())
            return pic
        else:
            print("now:", len(pic))
            while (True):
                if (len(pic) == int(buf)):
                    break
                pic1 = (connection.recv(204800))
                pic = pic + pic1
                print(len(pic1))
                if (len(pic1) == 0):
                    break
            print(connection.recv(1024).decode())
            return pic

    def pic_decode(data):
        data = np.frombuffer(data, np.uint8)  # 将获取到的字符流数据转换成1维数组
        decimg = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 将数组解码成图像
        cv2.imwrite("test.jpg", decimg)

    HOST = 'xxx.xx.xx.xx'  # 服务器的私网IP
    PORT = 1154
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    num = 0
    while True:
        connection, address = sock.accept()
        connection.settimeout(5)  # 5s
        try:

            code = None
            code = connection.recv(1024)

            if code == b'ts':
                localtime = time.asctime(time.localtime(time.time()))
                text1 = "this is from balmung's server: "
                num = str(num)
                connection.send(text1.encode() + num.encode())

            if code == b'up':
                data = receive_data()
                pic_decode(data)
                connection.send("success".encode())
                num = num + 1

            if code == b'dl':
                '''
                localtime = time.asctime(time.localtime(time.time()))
                text1 = "this is from balmung's server: "
                connection.send(text1.encode() + localtime.encode())
                '''
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]
                img = cv2.imread("test.jpg")
                result, imgencode = cv2.imencode('.jpg', img, encode_param)
                data = np.array(imgencode)
                stringData = data.tobytes()
                buf = str(len(stringData))
                connection.send(buf.encode())
                connection.sendall(stringData)
                '''
                status = connection.recv(1024).decode()
                if status == "correct":
                    connection.send("finish".encode())

                if status == "return":
                    connection.send("break".encode())
                '''
            else:
                connection.send("get".encode)
        except Exception as e:
            pass


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


threads = []

# 创建新线程
thread1 = myThread(1, "Thread-1", socket_portA)
thread2 = myThread(2, "Thread-2", socket_portB)

# 开启新线程
thread1.start()
thread2.start()

threads.append(thread1)
threads.append(thread2)




