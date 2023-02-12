import base64
import hashlib
import math


def hash_code(key):
    m = hashlib.md5()
    m.update(bytes(key, 'utf-8'))
    return str(m.hexdigest())


class Cipher:
    def __init__(self, first=None):
        if first is not None:
            self.first = first
        else:
            self.first = [90, 114, 89, 97, 104, 28, 82, 86, 90, 119, 22, 124, 73, 21, 36, 21]
        self.second = [60, 104, 49, 87, 100, 41, 61, 76, 9, 70, 104, 1, 91, 16, 73, 30]

    def b64e(self, s):
        return base64.b64encode(s.encode()).decode()

    def b64d(self, s):
        return base64.b64decode(s).decode()

    def xor_massive(self, f, s, s2, key1):
        return [((f[i]) ^ (~s | ~i)) & ((f[i] & ~(s2 ^ i)) ^ key1[(i ^ ~f[i]) % 16])
                & (key1[(i ^ f[i]) % 16] | s2) for i in range(16)]

    @staticmethod
    def func(value, n1, n2):
        return (value ^ n1) ^ n2

    @staticmethod
    def func2(value, k1):
        return (value ^ (k1 | (int(math.sqrt(k1)) + 1))) ^ (int(math.sqrt(math.sqrt(k1))) + 1)

    @staticmethod
    def func3(value, k1):
        value ^= (sum([int(v) for v in str(k1 ** 0.125).replace('.', '')]) + 1)
        return value

    @staticmethod
    def func4(value, k2):
        return ~(~value ^ k2)

    @staticmethod
    def eq(value, k4):
        return 1 ^ value ^ k4

    @staticmethod
    def rotate_List1(arry, E, K):
        arry[:] = arry[E:K] + arry[0:E]
        return arry

    def encrypt(self, text, key):
        text_mas = [ord(i) for i in self.b64e(text)]
        key_mas = [ord(i) for i in (hash_code(key))]
        hash_mas = [ord(i) for i in hash_code(self.b64e(key))]
        massive_generated_keys = [key_mas]
        leTextMas = len(text_mas)
        i = 1
        for gIndex in range(16):
            if i <= 15:
                massive_generated_keys.append(
                    list(map(lambda x: (x ^ self.first[i]) % 126 + 1, self.xor_massive(massive_generated_keys[i - 1],
                                                                                       self.first[i],
                                                                                       self.second[i], key_mas))))
            i += 1
            gMas = massive_generated_keys[gIndex]
            for index in range(leTextMas):
                text_mas[index] = self.func(text_mas[index], gMas[(gIndex + index) % 16], (self.second[(gIndex + index) % 16] ^ 125) % 126 + 1)
                text_mas[index] ^= gMas[gIndex]
                text_mas[index] ^= key_mas[gIndex]
                text_mas[index] = self.func2(text_mas[index], key_mas[gIndex])
                if index <= leTextMas // 2 and gIndex % 2 == 0:
                    text_mas[index] = ~text_mas[index]
                elif gIndex % 2 != 0:
                    text_mas[index] = ~text_mas[index]
                text_mas[index] = self.func3(text_mas[index], key_mas[-gIndex])
                text_mas[index] = self.func4(text_mas[index], key_mas[gIndex])
                text_mas[index] ^= hash_mas[gIndex]
                text_mas[index] = self.eq(text_mas[index], key_mas[gIndex])
                text_mas[index] ^= key_mas[-gIndex]
            hash_mas = self.rotate_List1(hash_mas, 2, 32)
            hash_mas = [(i ^ (self.second[gIndex] + 1) + 1) for i in hash_mas]
        return ' '.join([str(i) for i in text_mas])

    def decrypt(self, text, key):
        text_mas = [int(i) for i in text.split()]
        key_mas = [ord(i) for i in (hash_code(key))]
        hash_text_mas = [ord(i) for i in hash_code(self.b64e(key))]
        massive_generated_keys = [key_mas]
        leTextMas = len(text_mas)
        i = 1
        for gIndex in range(16):
            if i <= 15:
                massive_generated_keys.append(
                    list(map(lambda x: (x ^ self.first[i]) % 126 + 1, self.xor_massive(massive_generated_keys[i - 1],
                                                                                       self.first[i],
                                                                                       self.second[i], key_mas))))
            i += 1
            gMas = massive_generated_keys[gIndex]
            for index in range(leTextMas):
                text_mas[index] = self.func(text_mas[index], gMas[(gIndex + index) % 16], (self.second[(gIndex + index) % 16] ^ 125) % 126 + 1)
                text_mas[index] ^= gMas[gIndex]
                text_mas[index] ^= key_mas[gIndex]
                text_mas[index] = self.func2(text_mas[index], key_mas[gIndex])
                if index <= leTextMas // 2 and gIndex % 2 == 0:
                    text_mas[index] = ~text_mas[index]
                elif gIndex % 2 != 0:
                    text_mas[index] = ~text_mas[index]
                text_mas[index] = self.func3(text_mas[index], key_mas[-gIndex])
                text_mas[index] = self.func4(text_mas[index], key_mas[gIndex])
                text_mas[index] ^= hash_text_mas[gIndex]
                text_mas[index] = self.eq(text_mas[index], key_mas[gIndex])
                text_mas[index] ^= key_mas[-gIndex]
            hash_text_mas = self.rotate_List1(hash_text_mas, 2, 32)
            hash_text_mas = [(i ^ (self.second[gIndex] + 1) + 1) for i in hash_text_mas]
        return self.b64d(''.join([chr(i) for i in text_mas]))
