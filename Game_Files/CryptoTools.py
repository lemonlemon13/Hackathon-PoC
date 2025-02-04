#
# This script handles Cryptographic Functions, translating server IP/ports into a Lobby Code, and other functions.
#

class LobbyCode():

    def AddrToCode(self, ip: str, port: int) -> str:
        # Gets the conversion map to further compress the code's ASCII representation
        b64 = self.getb64map()
        # Get each part of the IP address in Hexadecimal for calculation
        ipHex = ''
        for x in ip.split("."):
            ipHex += f"{int(x):02X}"
        # Also get the port number in hex as well
        portHex = f"{port:04X}"
        i = 0
        codeHex = ''
        # Obfuscate the ip address based on the port number
        for n in ipHex:
            a = int(n, base=16)
            x = int(portHex[i % 4], base=16)
            ipX = ((a + (x * x + 1)) % 16)
            codeHex += f"{ipX:1X}"
            i += 1
        # add the port number on the end
        codeHex += portHex
        # convert it into binary to convert with the base64 mapping
        codeBin = f"{int(codeHex,base=16):48b}"
        code = ''
        for b in range(0, len(codeBin), 6):
            num = codeBin[b:b+6]
            char = b64[int(num, base=2)]
            code += char
            if len(code) == 4:
                code += "-"
        return code
    
    def CodeToAddr(self, code: str) -> tuple[str, int]:
        # Gets the conversion map to decompress from the input into the binary
        b64 = self.getb64map()
        codeBin = ''
        for c in code:
            if c == "-":
                continue
            codeBin += f"{int(b64.index(c)):06b}"
        codeHex = f"{int(codeBin,base=2):12X}"
        ipHex = codeHex[0:8]
        ip = ""
        portHex = codeHex[8:]
        port = int(portHex,base=16)
        i = 0
        curDigit = ""
        digitCount = 0
        for x in ipHex:
            a = int(x, base=16)
            x = int(portHex[i % 4], base=16)
            ipX = ((a - (x * x + 1)) % 16)
            curDigit += f"{ipX:1X}"
            if len(curDigit) == 2:
                ip += f"{int(curDigit,base=16)}"
                digitCount += 1
                curDigit = ""
                if (digitCount != 4):
                    ip += "."
            i += 1
        return (ip, port)
    
    def getb64map(self) -> list[str]:
        mapping = []
        file = open("Game_Files/b64map", "r")
        for c in file.read():
            mapping.append(c)
        return mapping
    
class RNG():
    def __init__(self, seed:int = None) -> None:
        if seed is not None:
            self._seed = seed
        else:
            self._seed = 0
        self._cur = self._seed
        self.MAX = (2 ** 32)

    def set_from_code(self, code:str) -> None:
        temp = 0
        for c in code:
            num = ord(c)
            temp |= num
            temp = 3 * temp + 1
            temp = temp % self.MAX
        self._seed = temp
        self._cur = temp

    def next(self) -> int:
        self._cur = (13 * self._cur + 7) % self.MAX
        return self._cur
    
    def reset(self) -> None:
        self._cur = self._seed

    def next_range(self, min:int, max:int) -> int:
        """
        Returns the next random number from min (inclusive) to max (inclusive).
        NOTE: The range will be from min (inclusive) to max (exclusive) if min = 0.
        """
        return (self.next() % max) + min
    
class CaesarCipher():

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def encrypt(self, pt: str, key: int) -> str:
        ct = ""
        pt = pt.upper()
        for c in pt:
            new = c
            i = self.alphabet.find(c)
            if i != -1:
                new = self.alphabet[(i + key) % 26]
            ct += new
        return ct
    
    def decrypt(self, ct: str, key: int) -> str:
        pt = ""
        ct = ct.upper()
        for c in ct:
            new = c
            i = self.alphabet.find(c)
            if i != -1:
                new = self.alphabet[(i - key) % 26]
            pt += new
        return pt
    
class ZigZagCipher():

    def encrypt(self, pt: str, key: int) -> str:
        ct = ""

        for i in range(0, key):
            x = i
            while x < len(pt):
                ct += pt[x]
                x += key
        return ct

    def decrypt(self, ct: str, key: int) -> str:
        pt = ""
        steps = len(ct) // key

        for i in range(0, steps):
            x = i
            while x < len(pt):
                ct += pt[x]
                x += steps
        return pt

class ProductCipher():

    def encrypt(self, pt: str, key: int) -> str:
        return ZigZagCipher.encrypt(CaesarCipher.encrypt(pt, key), key)

    def decrypt(self, ct: str, key: int) -> str:
        return ZigZagCipher.decrypt(CaesarCipher.decrypt(ct, key), key)

class Hasher():

    def hash_string(i: str) -> int:
        ans = 1
        for c in i:
            x = ord(c)
            ans = (x * ans) + 1
            ans = (ans << 1) ^ (ans >> 1)
            return ans % (2**32)