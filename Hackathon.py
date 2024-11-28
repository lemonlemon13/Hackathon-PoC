import Client
import Server
from _thread import *

def server():
    #Create a server
    code = Server.host_server()

    # When the server is ready, create a client to auto-join it.
    client(code)

def client(code: str = None):
    if code is None:
        Client.new_client()
    else:
        Client.new_client(code)

def boot():
    while True:
        userIn = input("> ")
        if userIn == "host":
            print("Starting New Lobby")
            server()
            break
        elif userIn == "join":
            print("Preparing to Join Lobby")
            client()
            break
        elif userIn == "quit":
            print("Closing the Game")
            break
        elif userIn == "help":
            print("Commands:")
            print("host: Host a Lobby")
            print("join: Join a Lobby")
            print("quit: Close the Game")
            print("help: See this information")
        else:
            print("Use 'help' to see commands")

if __name__ == "__main__":
    boot()