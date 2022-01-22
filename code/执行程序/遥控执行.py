import socket
import time

def connect():
    # HOST = 'localhost'
    HOST = 'xxx.xx.xx.xxx'  #公网IP
    PORT = 1178
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.connect((HOST, PORT))
    return sock
def test(status):
    status = int(status)
    if status == 0:
        print("停止")
    if status == 1:
        print("前进")
    if status == 2:
        print("前右")
    if status == 3:
        print("右转")
    if status == 4:
        print("右后")
    if status == 5:
        print("后退")
    if status == 6:
        print("左后")
    if status == 7:
        print("左转")
    if status == 8:
        print("前左")
     
while True:
    sock = connect()
    status = sock.recv(1).decode()
    test(status)
    sock.close()


