#
# This script handles the GUI for clients, which communicates with Server.py
#

import tkinter as tk
from enum import Enum
from Game_Files.Client import *

class runningApp(Enum):
    TERMINAL = 0
    MAIL = 1
    CHAT = 2

class mari():
    def __init__(self, master: tk.Tk) -> None:
        self._root = master
        self._curproc = runningApp.TERMINAL
        master.title("[HACKATHON]")
        master.maxsize(480, 360)
        master.minsize(480, 360)
        os = tk.Frame(master, width=480, height=360, bg="black")

        self.line = tk.Entry(os, bg="black", fg="white")
        self.indent = tk.Label(os, text="> ", bg="black", fg="white")
        self.text = tk.Label(os, bg="black", fg="white", anchor="sw", justify="left", width=480)
        self.indent.pack(side="left", anchor="sw")
        self.line.pack(side="bottom", fill="x")
        self.text.pack(side="top", fill="both", padx=0, anchor="w")

        master.bind('<Return>', self.handle_key)

        os.pack(fill="both", expand=True)

    def handle_key(self, event):
        newstr = self.text['text'] + self.line.get() + "\n"
        linecount= 0
        index = len(newstr) - 1
        for c in newstr[-1::-1]:
            if c == "\n":
                linecount += 1
                if linecount > 22:
                    newstr = newstr[index:]
            index -= 1

        self.text.config(text=newstr, anchor="w")
        self.line.delete(0, 'end')

def bootOS():
    root = tk.Tk()
    mari(root)
    root.mainloop()