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

class runningApp(Enum):
    TERMINAL = 0
    MAIL = 1
    CHAT = 2

class mari():
    def __init__(self, master: tk.Tk) -> None:
        self._root = master
        self._curproc = runningApp.TERMINAL
        self._powered = False
        master.title("[HACKATHON]")
        master.maxsize(480, 360)
        master.minsize(480, 360)
        opsys = tk.Frame(master, width=480, height=360, bg="black")
        self.line = tk.Entry(opsys, bg="black", fg="white")
        self.indent = tk.Label(opsys, text="> ", bg="black", fg="white")
        self.text = tk.Label(opsys, bg="black", fg="white", anchor="sw", justify="left", width=480, text="Virtual Machine Powered Off\n")
        self.indent.pack(side="left", anchor="sw")
        self.line.pack(side="bottom", fill="x")
        self.text.pack(side="top", fill="both", padx=0, anchor="w")

        master.bind('<Return>', self.handle_key)

        opsys.pack(fill="both", expand=True)

    def handle_key(self, event):
        command = self.line.get()
        commandList = self.line.get().split(" ")
        self.line.delete(0, 'end')

        output = ""
        newstr = ""

        if not self._powered:
            match (commandList[0]):
                case "reboot":
                    self.text.config(text="", anchor="w")
                    self.play_boot_anim()
                    self._powered = True
        else:
            match (commandList[0]):
                case "reboot":
                    self.text.config(text="", anchor="w")
                    self.play_boot_anim()
                    self._powered = True
            # Update the terminal output
            newstr = self.text['text'] + "> " + command + "\n" + output + ("" if output == "" else "\n")
            newstr = self.cutText(newstr)
            self.text.config(text=newstr, anchor="w")

    def play_boot_anim(self) -> None:
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

def bootOS():
    root = tk.Tk()
    mari(root)
    root.mainloop()