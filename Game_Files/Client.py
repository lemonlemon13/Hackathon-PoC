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
            msg.prepare(name, msgType.REQUEST, cmd)
            if len(msg.send()) > 2048:
                print("Failed to Send. Message Too Long.")
                continue
            if userIn != "":
                skt.send(bytes(msg.send().encode("utf-8")))
        except ConnectionError as e:
            print("Connect Lost with Server.")
            exit

def new_client(code: str = None):
    if code is None:
        name = input("Input Username (Max 16 Characters): ")
        while len(name) > 16 or len(name) == 0 or name.find(":") != 1 or name == "SERVER":
            print("INVALID USERNAME")
            name = input("Input Username (Max 16 Characters): ")
        (ip, port) = LobbyCode().CodeToAddr(input("Enter Lobby Code(e.g. ABCD-EFGH): "))
    else:
        name = input("Input Username (Max 16 Characters): ")
        while len(name) > 16 or len(name) == 0 or name.find(":") != 1 or name == "SERVER":
            print("INVALID USERNAME")
            name = input("Input Username (Max 16 Characters): ")
        (ip, port) = LobbyCode().CodeToAddr(code)

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect((ip, port))

    gameStarted = False
    message = GameMsg()

    while not gameStarted:
        try:
            skt.send(bytes(name.encode("utf-8")))
        except ConnectionError as e:
            print("Failed to connect to Server.")
            exit

        print("Type \"--quit\" to leave the room.")
        try:
            start_new_thread(sendmsg, (skt,name,))
            while not gameStarted:
                data = str(skt.recv(16*1024),encoding="utf-8")
                if data == "":
                    gameStarted = True
                    break
                os.system('cls')
                print(data)
        except ConnectionError as e:
            print("Connect Lost with Server.")

    # Create a window for mariOS's GUI
    bootOS()

if __name__ == "__main__":
    new_client()