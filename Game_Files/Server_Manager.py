#
# This script is for handling details about the game and the server's state.
#

from Game_Files.CryptoTools import *

class ServerManager():
    def __init__(self, code:str) -> None:
        self._host_name = ""
        self._players = []
        self._uninames = {}

        self._started = False

        self._joincode = code
        self._rng = RNG()
        self._rng.set_from_code(code)

        # Dictionary connecting player names in _players to IPs
        self._IPs = {}
        # Set up important IPs for the game
        self._teamA_IP_prefix = str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255)) + "."
        self._teamB_IP_prefix = self._teamA_IP_prefix
        while self._teamB_IP_prefix == self._teamA_IP_prefix:
            self._teamB_IP_prefix = str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255)) + "."
        self._teamA_Server_IP = self._teamA_IP_prefix + str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255))
        self._teamB_Server_IP = self._teamB_IP_prefix + str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255))
        self._flipTeams = False # False = A, True = B

    def add_player(self, name:str) -> str:
        new_name = name
        if name not in self._players:
            self._players.append(name)
            self._uninames[name] = 1
        # Add something extra to duplicate names
        else:
            new_name = name + f"({self._uninames[name]})"
            self._players.append(new_name)
            self._uninames[name] += 1
            self._uninames[new_name] = 1

        # If this is the first person to join, make them the host
        if len(self._players) == 1:
            self._host_name = new_name

        self.add_IP(new_name)

        return new_name
    
    def add_IP(self, name:str) -> None:
        if self._flipTeams:
            temp_IP = self._teamB_IP_prefix + str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255))
            while temp_IP == self._teamB_Server_IP or temp_IP in self._IPs.values():
                temp_IP = self._teamB_IP_prefix + str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255))
        else:
            temp_IP = self._teamA_IP_prefix + str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255))
            while temp_IP == self._teamA_Server_IP or temp_IP in self._IPs.values():
                temp_IP = self._teamA_IP_prefix + str(self._rng.next_range(0, 255)) + "." + str(self._rng.next_range(0, 255))
        self._IPs[name] = temp_IP
        self._flipTeams = not self._flipTeams
        

    def get_host(self) -> str:
        return self._host_name

    def start_game(self) -> None:
        self._started = True