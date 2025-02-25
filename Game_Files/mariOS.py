#
# This script handles the GUI for clients, which communicates with Server.py
#

from __future__ import annotations
import os

import tkinter as tk
from enum import Enum
from Game_Files.Client import *
from Game_Files.CryptoTools import *

BOOT_TEXT = ["Loading Boot Sector", "Running Boot Program", "Starting Kernel", "Running Shell",
             "Locating Disk Image", "Mounting File System", "Initialising Network Connections", "Preparing Drivers",
             "Preparing I/O Drivers", "Preparing System", "BOOT COMPLETE"]

TERMINAL_HELP_TEXT = ["ping [IP] | Pings the given IP to confirm it exists.\n",
             "reboot | Restart the virtual machine.\n",
             "ssh [IP] | Connects to the given IP. Further credentials may be required.\n",
             "exit | Leave a connected machine, powers off your machine, or closes the game.\n",
             "rm [name] | Deletes the given file name.\n",
             "cd [dir] | Change the working directory to the given path.\n",
             "ls | List all files in the current directory.\n",
             "mkdir [name] | Makes a new sub-directory in the current directory.\n"
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
    GAME_CLOCK = 3
    PWDRST = 4

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

        self._fs = FileSystem(ip)
        self._proxy_fs = None # Of Type FileSystem

        self._last_cmds = [""]
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
            newstr = self.text['text'] + "> " + (len(command) * "*") + "\n" + output + ("" if output == "" else "\n")
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
                        for x in TERMINAL_HELP_TEXT:
                            output += x
                    case "cd":
                        if len(commandList) != 2:
                            output = f"Usage: cd [path]"
                        else:
                            if self._fs.cd(commandList[1]):
                                output = f"Invalid: Path \"{commandList[1]}\" does not exist"
                    case "ls":
                        if len(commandList) != 1:
                            output = f"Usage: ls"
                        else:
                            output = self._fs.ls()
                    case "mkdir":
                        if len(commandList) != 2:
                            output = "Usage: mkdir [name]"
                        else:
                            err = self._fs.mkdir(commandList[1])
                            if (err == 1):
                                output = "Invalid: Subdirectory cannot have the same name as the root directory."
                            if (err == 2):
                                output = "Invalid: Subdirectory of the same name already exists."
                            if (err == 3):
                                output = f"Invalid: Subdirectory cannot have the name {commandList[1]}"
                    case "rm":
                        if len(commandList) != 2:
                            output = "Usage: rm [name]"
                        else:
                            if self._fs.rm(commandList[1]):
                                output = f"File or Directory {commandList[1]} couldn't be found."
                    case "cat":
                        if len(commandList) != 2:
                            output = "Usage: cat [name]"
                        else:
                            output = self._fs.cat(commandList[1])
                            if output == "1":
                                output = f"File or cannot be read correctly, must end with '.txt'"
                            elif output == "2":
                                output = f"File {commandList[1]} couldn't be found."
                    case "exit":
                        self._powered = False
                        self.text.config(text="Virtual Machine Powered Off\n", anchor="w")
                    case _:
                        output = f"Error: command \'{command}\' not found.\nPlease use \'help\' if you are having trouble."
            elif self._curproc == runningApp.CHAT:
                pass
            elif self._curproc == runningApp.MAIL:
                pass
            else:
                output = "Something has gone VERY wrong.\n"
            # Update the terminal output
            newstr = self.text['text'] + self._ip + "/" + self._fs._cur_path + "$ > " + command + "\n" + output + ("" if output == "" else "\n")
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

class FileSystem():
    def __init__(self, ip: str) -> None:
        # Contains the VM's IP for identification purposes if needed, current directory, and a Directory Object for the root.
        self._ip = ip
        self._root = Directory("root")
        self._cur_path = self._root.get_path()
        self._cur_dir = self._root

        # Adding default files
        self.populate()

    def populate(self) -> None:
        self._root.add_dir("docs")
        self._root.add_dir("apps")
        self._root.add_dir("sys")
        self._root.get_dir("docs").add_dir("keys")
        self._root.get_dir("docs").add_file("dontreadme.txt")
        self._root.get_dir("docs").add_file("groceries.txt")
        self._root.get_dir("docs").add_file("lorem_ipsum.txt")
        self._root.get_dir("docs").add_file("reference_you_know.txt")
        self._root.get_dir("docs/keys").add_file("chatcode.txt")
        self._root.get_dir("docs/keys").add_file("serverIP.txt")
        self._root.get_dir("apps").add_file("mail")
        self._root.get_dir("apps").add_file("chat")
        self._root.get_dir("apps").add_file("gameclock")
        self._root.get_dir("apps").add_file("forkbomb")
        self._root.get_dir("sys").add_file("resh")
        self._root.get_dir("sys").add_file("pwdrst")

    def cd(self, path: str) -> int:
        dir = self._cur_dir.get_dir(path)
        if dir is None:
            return 1
        self._cur_dir = dir
        self._cur_path = dir.get_path()
        return 0
    
    def ls(self) -> str:
        l = self._cur_dir.get_list()
        ans = ""
        for x in l:
            ans += x + "\n"
        return ans[:-1]
    
    def mkdir(self, name: str) -> int:
        if name == "root":
            return 1
        if name == "" or name.find("-") != 1:
            return 3
        for s in self._cur_dir.get_subs():
            if name == s.get_name():
                return 2
        self._cur_dir.add_dir(name)
        return 0
    
    def rm(self, name: str) -> int:
        for f in self._cur_dir.get_files():
            if f == name:
                self._cur_dir._files.remove(f)
                return 0
        for s in self._cur_dir.get_subs():
            if s.get_name() == name:
                self._cur_dir._subdirs.remove(s)
                return 0
        return 1

    def cat(self, name: str) -> str:
        path = "Game_FS/" + self._cur_path.replace("/", "-") + name
        if path[-4:] != ".txt":
            return "1"
        if not os.path.isfile(path):
            return "2"
        f = open(path, "r")
        return "\n" + f.read() + "\n"

class Directory():
    def __init__(self, name: str, parent: Directory | None = None):
        # Contains parent directory, directory name, and list of files/sub-directories
        # Files are stored as paths to where the files are actually stored irl
        self._name = name
        self._parent = parent
        self._subdirs = [] # not including .. and .
        self._files = []
        self._path = (parent.get_path() + name + "/") if parent is not None else (name + "/")

    def get_name(self) -> str:
        return self._name
    
    def get_parent(self) -> Directory | None:
        return self._parent
    
    def get_subs(self) -> list:
        return self._subdirs

    def get_files(self) -> list:
        return self._files

    def get_path(self) -> str:
        return self._path
    
    def get_dir(self, path: str) -> Directory | None:
        """
        Get the Directory object in the file system from a given path.
        Returns None if the directory does not exist.
        """
        # Assuming path has valid syntax
        path = path.removesuffix("/") # Remove the last '/' if they were given
        path_list = path.split("/")
        cur_dir = self
        first_element = True
        for p in path_list:
            if p == ".": # e.g. "./keys"
                pass # Do nothing
            elif p == ".." and cur_dir != "root": # e.g. "../apps"
                cur_dir = cur_dir.get_parent()
            elif p == ".." and cur_dir == "root": # Invalid
                return None
            elif p == "root" and first_element: # e.g. "root/sys"
                # Go to the root Directory
                while cur_dir.get_parent() is not None:
                    cur_dir = cur_dir.get_parent()
            else:
                # Search subdirectories for a match and go from there
                found = False
                for s in cur_dir.get_subs():
                    if p == s.get_name():
                        found = True
                        cur_dir = s
                        break
                if not found:
                    return None
            first_element = False
        return cur_dir
    
    def add_dir(self, child: str) -> None:
        new = Directory(child, self)
        self._subdirs.append(new)

    def add_file(self, file: str) -> None:
        self._files.append(file)
    
    def get_list(self) -> list[str]:
        ans = ["..", "."] if self._parent is not None else ["."]
        for s in self.get_subs():
            ans.append(s.get_name())
        for f in self.get_files():
            ans.append(f)
        return ans

def bootOS(ip: str):
    root = tk.Tk()
    root.lift()
    root.attributes("-topmost", True)
    mari(root, ip)
    root.mainloop()