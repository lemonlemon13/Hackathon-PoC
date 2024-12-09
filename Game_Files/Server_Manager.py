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

        self._IPs = []
        self._teamA_IP = ""
        self._teamB_IP = ""
        self._teamA_Server_IP = ""
        self._teamB_Server_IP = ""

        self._joincode = code
        self._rng = RNG()
        self._rng.set_from_code(code)

    def add_player(self, name:str) -> None:
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
            self._host_name = name

    def get_host(self) -> str:
        return self._host_name

    def start_game(self) -> None:
        self._started = True
        for i in range(0, len(self._players)):
            # Generate in-game IPs for them to use
            pass