import struct
import base64
import os

class Magma:
    S_BOX = (
        (12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1),
        (6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15),
        (11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0),
        (12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11),
        (7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12),
        (5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0),
        (8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7),
        (1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 12, 11, 2, 9),
    )

    def __init__(self, key):
        """
        key: 32 байта (256 бит)
        """
        if len(key) != 32:
            raise ValueError("Ключ должен быть длиной 32 байта (256 бит)")

        self.keys = struct.unpack("<8I", key)

    def _f(self, part, key):
        temp = (part + key) % (2**32)
        substituted = 0
        for i in range(8):
            # Замена по S-блокам
            nibble = (temp >> (4 * i)) & 0x0F
            substituted |= (self.S_BOX[i][nibble] << (4 * i))
        return ((substituted << 11) | (substituted >> (32 - 11))) & 0xFFFFFFFF

    def encrypt_block(self, block):
        left, right = struct.unpack(">2I", block)

        for i in range(32):
            if i < 24:
                k = self.keys[i % 8]
            else:
                k = self.keys[7 - (i % 8)]
                
            new_right = left ^ self._f(right, k)
            left = right
            right = new_right

        return struct.pack(">2I", right, left)

    def decrypt_block(self, block):
        left, right = struct.unpack(">2I", block)
        
        for i in range(32):
            if i < 8:
                k = self.keys[i % 8]
            else:
                k = self.keys[7 - (i % 8)]
                
            new_right = left ^ self._f(right, k)
            left = right
            right = new_right
            
        return struct.pack(">2I", right, left)

class MagmaCTR:
    def __init__(self, key):
        self.magma = Magma(key)

    def process(self, data, iv):
        result = bytearray()
        counter = struct.unpack(">Q", iv)[0]
        
        for i in range(0, len(data), 8):
            keystream_block = self.magma.encrypt_block(struct.pack(">Q", counter + (i // 8)))
            
            chunk = data[i:i+8]
            for j in range(len(chunk)):
                result.append(chunk[j] ^ keystream_block[j])
                
        return bytes(result)

MASTER_KEY = os.environ.get("MAGMA_SECRET_KEY", "static_key_for_dev_32bytes_long!!").encode()[:32].ljust(32, b'\0')

def encrypt_text(text):
    if not text: return ""
    iv = os.urandom(8)
    ctr = MagmaCTR(MASTER_KEY)
    encrypted = ctr.process(text.encode('utf-8'), iv)
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt_text(encrypted_base64):
    if not encrypted_base64: return ""
    try:
        raw = base64.b64decode(encrypted_base64)
        iv = raw[:8]
        data = raw[8:]
        ctr = MagmaCTR(MASTER_KEY)
        decrypted = ctr.process(data, iv)
        return decrypted.decode('utf-8')
    except Exception:
        return "[Ошибка расшифровки]"
