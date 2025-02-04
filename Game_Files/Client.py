#
# This script handles the networking for the clients sending requests to the server.
#

import socket
import time
import os
from _thread import *
from Game_Files.CryptoTools import *
from Game_Files.mariOS import *
from Game_Files.NetworkArch import *

def sendmsg(skt: socket.socket, name:str):
    while True:
        try:
            userIn = input()
            if (userIn == "--quit"):
                skt.close()
                break
            now = time.strftime("%d %b %Y %I:%M %p")
            cmd = f"({now}) {name}: {userIn}"
            msg = GameMsg()
            msg.prepare(name, msgType.PREGAME, cmd)
            if len(msg.send()) > 2048:
                print("Failed to Send. Message Too Long.")
                continue
            if userIn != "":
                skt.send(bytes(msg.send().encode("utf-8")))
        except ConnectionError as e:
            print("Connect Lost with Server.")
            exit

def new_client(code: str = None):
    # Get the user's name
    if code is None:
        name = input("Input Username (Max 16 Characters): ")
        while len(name) > 16 or len(name) == 0 or name.find(":") != -1 or name.find("|") != -1 or name == "SERVER":
            print("INVALID USERNAME")
            name = input("Input Username (Max 16 Characters): ")
        (ip, port) = LobbyCode().CodeToAddr(input("Enter Lobby Code(e.g. ABCD-EFGH): "))
    else:
        name = input("Input Username (Max 16 Characters): ")
        while len(name) > 16 or len(name) == 0 or name.find(":") != -1 or name.find("|") != -1 or name == "SERVER":
            print("INVALID USERNAME")
            name = input("Input Username (Max 16 Characters): ")
        (ip, port) = LobbyCode().CodeToAddr(code)

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect((ip, port))

    gameStarted = False
    quit_game = False
    ip = ""

    while not gameStarted:
        message = GameMsg()
        # Send the user's name to the server
        try:
            message.prepare(name, msgType.NEW, name)
            skt.send(bytes(message.send().encode("utf-8")))
            d = str(skt.recv(16*1024),encoding="utf-8")
            data = GameMsg()
            data.recv(d)
            name_IP = data.getcmd().split("|")
            name = name_IP[0]
            ip = name_IP[1]
        except OSError as e:
            print("Failed to connect to Server.")
            quit_game = True
            break

        print("Type \"--quit\" to leave the room.")
        print("Type \"--start\" to start the game if you're the host.")
        try:
            start_new_thread(sendmsg, (skt,name,))
            while not gameStarted:
                d = str(skt.recv(16*1024),encoding="utf-8")
                data = GameMsg()
                data.recv(d)
                if data.send() == GAMESTART.send():
                    gameStarted = True
                    break
                os.system('cls')
                print(data.getcmd())
        except OSError as e:
            print("Connect Lost with Server.")
            exit

    # Create a window for mariOS's GUI
    if not quit_game:
        bootOS(ip)

if __name__ == "__main__":
    new_client()