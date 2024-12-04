#
# This script handles neutral information and data regarding both clients and servers.
#

from enum import Enum

class msgType(Enum):
    REQUEST = 0 # From client to server
    RESPONSE = 1 # From server to individual client
    PREGAME = 2 # For clients in pregame chatting
    ALERT = 3 # From server to all clients
    NEW = 4 # For new clients

class GameMsg():
    def __init__(self) -> None:
        pass
    
    def prepare(self, src:str, type:msgType, cmd:str) -> None:
        self._src = src
        self._type = type
        self._cmd = cmd
    
    def send(self) -> str:
        # Convert message object into a string to be sent to the socket
        msg = f"{self._src}:{self._type}:{self._cmd}"
        return msg
    
    def recv(self, msg:str) -> None:
        # Take a sent message and convert it back into the object
        elements = msg.split(":", 2)
        self._src = elements[0]
        self._type = elements[1]
        self._cmd = elements[2]
    
    def getsrc(self) -> str:
        return self._src
    
    def gettype(self) -> msgType:
        return self._type
    
    def getcmd(self) -> str:
        return self._cmd
    
    def __str__(self) -> str:
        return self.send()

GAMESTART = GameMsg()
GAMESTART.prepare("SERVER", msgType.ALERT, "start") # Message to say game is starting

GAMEEND = GameMsg()
GAMEEND.prepare("SERVER", msgType.ALERT, "end") # Message to say game has ended

GAMECLOSE = GameMsg()
GAMECLOSE.prepare("SERVER", msgType.ALERT, "close") # Message to say lobby is closing