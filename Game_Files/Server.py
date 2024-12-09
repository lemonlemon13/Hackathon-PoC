#
# This script handles the networking for handling requests from clients and sending responses to them.
#

import socket
from _thread import *
from Game_Files.CryptoTools import *
from Game_Files.Server_Manager import *
import time
from Game_Files.NetworkArch import *

def manage_server(skt: socket.socket, mngr: ServerManager):
    skt.listen(16)
    while True:
        c, addr1 = skt.accept()
        try:
            m = GameMsg()
            m.recv(str(c.recv(64), encoding="utf-8"))
            name = m.getcmd()
            file = open("Game_Files/preGameLog", "a")
            file.write(f"{name} joined the Room.\n")
            file.close()
            mngr.add_player(name)
        except ConnectionError as e:
            file = open("Game_Files/preGameLog", "a")
            file.write(f"{name} left the Room.\n")
            file.close()
        start_new_thread(manage_chat, (c,name,mngr,))
    skt.close()

def manage_chat(c: socket.socket, user: str, mngr: ServerManager):
    last_line = ""
    old_count = 0
    c.setblocking(False)
    while True:
        rememberStarted = False
        try:
            data = c.recv(2048)
            msg = str(data,encoding="utf-8") + "\n"
            msgin = GameMsg()
            msgin.recv(msg)
            if msgin.getsrc() == mngr.get_host() and msgin.getcmd()[-8:-1] == "--start":
                mngr.start_game()
            file = open("Game_Files/preGameLog", "a")
            file.write(msgin.getcmd())
            file.close()
        except ConnectionError as e:
            file = open("Game_Files/preGameLog", "a")
            file.write(f"{user} left the Room.\n")
            file.close()
            break
        except BlockingIOError as e:
            if not mngr._started:
                file = open("Game_Files/preGameLog", "r")
                line = ""
                count = 0
                for l in file:
                    line = l
                    count += 1
                if last_line != line or old_count != count:
                    last_line = line
                    old_count = count
                    fbin = open("Game_Files/preGameLog", "b+r")
                    c.setblocking(True)
                    m = GameMsg()
                    m.prepare("SERVER", msgType.ALERT, fbin.read().decode("utf-8"))
                    c.send(bytes(m.send().encode("utf-8")))
                    c.setblocking(False)
                    fbin.close()
            elif not rememberStarted:
                rememberStarted = True
                c.setblocking(True)
                c.send(bytes(GAMESTART.send().encode("utf-8")))
                c.setblocking(False)
            file.close()
            time.sleep(0.1)

def host_server() -> str:
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = socket.gethostbyname(socket.gethostname())
    skt.bind((host_ip, 0))
    roomCode = LobbyCode().AddrToCode(skt.getsockname()[0], skt.getsockname()[1])
    manager = ServerManager(roomCode)
    
    file = open("Game_Files/preGameLog", "w")
    print(f"Lobby Code: {roomCode}")
    file.write(f"Lobby Code: {roomCode}\n")
    file.close()

    start_new_thread(manage_server, (skt,manager,))

    return roomCode

if __name__ == "__main__":
    host_server()