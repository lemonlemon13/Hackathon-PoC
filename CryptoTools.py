
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
        file = open("b64map")
        for c in file.read():
            mapping.append(c)
        return mapping