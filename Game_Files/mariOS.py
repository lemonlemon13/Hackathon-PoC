#
# This script handles the GUI for clients, which communicates with Server.py
#

import tkinter as tk
from enum import Enum
from Game_Files.Client import *
from Game_Files.CryptoTools import *

BOOT_TEXT = ["Loading Boot Sector", "Running Boot Program", "Starting Kernel", "Running Shell",
             "Locating Disk Image", "Mounting File System", "Initialising Network Connections", "Preparing Drivers",
             "Preparing I/O Drivers", "Preparing System", "BOOT COMPLETE"]

HELP_TEXT = ["ping [IP] | Pings the given IP to confirm it exists.\n",
             "reboot | Restart the virtual machine.\n",
             "ssh [IP] | Connects to the given IP. Further credentials may be required.\n",
             "exit | Leave a connected machine, powers off your machine, or closes the game.\n",
             "rm [name] | Deletes the given file name.\n",
             "cd [dir] | Change the working directory to the given path.\n",
             "ls | List all files in the given directory.\n",
             "cat [file] | Read the contents of the given file.\n",
             "nc [IP] [port] | Monitor traffic from the given IP address and port.\n",
             "hping3 [IP] --flood | Flood the target IP in a DoS Attack.\n",
             "decrypt [file] [--cipher_type] [key] | Decrypts the file using the known key.\n",
             "pwdck [IP] | Password cracker tool targeting the given IP.\n",
             "sqlinject [IP] | Collect any SQL Databases present from the target.\n",
             "dnslookup [Domain] | Get the IP address associated with the given Domain.\n",
             "scp [src] [dst] | Copy the source file to the destination path on the local machine.\n",
             "help | View this text."]

class runningApp(Enum):
    TERMINAL = 0
    MAIL = 1
    CHAT = 2

class mari():
    def __init__(self, master: tk.Tk, ip: str) -> None:
        self._root = master

        self._curproc = runningApp.TERMINAL
        self._powered = False
        self._logIn = 0
        self._firstIn = True

        self._ip = ip
        self._username = ""
        self._password = ""

        self._proxy_ip = ""
        self._proxy_username = ""
        self._proxy_password = ""

        self._cd = "root$"

        self._last_cmds = []
        self._lci = 999

        master.title("[HACKATHON]")
        master.maxsize(480, 360)
        master.minsize(480, 360)
        opsys = tk.Frame(master, width=480, height=360, bg="black")
        self.line = tk.Entry(opsys, bg="black", fg="white")
        self.indent = tk.Label(opsys, text="> ", bg="black", fg="white")
        self.text = tk.Label(opsys, bg="black", fg="white", anchor="sw", justify="left", width=480, text="Virtual Machine Powered Off\n")
        self.indent.pack(side="left", anchor="sw")
        self.line.pack(side="bottom", fill="x")
        self.line.focus_set()
        self.text.pack(side="top", fill="both", padx=0, anchor="w")

        master.bind('<Return>', self.handle_key)
        master.bind('<Up>', self.cycle_up)
        master.bind('<Down>', self.cycle_down)

        opsys.pack(fill="both", expand=True)

    def cycle_up(self, event):
        if self._lci == 999:
            self._lci = len(self._last_cmds) - 1
        elif self._lci == 0:
            pass
        else:
            self._lci = self._lci - 1
        self.line.delete(0, tk.END)
        self.line.insert(0, self._last_cmds[self._lci])

    def cycle_down(self, event):
        if self._lci >= len(self._last_cmds) - 1:
            self._lci = 999
            self.line.delete(0, tk.END)
        else:
            self._lci = (self._lci + 1) % len(self._last_cmds)
            self.line.delete(0, tk.END)
            self.line.insert(0, self._last_cmds[self._lci])

    def handle_key(self, event):
        command = self.line.get()
        self.line.delete(0, tk.END)
        commandList = command.split(" ")

        if len(self._last_cmds) == 10:
            self._last_cmds.pop(0)
        self._last_cmds.append(command)
        self._lci = 999

        output = ""
        newstr = ""

        if not self._powered:
            # Turn on the VM
            match (commandList[0]):
                case "reboot":
                    self.text.config(text="", anchor="w")
                    self.play_boot_anim()
                    self._powered = True
                case "exit":
                    self._root.destroy()
                case _:
                    self.text.config(text=self.cutText(self.text['text'] +
                        f"Error: command \'{command}\' not found.\n" +
                        "Please use \'reboot\' to start the virtual machine.\n"), anchor="w")
        elif self._logIn == 0:
            # Enter Username
            if len(command) > 16 or len(command) == 0 or command.find(":") != -1:
                output = "Invalid Username"
            elif self._firstIn:
                # Setting Username
                output = "Enter Password:"
                self._username = command
                self._logIn += 1
            elif command == self._username:
                # Correct Username
                output = "Enter Password:"
                self._logIn += 1
            else:
                # Wrong Username
                output = "Incorrect Username"
            newstr = self.text['text'] + "> " + command + "\n" + output + ("" if output == "" else "\n")
            newstr = self.cutText(newstr)
            self.text.config(text=newstr, anchor="w")
        elif self._logIn == 1:
            # Enter Password
            if len(command) > 16 or len(command) == 0 or command.find(":") != -1:
                output = "Invalid Password"
            elif self._firstIn:
                # Setting Password
                output = f"Welcome, {self._username}."
                self._password = command
                self._logIn += 1
                self._firstIn = False
            elif command == self._password:
                # Correct Password
                output = f"Welcome, {self._username}."
                self._logIn += 1
            else:
                # Wrong Password
                output = "Incorrect Password"
            newstr = self.text['text'] + "> " + command + "\n" + output + ("" if output == "" else "\n")
            newstr = self.cutText(newstr)
            self.text.config(text=newstr, anchor="w")
        else:
            if self._curproc == runningApp.TERMINAL:
                match (commandList[0]):
                    case "reboot":
                        self._powered = False
                        self.text.config(text="", anchor="w")
                        self.play_boot_anim()
                        self._powered = True
                    case "help":
                        for x in HELP_TEXT:
                            output += x
                    case "exit":
                        self._powered = False
                        self.text.config(text="Virtual Machine Powered Off\n", anchor="w")
            elif self._curproc == runningApp.CHAT:
                pass
            elif self._curproc == runningApp.MAIL:
                pass
            else:
                output = "Something has gone VERY wrong.\n"
            # Update the terminal output
            newstr = self.text['text'] + self._ip + "/" + self._cd + " > " + command + "\n" + output + ("" if output == "" else "\n")
            newstr = self.cutText(newstr)
            self.text.config(text=newstr, anchor="w")

    def play_boot_anim(self) -> None:
        self._logIn = 0
        s = ""
        timer = 0
        for i in range(0, 101):
            s = self.cutText(s + (BOOT_TEXT[i //10] + "\n" if i % 10 == 0 else "") +
                             f"{i}% [" + ("|" * (i // 10)) + (" " * (10 - (i // 10))) + "]\n")
            if (i % 10 == 0):
                self._root.after(timer, self.setText, s)
                timer += 125
            else:
                self._root.after(timer, self.setText, s)
                timer += 50
        self._root.after(7500, self.setText, "Virtual Machine Powered On\n")
        if self._firstIn:
            self._root.after(8500, self.setText, "First Log In Detected\n" +
            "Account Set-Up Required\n" +
            "Enter Username:\n")
        else:
            self._root.after(8500, self.setText, f"Current IP Address: {self._ip}\n" +
            "Enter Username:\n")
    
    def setText(self, s) -> None:
        self.text.config(text=s, anchor="w")

    def cutText(self, s:str) -> str:
        linecount= 0
        index = len(s) - 1
        for c in s[-1::-1]:
            if c == "\n":
                linecount += 1
                if linecount > 22:
                    return s[index:]
            index -= 1
        return s

def bootOS(ip: str):
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    mari(root, ip)
    root.mainloop()