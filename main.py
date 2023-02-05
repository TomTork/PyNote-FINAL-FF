import os.path
import random
import string
import sys
import re
import plyer
import sqlite3
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QShortcut, QKeySequence
from PyQt6.QtWidgets import *
from tkinter import Tk

import base64
import hashlib
import numpy as np

Gkey = ''  # Временная переменная для хранения ключа шифрования
GEnter = True  # Переменная отвечающая за закрытие основного окна при неподтверждении пароля
GNote = ''  # Временная переменная для хранения ключа шифрования для отдельной заметки
open_or_delete = -1  # Временная переменная для menu в Main | 0 -> open | 1 -> delete


def to_primary_key(key: str) -> str:  # Приводит длину ключа в 16 символов, если требуется
    le = len(key)
    if le == 16:
        return key
    elif le > 16:
        return key[0:16]
    else:
        return key + '0' * (16 - le)


def hash_code(key):
    m = hashlib.md5()
    m.update(bytes(key, 'utf-8'))
    return str(m.hexdigest())


class Cipher:
    def __init__(self, g_mas=None, initial_m=None, prepare_g=0, prepare_m=0):
        # Проверка на использования личной таблицы box (таблицы замены)
        if g_mas is not None and initial_m is not None:
            self.g_mas = g_mas
            self.initial_m = initial_m
        else:
            self.g_mas = [9, 229, 180, 243, 169, 174, 125, 197, 83, 241, 66, 112, 124, 148, 110, 134]
            # Массив для замены в return box
            self.initial_m = [92, 55, 33, 124, 8, 183, 140, 171, 136, 129, 126, 154, 216, 150, 40, 106]
            # Массив для замены m в box
        self.reverse_g_mas = self.g_mas[::-1]
        self.reverse_initial_n = self.initial_m[::-1]
        self.prepare_g = prepare_g
        self.prepare_m = prepare_m

        self.global_dict = {'': 1, 'e': 2, 't': 3, 'a': 4, 'o': 5, 'i': 6, 'n': 7, 's': 8, 'h': 9, 'r': 10, 'd': 11,
                            'l': 12, 'c': 13, 'u': 14, 'm': 15, 'w': 16, 'f': 17, 'g': 18, 'y': 19, 'p': 20, 'b': 21,
                            'v': 22, 'k': 23, 'x': 24, 'j': 25, 'q': 26, 'z': 27, ' ': 28,
                            'E': 29, 'T': 30, 'A': 31, 'O': 32, 'I': 33, 'N': 34, 'S': 35, 'H': 36, 'R': 37, 'D': 38,
                            'L': 39, 'C': 40, 'U': 41, 'M': 42, 'W': 43, 'F': 44, 'G': 45, 'Y': 46, 'P': 47, 'B': 48,
                            'V': 49, 'K': 50, 'X': 51, 'J': 52, 'Q': 53, 'Z': 54,
                            'о': 55, "е": 56, "а": 57, "и": 58, "н": 59, "т": 60, "с": 61, "р": 62, "л": 63, "в": 64,
                            "к": 65, "д": 66, "м": 67, "п": 68, "у": 69, "г": 70, "б": 71, "з": 72, "я": 73, "ы": 74,
                            "ь": 75, "ч": 76, "х": 77, "ж": 78, "ш": 79, "ц": 80, "щ": 81, "ф": 82, "ю": 83, "э": 84,
                            "й": 85, "ё": 86, "ъ": 87, ",": 88, ".": 89,
                            'О': 90, "Е": 91, "А": 92, "И": 93, "Н": 94, "Т": 95, "С": 96, "Р": 97, "Л": 98, "В": 99,
                            "К": 100, "Д": 101, "М": 102, "П": 103, "У": 104, "Г": 105, "Б": 106, "З": 107, "Я": 108,
                            "Ы": 109, "Ч": 110, "Х": 111, "Ж": 112, "Ш": 113, "Ц": 114, "Щ": 115, "Ф": 116, "Ю": 117,
                            "Э": 118, "Й": 119, "Ё": 120, "Ъ": 121, "Ь": 122, '?': 123, '!': 124, '(': 125, ')': 126,
                            '"': 127, "'": 128, ':': 129, '<': 130, '>': 131, '[': 132, ']': 133, '\\': 134, '|': 135,
                            '*': 136, '/': 137, '-': 138, '=': 139, '+': 140, '_': 141, '—': 142, '%': 143, ';': 144,
                            '$': 145, '&': 146, '^': 147, '#': 148, '№': 149, '@': 150, '`': 151, '~': 152,
                            '1': 153, '2': 154, '3': 155, '4': 156, '5': 157, '6': 158, '7': 159, '8': 160, '9': 161,
                            '0': 162, '\n': 163, '\t': 164
                            }

    def get_word_by_dict(self, number):
        for i in self.global_dict:
            if self.global_dict[i] == number:
                return i
        return chr(number)

    def get_number_by_dict(self, word):
        if word in self.global_dict:
            return self.global_dict[word]
        else:
            return ord(word)

    def box_function(self, b):
        self.prepare_g += 1
        self.prepare_m += 1
        m = self.initial_m[self.prepare_m % 16]
        r = 0
        q = ~ b | 0
        for i in range(8):
            r = (r << 1) | (q ^ m)
            m = (m >> 1) | ((m & 1) << 7)
        return r ^ self.g_mas[self.prepare_g % 16]

    @staticmethod
    def inv_plus(x):
        return -(x + 1)

    def xor_massive(self, f, s, s2, key1):
        return [
            ((self.pol_inversion(f[i]) ^ (~s | ~i)) & ((f[i] & ~self.pol_inversion(s2 ^ i)) ^ key1[(i ^ ~f[i]) % 16])
             & (key1[(i ^ f[i]) % 16] | self.pol_inversion(s2)))
            for i in range(len(f))]

    @staticmethod
    def extension_list(massive):
        [massive.append(1) for _ in range(32 - len(massive) % 32)]
        return [list(i) for i in np.hsplit(np.array(massive), len(massive) / 32)]

    @staticmethod
    def simple_extension_list(massive):
        return [list(i) for i in np.hsplit(np.array(massive), len(massive) / 32)]

    def enc_base64(self, value):  # на вход массив чисел - выход строка
        a = base64.b64encode(self.joined(list(map(str, value))).encode('UTF-8')).decode('UTF-8')
        return a

    def dec_base64(self, value):  # вход строка - выход массив чисел
        return list(map(lambda x: self.undo(x), base64.b64decode(value).decode('UTF-8').split()))

    def joined(self, massive):  # Перевод массива в строку
        a = ''
        for i in massive:
            for t in str(i).replace('[', '').replace(']', '').split(', '):
                a += str(self.convert_base(int(t), 36)) + ' '
        return a

    def to_final_chr(self, massive):  # Финальный перевод массива в chr
        a = ''
        for i in massive:
            for t in i:
                if t != 1:
                    a += self.get_word_by_dict(int(t))
                else:
                    return a
        return a

    @staticmethod
    def convert_base(num, to_base=10, from_base=10):
        n = int(num, from_base) if isinstance(num, str) else num
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        res = ""
        while n > 0:
            n, m = divmod(n, to_base)
            res += alphabet[m]
        return res[::-1]

    @staticmethod
    def s_box(element, n1, n2):
        m = n1
        r = 0
        q = ~ element | 0
        for i in range(16):
            r = (r << 1) | (q ^ m)
            m = (m >> 1) | ((m & 1) << 7)
            return r ^ n2

    @staticmethod
    def pol_inversion(value):
        b = bin(value)[2:]
        s = ''
        for el in range(len(b)):
            if el >= 2:
                if b[el] == '1':
                    s += '0'
                else:
                    s += '1'
            else:
                s += b[el]
        return int(s, 2)

    @staticmethod
    def undo(el):
        return int(el, 36)

    @staticmethod
    def rotate_List1(arry, E, K):
        arry[:] = arry[E:K] + arry[0:E]
        return arry

    def encrypt(self, text: str, key: str) -> str:
        # Подготовительный этап
        text_mas = self.extension_list(list(map(lambda x: int(str(hex(self.get_number_by_dict(x)))[2:], 16), text)))
        key_mas = list(map(lambda x: self.box_function(x), list(map(lambda x:
                                                                    int(str(hex(self.get_number_by_dict(x)))[2:], 16),
                                                                    hash_code(key)))))
        key_mas = list(map(lambda x: self.inv_plus(x), key_mas))
        massive_generated_keys = [key_mas]
        for i in range(1, 16):  # Генерируем 16 массивов ключей
            massive_generated_keys.append(
                list(map(lambda x: x ^ self.initial_m[i], self.xor_massive(massive_generated_keys[i - 1],
                                                                           self.initial_m[i],
                                                                           self.g_mas[i], key_mas)))
            )
        time = []
        m = []
        for i in range(16):
            time.clear()
            k = 0
            for massive in text_mas:
                m.clear()
                k += 1
                m = list(map(lambda x: x << (key_mas[k % 32] % 4), massive))
                for ind in range(len(m)):
                    m[ind] = self.pol_inversion(self.inv_plus(self.s_box(int(str(hex(m[ind]))[2:], 16),
                                                      int(str(hex(massive_generated_keys[i][k % 32]))[2:], 16),
                                                      int(str(hex(massive_generated_keys[i][k % 32]))[2:], 16)))
                                                << (massive_generated_keys[i][k % 32] % 16))
                    if ind <= i:
                        m[ind] -= i

                time.append(self.rotate_List1(m.copy(), i, 32))
            text_mas = time.copy()
        return self.enc_base64(text_mas)

    def decrypt(self, text: str, key: str) -> str:
        # Подготовительный этап
        text_mas = self.simple_extension_list(self.dec_base64(text))
        key_mas = list(map(lambda x: self.box_function(x), list(map(lambda x:
                                                                    int(str(hex(self.get_number_by_dict(x)))[2:], 16),
                                                                    hash_code(key)))))
        key_mas = list(map(lambda x: self.inv_plus(x), key_mas))
        massive_generated_keys = [key_mas]
        for i in range(1, 16):  # Генерируем 16 массивов ключей
            massive_generated_keys.append(
                list(map(lambda x: x ^ self.initial_m[i], self.xor_massive(massive_generated_keys[i - 1],
                                                                           self.initial_m[i],
                                                                           self.g_mas[i], key_mas)))
            )
        time = []
        m = []
        for i in range(16):
            time.clear()
            k = 0
            for massive in text_mas:
                m.clear()
                k += 1
                m = list(map(lambda x: x >> (key_mas[k % 32] % 4), massive))
                for ind in range(len(m)):
                    if ind <= i:
                        m[ind] -= i
                    m[ind] = self.pol_inversion(self.inv_plus(self.s_box(int(str(hex(m[ind]))[2:], 16),
                                                           int(str(hex(massive_generated_keys[i][k % 32]))[2:], 16),
                                                           int(str(hex(massive_generated_keys[i][k % 32]))[2:], 16)))
                              >> (massive_generated_keys[i][k % 32] % 16))
                time.append(self.rotate_List1(m.copy(), 16 - i, 32))
            text_mas = time.copy()
        return self.to_final_chr(text_mas)


def notify(text, title):  # Функция для уведомления пользователя, автоматически не скипается
    pass
    # plyer.notification.notify(message=f'{text}', app_name='PyNote', app_icon=r'pynote.ico',
    #                           title=title)


def confirm():  # Проверка пароля
    global GEnter
    if Database().get_ask_key() == 1:
        dialog = ConfirmPasswordInputDialog(labels=["Пароль:"])
        if not dialog.exec() and not Gkey:
            GEnter = False
            dialog.close()


class GeneratePasswordForNoteInputDialog(QDialog):  # Создание пароля для новой заметки
    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self.database = Database()
        self.setWindowIcon(QIcon('pynote.png'))
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.setWindowTitle('Придумайте пароль')
        layout = QFormLayout(self)
        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(lambda: self.ok())

    def getInputs(self):
        return tuple(input.text() for input in self.inputs)

    def ok(self):  # Обработка нажатия на кнопку 'ок'
        global GNote
        initial = self.getInputs()[0]
        if initial != "":
            self.close()
            GNote = initial
        else:
            GNote = 'NULL'


class ConfirmPasswordForNoteInputDialog(QDialog):  # Подтверждение пароля для новой заметки
    def __init__(self, labels, parent=None, number=0):
        super().__init__(parent)
        self.database = Database()
        self.setWindowIcon(QIcon('pynote.png'))
        self.number = number
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.setWindowTitle('Подтвердите пароль')
        layout = QFormLayout(self)
        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(lambda: self.ok())

    def getInputs(self):
        return tuple(input.text() for input in self.inputs)

    def ok(self):  # Обработка нажатия на кнопку 'ок'
        global GNote
        if str(hash_code(self.getInputs()[0])) == str(self.database.get_hash_code_note(self.number)[0]):
            self.close()
            GNote = self.getInputs()[0]


class ConfirmPasswordInputDialog(QDialog):  # Окно, открываемое для подтверждения главного ключа шифрования
    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self.database = Database()
        self.setWindowIcon(QIcon('pynote.png'))
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.setWindowTitle('Подтвердите пароль')
        layout = QFormLayout(self)
        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])
        self.inputs[0].setFocus()
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(lambda: self.ok())

    def getInputs(self):
        return tuple(input.text() for input in self.inputs)

    def ok(self):  # Обработка нажатия на кнопку 'ок'
        global Gkey
        if str(hash_code(self.getInputs()[0])) == str(self.database.get_hash_code()):
            self.close()
            Gkey = self.getInputs()[0]


class AreYouSureInputDialog(QDialog):  # Окно, открываемое в случае желания пользователя входить без пароля
    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('pynote.png'))
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.setWindowTitle('Вы уверены? Это действие не безопасно. Введите пароль повторно для подтверждения')
        layout = QFormLayout(self)
        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(lambda: self.ok())

    def getInputs(self):
        return tuple(input.text() for input in self.inputs)

    def ok(self):  # Обработка нажатия на кнопку 'ок'
        if str(hash_code(self.getInputs()[0])) == str(Database().get_hash_code()):
            file = open('key.txt', 'w+')  # Создаём внутренний файл для хранения пути баз данных
            file.write(self.getInputs()[0])
            file.close()
            Database().set_aks_key(0)
            self.close()
        else:
            notify('Your key is wrong!', 'Check the input line')
            self.close()


class MyInputDialog(QDialog):  # Окно, открываемое в случае удаления пользователем бд
    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('pynote.png'))
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        self.setWindowTitle('Ваша база данных была уничтожена. Пожалуйста, заполните поля ниже')
        layout = QFormLayout(self)
        self.inputs = []
        for lab in labels:
            self.inputs.append(QLineEdit(self))
            layout.addRow(lab, self.inputs[-1])

        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(lambda: self.ok())

    def getInputs(self):
        return tuple(input.text() for input in self.inputs)

    def ok(self):  # Обработка нажатия на кнопку 'ок'
        if '\\' in self.getInputs()[0]:
            if not self.getInputs()[1]:
                k = random_key()
                Database().create_database_(hash_code(k), self.getInputs()[0])
                notify(k, 'Remember your key!')
            else:
                Database().create_database_(hash_code(self.getInputs()[1]), self.getInputs()[0])
                notify(self.getInputs()[1], 'Remember your key!')
            self.close()
        else:
            notify('Check the input lines', 'Error')


class Database:  # Класс для обработки sqlite запросов
    def listener(self):  # Проверка на существование базы данных
        if not self.exist_database_():
            self.table_database_was_del()
        if not self.exist_notes():
            self.create_notes(self.get_path())
        if not self.exist_settings():
            self.create_settings(self.get_path())

    def create_database_(self, ha, path):  # Создание базы данных
        try:
            conn = sqlite3.connect(f'{path}\database.db')
            c = conn.cursor()
            if not os.path.isfile('database.db'):
                c.execute("""create table database_ (
                                        identity integer,
                                        path text,
                                        hash_key text
                                        )""")

                conn.commit()  # Фиксируем текущие значения в дб
                c.execute(f"INSERT INTO database_ VALUES (0, '{path}', '{ha}')")  # Значения по умолчанию
                conn.commit()
            conn.close()
            file = open('path.txt', 'w+')  # Создаём внутренний файл для хранения пути баз данных
            file.write(path)
            file.close()
        except sqlite3.Error as error:
            notify(f'{error}', 'Error')

    def create_notes(self, path):  # Создание базы данных для создания заметок
        try:
            conn = sqlite3.connect(f'{path}\TNotes.db')
            c = conn.cursor()
            if not os.path.isfile('TNotes.db'):
                c.execute("""create table notes (
                                        number integer,
                                        txt text,
                                        hash_key text
                                        )""")
                conn.commit()
            conn.close()
        except sqlite3.Error as error:
            pass

    def create_settings(self, path):
        try:
            conn = sqlite3.connect(f'{path}\Settings.db')
            c = conn.cursor()
            if not os.path.isfile('Settings.db'):
                c.execute("""create table settings (
                                        identity integer,
                                        resolution_main text,
                                        resolution_note text,
                                        new_key_for_new_note integer,
                                        ask_key integer,
                                        key_entrance text
                                        )""")
                conn.commit()
                # 0 - False, 1 - True
                c.execute(f'insert into settings values (0, "1366x768", "800x600", 0, 1, "")')
                conn.commit()
            conn.close()
        except sqlite3.Error as error:
            pass

    def new_note(self, text, password=''):  # Создание новой заметки
        Database().listener()
        conn = sqlite3.connect(f'{Database().get_path()}\TNotes.db')
        c = conn.cursor()
        if password == '':
            c.execute(f'insert into notes values ({int(Database().get_count_notes())},'
                      f' "{str(Cipher().encrypt(text, Gkey))}", "EMPTY")')
            conn.commit()
        else:
            c.execute(f'insert into notes values ({int(Database().get_count_notes())},'
                      f'"{str(Cipher().encrypt(text, password))}", "{hash_code(password)}")')
            conn.commit()
        conn.close()

    def get_all_notes(self):
        Database().listener()
        conn = sqlite3.connect(f'{Database().get_path()}\TNotes.db')
        c = conn.cursor()
        c.execute('select * from notes')
        mas = c.fetchall()
        conn.close()
        return mas  # Возвращает массив массивов из базы данных TNotes

    def initSettings(self):
        conn = sqlite3.connect(f'{self.get_path()}\Settings.db')
        c = conn.cursor()
        c.execute('select * from settings')
        return c

    def get_count_notes(self):  # Получение номера последней существующей заметки для создания новой
        try:
            conn = sqlite3.connect(f'{Database().get_path()}\TNotes.db')
            c = conn.cursor()
            c.execute('select * from notes')
            sp = c.fetchall()
            if len(sp) != 0:
                k = int(sp[-1][0]) + 1
            else:
                k = 0
            conn.close()
            return k
        except sqlite3.Error:
            return 0

    def update_note(self, number, text):  # Обновление текста в заметке
        conn = sqlite3.connect(f'{Database().get_path()}\TNotes.db')
        c = conn.cursor()
        if GNote != '':
            c.execute(f'update notes set txt="{str(Cipher().encrypt(text, GNote))}" where number={number}')
            conn.commit()
        else:
            c.execute(f'update notes set txt="{str(Cipher().encrypt(text, Gkey))}" where number={number}')
            conn.commit()
        conn.close()

    def update_note_in_mode_editing(self, number, text):  # Обновление текста в режиме редактирования
        conn = sqlite3.connect(f'{Database().get_path()}\TNotes.db')
        c = conn.cursor()
        c.execute(f'update notes set txt="{str(text)}" where number={number}')
        conn.commit()
        conn.close()

    def delete_note(self, number: int):  # Удаление заметки по номеру
        conn = sqlite3.connect(f'{Database().get_path()}\TNotes.db')
        c = conn.cursor()
        c.execute(f'delete from notes where number={number}')
        conn.commit()
        conn.close()

    def get_hash_code_note(self, number=0):
        conn = sqlite3.connect(f'{self.get_path()}\TNotes.db')
        c = conn.cursor()
        c.execute(f'select hash_key from notes where number={number}')
        h = c.fetchone()
        conn.close()
        return h

    def get_hash_code(self):
        conn = sqlite3.connect(f'{self.get_path()}\database.db')
        c = conn.cursor()
        c.execute('select * from database_')
        auto = c.fetchone()[2]
        conn.close()
        return auto

    def get_encrypted_text_note(self, number: int = 0):
        conn = sqlite3.connect(f'{self.get_path()}\TNotes.db')
        c = conn.cursor()
        c.execute(f'select txt from notes where number={number}')
        t = c.fetchone()
        conn.close()
        return t

    def get_resolution_main(self):
        return self.initSettings().fetchone()[1]

    def get_resolution_note(self):
        return self.initSettings().fetchone()[2]

    def get_new_key_for_new_note(self):
        return self.initSettings().fetchone()[3]

    def get_ask_key(self):
        return self.initSettings().fetchone()[4]

    def get_usb_entrance(self):
        return self.initSettings().fetchone()[5]

    def key_entrance(self):
        return self.initSettings().fetchone()[6]

    def replace_statement(self, where, statement, is_str: bool = True):  # Функция для обновления базы настроек
        conn = sqlite3.connect(f'{self.get_path()}\Settings.db')
        c = conn.cursor()
        if is_str:  # Если входное значение строка
            c.execute(f'update settings set {where}="{statement}" where identity=0')
        else:  # Если int
            c.execute(f'update settings set {where}={statement} where identity=0')
        conn.commit()
        conn.close()

    def set_resolution_main(self, width, height):
        self.replace_statement('resolution_main', f'{width}x{height}')

    def set_resolution_note(self, width, height):
        self.replace_statement('resolution_note', f'{width}x{height}')

    def set_new_key_for_new_note(self, n: int):
        self.replace_statement('new_key_for_new_note', n, False)

    def set_aks_key(self, n: int):
        self.replace_statement('ask_key', n, False)

    def set_usb_entrance(self, n: int):
        self.replace_statement('usb_entrance', n, False)

    def set_key_entrance(self, val):
        self.replace_statement('key_entrance', val)

    def get_path(self):  # Функция для получения пути из внутреннего файла
        if os.path.exists('path.txt'):
            file = open('path.txt', 'r')
            return file.read()
        else:
            self.table_database_was_del()
            return self.get_path()

    def exist_database_(self):  # Проверка на существования основной базы данных
        if os.path.isfile(f'{self.get_path()}\database.db'):
            return True
        return False

    def exist_settings(self):  # Проверка на существование базы настроек
        if os.path.isfile(f'{self.get_path()}\Settings.db'):
            return True
        return False

    def exist_notes(self):  # Проверка на существование базы заметок
        if os.path.isfile(f'{self.get_path()}\TNotes.db'):
            return True
        return False

    def table_database_was_del(self):  # Функция, запускающая MyInputDialog
        if not self.exist_database_():
            dialog = MyInputDialog(labels=["Destination folder", "Password"])
            if not dialog.exec():
                self.table_database_was_del()


def random_key():  # Генерация случайного ключа длиной в 16 символов
    m = [i for i in string.digits + string.ascii_uppercase + string.ascii_lowercase]
    random.shuffle(m)  # Перемешивание всех значений массива
    return ''.join(m[:16])


class Example(QWidget):  # Стартовое окно
    def __init__(self):
        super().__init__()
        self.edt1 = QLineEdit('', self)
        self.edt1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.edt1.setContentsMargins(10, 0, 10, 0)
        self.btn = QPushButton('Начать!', self)
        self.btn2 = QPushButton('Обзор', self)
        self.initUI()

    def click_browse(self):  # Обработка нажатия на кнопку 'browse'
        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите папку')
        self.edt1.setText(str(folderpath).replace('/', "\\"))

    def click_next(self):  # Обработка нажатия на кнопку 'next'
        global Gkey
        try:
            if self.edt1.text():
                # Создание окна с задаванием ключа
                q = QInputDialog()
                text, ok = q.getText(self, 'Придумайте пароль',
                                                'Введите:')
                if ok and text:
                    Gkey = text
                else:
                    q.close()
                ha = hash_code(Gkey)  # В базе данных будет храниться hash от ключа шифрования
                if ha and Gkey != '':
                    if "\\" in self.edt1.text():  # Проверка, что введённая строка это путь
                        try:
                            d = Database()  # Инициализация класса базы данных
                            d.create_database_(ha, self.edt1.text())
                            d.create_notes(self.edt1.text())
                            d.create_settings(self.edt1.text())
                            notify(Gkey, 'Remember your key!')  # Уведомляем пользователя, чтобы он запомнил свой ключ

                            self.close()  # Закрываем окно
                            self.wm = MainWindow()  # Открываем основное окно
                            self.wm.show()
                        except sqlite3.Error as error:
                            pass
                    else:
                        notify('Probably your destination folder path is wrong!', 'Attention!')
            else:
                notify('Check the input line', 'Error!')
        except AttributeError:
            pass

    def initUI(self):  # Инициализация окна регистрации
        self.setGeometry(100, 100, 800, 620)  # Размеры окна
        self.setWindowTitle('PyNote')
        self.setWindowIcon(QIcon('pynote.png'))
        lbl1 = QLabel('PyNote', self)
        lbl1.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # Выравнивание по горизонтали
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(45)  # Размер шрифта
        lbl1.setFont(font)
        lbl2 = QLabel('Давайте начнём! Введите путь папки назначения:')
        lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Выравнивание по центру

        layout = QFormLayout(self)
        layout.addWidget(lbl1)
        layout.addWidget(lbl2)
        l2 = QHBoxLayout(self)
        l2.addWidget(self.edt1)
        l2.addWidget(self.btn2)
        l2.addWidget(self.btn)
        layout.addItem(l2)
        self.btn2.clicked.connect(lambda: self.click_browse())  # Добавление слушателя на кнопку 'browse'
        self.btn.clicked.connect(lambda: self.click_next())  # Добавление слушателя на кнопку 'next'


class MainWindow(QWidget):  # Основное окно
    def __init__(self):
        super().__init__()
        global app
        self.database = Database()
        self.create_note = QPushButton('Создать заметку', self)  # Создание кнопки 'Create note'
        self.create_note.clicked.connect(lambda: self.click_plus())
        self.create_note.setIcon(QIcon('plus.png'))

        self.go_settings = QPushButton('Настройки', self)  # Создание кнопки 'Settings'
        self.go_settings.clicked.connect(lambda: self.click_settings())
        self.go_settings.setIcon(QIcon('settings.png'))

        self.search = QLineEdit(self)
        self.search.setPlaceholderText('Найти...')
        font = QtGui.QFont()
        font.setPointSize(12)  # Размер шрифта
        self.search.setFont(font)
        self.lis = QListWidget()  # Основной список со всеми заметками
        font.setPointSize(16)
        self.lis.setFont(font)

        main_sp = self.database.get_all_notes()
        self.base_sp = []
        for i in range(len(main_sp)):
            if main_sp[i][2] == 'EMPTY':
                e = str(Cipher().decrypt(main_sp[i][1], Gkey))[:102] + '\n'
                self.base_sp.append(str(main_sp[i][0]) + "    " +
                                    e[:e.index('\n')])
            else:
                self.base_sp.append(str(main_sp[i][0]) + "P" + "   " + "ENCRYPTED")
        self.lis.addItems(self.base_sp)
        self.lis.itemDoubleClicked.connect(self.click_item)
        self.lis.itemClicked.connect(self.choose_item)
        self.grid = QGridLayout()

        self.setFocus()  # Устанавливаем фокус на окне, это понадобится для обновления списка заметок
        app.focusChanged.connect(lambda: self.update_sp())

        self.shortcut_delete = QShortcut(QKeySequence('Del'), self)  # Сочетание клавиш для удаления заметки

        self.lis.installEventFilter(self)
        self.search.textChanged.connect(lambda: self.search_sp())
        self.initUI()

    def search_sp(self):  # Поиск по списку заметок
        n_sp = list(filter(lambda x: self.search.text() in x, self.base_sp))
        self.lis.clear()
        self.lis.addItems(n_sp)

    def eventFilter(self, source, event):
        global open_or_delete
        if event.type() == event.Type.ContextMenu and source is self.lis:
            menu = QMenu()

            open_action = QAction('Открыть', self)
            open_action.triggered.connect(lambda: self.open_note())

            delete_action = QAction('Удалить', self)
            delete_action.triggered.connect(lambda: self.delete_action())

            menu.addAction(open_action)
            menu.addSeparator()  # Разделитель
            menu.addAction(delete_action)
            if menu.exec(event.globalPos()):
                item = source.itemAt(event.pos())
                if open_or_delete == 0:  # Если пользователь выбрал open
                    self.click_item(item)
                elif open_or_delete == 1:  # Если пользователь выбрал delete
                    text = item.text()
                    index = text[0:text.find("  ")]
                    if 'P' in index:
                        num = int(index[0:index.find('P')])
                    else:
                        num = int(index)
                    self.delete_note(num)
            return True
        return super().eventFilter(source, event)

    def open_note(self):
        global open_or_delete
        open_or_delete = 0

    def delete_action(self):
        global open_or_delete
        open_or_delete = 1

    def update_sp(self, update_forcibly=False):  # Функция для обновления списка заметок
        if self.isActiveWindow() and (self.search.text() == '' or update_forcibly):
            main_sp = self.database.get_all_notes()
            self.base_sp = []
            for i in range(len(main_sp)):
                if main_sp[i][2] == 'EMPTY':
                    e = str(Cipher().decrypt(str(main_sp[i][1]), Gkey))[:102] + '\n'
                    self.base_sp.append(str(main_sp[i][0]) + "    " +
                                        e[:e.index('\n')])
                else:
                    self.base_sp.append(str(main_sp[i][0]) + "P" + "   " + "ENCRYPTED")
            self.lis.clear()
            self.lis.addItems(self.base_sp)

    def choose_item(self, item):
        text = item.text()
        index = text[0:text.find("  ")]
        if 'P' in index:
            num = int(index[0:index.find('P')])
        else:
            num = int(index)
        self.shortcut_delete.setKey(0)  # Очищаем очередь, чтобы функция не вызывалась несколько раз
        self.shortcut_delete = QShortcut(QKeySequence('Del'), self)  # Сочетание клавиш для удаления заметки
        self.shortcut_delete.activated.connect(lambda: self.delete_note(num))

    def click_item(self, item):  # Обработка нажатий на элемент списка
        text: str = item.text()
        index = text[0:text.find("  ")]
        if 'P' in index:
            num = int(index[0:index.find('P')])
            dialog = ConfirmPasswordForNoteInputDialog(labels=['Подтвердите пароль'],
                                                       number=num)
            dialog.exec()
            if GNote != '':
                self.note = Note(initial_text=Cipher()
                                 .decrypt(self.database.get_encrypted_text_note(num)[0], GNote),
                                 initial_number=num, editing=True, password=GNote)
                self.note.show()
                self.search.setText('')  # Очищаем поисковую строку для обновления списка
        else:
            self.note = Note(initial_text=Cipher().
                             decrypt(self.database.get_encrypted_text_note(int(index))[0], Gkey),
                             initial_number=int(index), editing=True, password=Gkey)
            self.note.show()
            self.search.setText('')  # Очищаем поисковую строку для обновления списка

    def initUI(self):  # Инициализация основного окна
        w, h = list(map(int, Database().get_resolution_main().split('x')))
        self.setGeometry(0, 0, w, h)
        self.setWindowTitle('PyNote: Главный экран')
        self.setWindowIcon(QIcon('pynote.png'))

        self.grid.setSpacing(10)  # Отступы
        self.grid.addWidget(self.create_note, 0, 0)
        self.grid.addWidget(self.go_settings, 2, 0)
        self.grid.addWidget(self.search, 0, 1)
        self.grid.addWidget(self.lis, 1, 1)

        self.setLayout(self.grid)

    def click_plus(self):
        self.note = Note()
        self.note.show()
        self.search.setText('')  # Очищаем поисковую строку для обновления списка

    def delete_note(self, number):
        Database().delete_note(number)
        self.update_sp(update_forcibly=True)

    def click_settings(self):
        self.settings = Settings()
        self.settings.show()


class Settings(QWidget):  # Окно настроек
    def __init__(self):
        super().__init__()
        self.database = Database()
        font = QtGui.QFont()
        font.setPointSize(14)  # Размер шрифта
        self.resolutions = ['320x200', '640x480', '800x600', '1024x768', '1366x768',
                            '1280x1024', '1600x1200', '1920x1080', '2560x1600']
        self.change_resolution_main = QLabel()
        self.change_resolution_main.setFont(font)
        self.change_resolution_main.setText('Разрешение главного окна')

        self.change_resolution_main_combo = QComboBox()
        self.change_resolution_main_combo.setFont(font)
        self.change_resolution_main_combo.setPlaceholderText(self.database.get_resolution_main())  # предпросмотр
        self.change_resolution_main_combo.addItems(self.resolutions)  # Добавление списка разрешений в выпадающее окно
        self.change_resolution_main_combo.currentIndexChanged.connect(self.index_changed_main)  # Слушатель изменений

        self.change_resolution_note = QLabel()
        self.change_resolution_note.setFont(font)
        self.change_resolution_note.setText('Разрешение окна заметок')

        self.change_resolution_note_combo = QComboBox()
        self.change_resolution_note_combo.setFont(font)
        self.change_resolution_note_combo.setPlaceholderText(self.database.get_resolution_note())  # предпросмотр
        self.change_resolution_note_combo.addItems(self.resolutions)
        self.change_resolution_note_combo.currentIndexChanged.connect(self.index_changed_note)

        self.new_password = QLabel()
        self.new_password.setFont(font)
        self.new_password.setText('Новый пароль для каждой новой заметки')

        self.check = QCheckBox()
        self.check.setFont(font)
        if self.database.get_new_key_for_new_note() == 1:
            self.check.setCheckState(Qt.CheckState.Checked)
        self.check.stateChanged.connect(self.show_activity)

        self.ask_pass = QLabel()
        self.ask_pass.setFont(font)
        self.ask_pass.setText('Спрашивать ключ при входе')

        self.ask_button = QPushButton()
        self.ask_button.setFont(font)
        if self.database.get_ask_key() == 0:
            self.ask_button.setText('Нет')
        else:
            self.ask_button.setText('Да')
        self.ask_button.clicked.connect(lambda: self.click_ask())
        self.initUI()

    def initUI(self):
        self.setGeometry(50, 100, 800, 600)
        self.setWindowTitle('PyNote: Настройки')
        self.setWindowIcon(QIcon('pynote.png'))

        vertical = QVBoxLayout()

        h1 = QHBoxLayout()
        h1.addWidget(self.change_resolution_main)
        h1.addWidget(self.change_resolution_main_combo)

        h2 = QHBoxLayout()
        h2.addWidget(self.change_resolution_note)
        h2.addWidget(self.change_resolution_note_combo)

        h3 = QHBoxLayout()
        h3.addWidget(self.new_password)
        h3.addWidget(self.check)

        h4 = QHBoxLayout()
        h4.addWidget(self.ask_pass)
        h4.addWidget(self.ask_button)

        vertical.addLayout(h1)
        vertical.addLayout(h2)
        vertical.addLayout(h3)
        vertical.addLayout(h4)

        self.setLayout(vertical)

    def index_changed_main(self, i):
        w, h = list(map(int, self.resolutions[i].split('x')))
        self.database.set_resolution_main(w, h)

    def index_changed_note(self, i):
        w, h = list(map(int, self.resolutions[i].split('x')))
        self.database.set_resolution_note(w, h)

    def show_activity(self, s):
        if s == 2:
            self.database.set_new_key_for_new_note(1)
        else:
            self.database.set_new_key_for_new_note(0)

    def click_ask(self):
        if self.ask_button.text() == 'Нет':
            self.database.set_aks_key(1)
            file = open('key.txt', 'w+')
            file.write('')
            file.close()
            self.ask_button.setText('Да')
        elif self.ask_button.text() == 'Да':
            dialog = AreYouSureInputDialog(labels=['Введите пароль повторно'])
            dialog.exec()
            self.ask_button.setText('Нет')


font = QtGui.QFont('Courier New')
font_size = 14


class Note(QMainWindow):  # Окно создания / редактирования заметки
    def __init__(self, initial_text='', initial_number=-1, editing=False, password=''):
        global font, font_size
        super().__init__()
        self.initUI()
        self.previous_text = ''
        self.password = password
        self.editing = editing
        Database().listener()
        if initial_number == -1:
            self.g_number = Database().get_count_notes()
        else:
            self.g_number = initial_number
        self.layout = QFormLayout()
        self.line = QTextEdit(self)
        self.line.setText(initial_text)
        self.label = self.line.toPlainText()[0:16]
        if self.label != '':
            self.setWindowTitle(f'PyNote: {self.label} (Сохранено)')

        self.line.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                                                      QtWidgets.QSizePolicy.Policy.MinimumExpanding))
        font.setPointSize(font_size)  # Размер шрифта
        self.line.setFont(font)
        button_action = QAction("Сохранить                     CTRL+S", self)  # Создание кнопки в меню
        button_action.triggered.connect(lambda: self.click_save())  # Обработка нажатия
        self.shortcut_save = QShortcut(QKeySequence('Ctrl+s'), self)  # Сочетание клавиш на сохранение
        self.shortcut_save.activated.connect(lambda: self.click_save())

        button_action2 = QAction('Сохранить как... CTRL+SHIFT+S', self)  # Создание второй кнопки в меню
        button_action2.triggered.connect(lambda: self.click_save_as())  # Обработка нажатия
        self.shortcut_saveAs = QShortcut(QKeySequence('Ctrl+Shift+s'), self)  # Сочетание клавиш на сохранение как
        self.shortcut_saveAs.activated.connect(lambda: self.click_save_as())

        button_action3 = QAction('Выйти без сохранения', self)
        button_action3.triggered.connect(lambda: self.exit_w_s())

        scale_b1 = QAction('Приблизить                                CTRL+Up', self)
        scale_b1.triggered.connect(lambda: self.zoom_in())
        self.shortcut_zIn = QShortcut(QKeySequence('Ctrl+Up'), self)  # Сочетание клавиш на увеличение текста
        self.shortcut_zIn.activated.connect(lambda: self.zoom_in())

        scale_b2 = QAction('Отдалить                                    CTRL+Down', self)
        scale_b2.triggered.connect(lambda: self.zoom_out())
        self.shortcut_zOut = QShortcut(QKeySequence('Ctrl+Down'), self)  # Сочетание клавиш на уменьшение текста
        self.shortcut_zOut.activated.connect(lambda: self.zoom_out())

        scale_default = QAction('Вернуть приближение по умолчанию     CTRL+0', self)
        scale_default.triggered.connect(lambda: self.zoom_default())
        self.shortcut_zD = QShortcut(QKeySequence('Ctrl+0'), self)  # Сочетание клавиш для размера текста по умолчанию
        self.shortcut_zD.activated.connect(lambda: self.zoom_default())

        self.menu = self.menuBar()  # Инициализация меню
        file_menu = self.menu.addMenu("Файл")  # Название в меню
        zoom = self.menu.addMenu('Приближение')
        other = self.menu.addMenu('Другое')

        file_menu.addAction(button_action)
        file_menu.addAction(button_action2)
        file_menu.addSeparator()
        file_menu.addAction(button_action3)

        zoom.addAction(scale_b1)
        zoom.addAction(scale_b2)
        zoom.addSeparator()
        zoom.addAction(scale_default)

        self.setCentralWidget(self.line)

        self.shortcut_csv = QShortcut(QKeySequence('Ctrl+shift+v'), self)  # Вставка csv таблиц
        self.shortcut_csv.activated.connect(lambda: self.parse_csv())

        other_action = QAction('Встать csv таблицу              Ctrl+Shift+V', self)
        other_action.triggered.connect(lambda: self.parse_csv())
        other.addAction(other_action)

        self.line.textChanged.connect(lambda: self.change_text())

    def click_save(self):  # Функция обработки нажатия save
        if not self.editing:
            if self.previous_text == '' and self.previous_text != self.line.toPlainText():
                if Database().get_new_key_for_new_note() == 1:
                    dialog = GeneratePasswordForNoteInputDialog(labels=["Придумайте пароль"])
                    dialog.exec()
                    Database().new_note(self.line.toPlainText(), GNote)
                else:
                    Database().new_note(self.line.toPlainText())
            else:
                Database().update_note(self.g_number, self.line.toPlainText())
        else:  # Сохранение в режиме редактирования
            Database().update_note_in_mode_editing(self.g_number, text=Cipher()
                                                   .encrypt(self.line.toPlainText(), self.password))

        self.previous_text = self.line.toPlainText()
        self.label = self.line.toPlainText()[0:16]
        self.setWindowTitle(f'PyNote: {self.label} (Сохранено)')

    def click_save_as(self):  # Функция обработки нажатия save as
        try:
            file = QtWidgets.QFileDialog.getSaveFileName(None, 'Сохранить', '/', "Текстовые файлы (*.txt)")
            text = self.line.toPlainText()
            if file[0]:
                with open(file[0], 'w', encoding='utf-8') as file:
                    file.write(text)
            self.close()
        except BaseException as e:
            print(e)


    def exit_w_s(self):
        self.close()

    def zoom_in(self):
        global font, font_size
        font_size += 2
        font.setPointSize(font_size)  # Размер шрифта
        self.line.setFont(font)

    def zoom_out(self):
        global font, font_size
        font_size -= 2
        font.setPointSize(font_size)  # Размер шрифта
        self.line.setFont(font)

    def zoom_default(self):
        global font, font_size
        font_size = 14
        font.setPointSize(font_size)  # Размер шрифта
        self.line.setFont(font)

    def parse_csv(self):
        try:
            text = Tk().clipboard_get()
            try:
                sp = [re.split(';;|;|,|;;;', i) for i in text.split('\n')]  # Разбиение csv на массивы
                max_len = sorted([len(i) for i in sp])[-1]  # Проверка максимальной длины для каждой строки стобца
                for i in sp:
                    if len(i) != max_len:
                        for t in range(max_len - len(i)):
                            i.append('')
                le = [max([len(i) for i in list(col)]) for col in
                      zip(*sp)]  # Нахождение максимальной длины в повёрнутом списке
                separator = '-' * (sum(le) + len(le)) + "\n"
                save = separator
                k = 0
                for i in sp:
                    for w in range(len(i)):
                        save += i[w] + " " * (le[w] - len(i[w])) + "|"
                    if k != (len(sp) - 1):
                        save += "\n" + separator
                    k += 1
                save += '\n' + '-' * (sum(le) + len(le)) + "\n"
                self.line.append(save)
            except BaseException:
                self.line.append(text)
        except BaseException:
            pass


    def change_text(self):
        if self.label != '':
            self.setWindowTitle(f'PyNote: {self.label} (Изменения не сохранены)')
        else:
            self.setWindowTitle('PyNote: Объект (Не сохранено)')

    def initUI(self):
        w, h = list(map(int, Database().get_resolution_note().split('x')))
        self.setGeometry(0, 0, w, h)
        self.setWindowTitle('PyNote: Объект')
        self.setWindowIcon(QIcon('pynote.png'))


app = QApplication(sys.argv)  # Инициализация приложения | глобальная переменная требуется для focusChanged


def main():
    global GEnter, Gkey, app
    if not (Database().exist_database_() and Database().exist_notes()):  # Проверка на существование базы данных
        ex = Example()
        ex.show()
    else:
        Database().listener()  # Проверка на существование базы данных, открывает маленькое окно
        if Database().get_ask_key() == 1:
            confirm()  # Проверка пароля
        else:
            f = open('key.txt')
            Gkey = f.read()
            f.close()
        if GEnter:
            mw = MainWindow()  # Запуск основного окна
            mw.show()
        else:
            app.closeAllWindows()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()  # Запуск приложения
