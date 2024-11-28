import socket
from _thread import *
from CryptoTools import *
import time

def manage_server(skt: socket.socket):
    skt.listen(16)
    while True:
        c, addr1 = skt.accept()
        try:
            name = str(c.recv(16), encoding="utf-8")
            file = open("chatLog", "a")
            file.write(f"{name} joined the Room.\n")
            file.close()
        except ConnectionError as e:
            file = open("chatLog", "a")
            file.write(f"{name} left the Room.\n")
            file.close()
        start_new_thread(manage_chat, (c,name,))
    skt.close()

def manage_chat(c: socket.socket, user: str):
    last_line = ""
    old_count = 0
    c.setblocking(False)
    while True:
        try:
            data = c.recv(2048)
            msg = str(data,encoding="utf-8") + "\n"
            file = open("chatLog", "a")
            file.write(msg)
            file.close()
        except ConnectionError as e:
            file = open("chatLog", "a")
            file.write(f"{user} left the Room.\n")
            file.close()
            break
        except BlockingIOError as e:
            file = open("chatLog", "r")
            line = ""
            count = 0
            for l in file:
                line = l
                count += 1
            if last_line != line or old_count != count:
                last_line = line
                old_count = count
                fbin = open("chatLog", "b+r")
                c.setblocking(True)
                c.sendfile(fbin)
                c.setblocking(False)
                fbin.close()
            file.close()
            time.sleep(0.1)

def host_server() -> str:
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = socket.gethostbyname(socket.gethostname())
    skt.bind((host_ip, 0))
    roomCode = LobbyCode().AddrToCode(skt.getsockname()[0], skt.getsockname()[1])
    
    file = open("chatLog", "a")
    file.write(f"Lobby Code: {roomCode}\n")
    file.close()

    start_new_thread(manage_server, (skt,))

    return roomCode

if __name__ == "__main__":
    host_server()