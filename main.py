import sys
import re
import os
import sqlite3
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction, QShortcut, QKeySequence
from PyQt6.QtWidgets import *
from tkinter import Tk
from CIPHER import Cipher
import string
import random

import hashlib

Gkey = ''  # Временная переменная для хранения ключа шифрования
GEnter = True  # Переменная отвечающая за закрытие основного окна при неподтверждении пароля
GNote = ''  # Временная переменная для хранения ключа шифрования для отдельной заметки
open_or_delete = -1  # Временная переменная для menu в Main | 0 -> open | 1 -> delete


def hash_code(key):
    m = hashlib.md5()
    m.update(bytes(key, 'utf-8'))
    return str(m.hexdigest())


def confirm():  # Проверка пароля
    global GEnter
    if Database().get_ask_key() == 1:
        n = Database().get_language()
        if n == 0:
            p1 = 'Password:'
        elif n == 1 or n == 2 or n == 3 or n == 5:
            p1 = 'Пароль:'
        else:
            p1 = 'Серсүз:'
        dialog = ConfirmPasswordInputDialog(labels=[p1])
        if not dialog.exec() and not Gkey:
            GEnter = False
            dialog.close()


def get_name_by_num_lang(number):  # Получить название языка по номеру
    if number == 0:
        return 'English'
    elif number == 1:
        return 'Русский язык'
    elif number == 2:
        return 'Беларуская мова'
    elif number == 3:
        return 'Удмурт кыл'
    elif number == 4:
        return 'Татар теле'
    elif number == 5:
        return 'Башҡорт теле'
    else:
        return 'Unknown number in database'


class Example(QWidget):  # Стартовое окно
    def __init__(self):
        super().__init__()
        self.edt1 = QLineEdit('', self)
        self.edt1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.edt1.setContentsMargins(10, 0, 10, 0)
        self.btn = QPushButton('Начать!', self)
        self.btn2 = QPushButton('Обзор', self)

        self.lan = 1
        self.languages = ['English', 'Русский язык', 'Беларуская мова', 'Удмурт кыл', 'Татар теле', 'Башҡорт теле']
        self.change_languages = QComboBox()
        self.change_languages.setFont(font)
        self.change_languages.setPlaceholderText('Русский язык')
        self.change_languages.addItems(self.languages)
        self.change_languages.currentIndexChanged.connect(self.index_changed)
        self.change_languages.setMaximumWidth(150)

        self.initUI()

    def index_changed(self, i):
        self.lan = i
        if self.lan == 0:
            self.btn.setText('Start!')
            self.btn2.setText('Browse')
            self.lbl2.setText("Let's get started! Enter the path of the destination folder:")
        elif self.lan == 1:
            self.btn.setText('Начать!')
            self.btn2.setText('Обзор')
            self.lbl2.setText('Давайте начнём! Введите путь папки назначения:')
        elif self.lan == 2:
            self.btn.setText('Пачаць!')
            self.btn2.setText('Агляд')
            self.lbl2.setText('Давайце пачнем! Увядзіце шлях тэчкі прызначэння:')
        elif self.lan == 3:
            self.btn.setText('Кутске!')
            self.btn2.setText('Обзор')
            self.lbl2.setText("Вай кутске! Сюресэ пыро назначение папка:")
        elif self.lan == 4:
            self.btn.setText('Башлау!')
            self.btn2.setText('Гомуми күзәтү')
            self.lbl2.setText('әйдәгез башлыйк! Максат папкасы юлын кертегез:')
        elif self.lan == 5:
            self.btn.setText('Башларға!')
            self.btn2.setText('Күҙәтеү')
            self.lbl2.setText('әйҙәгеҙ, башлайыҡ! Папканың тәғәйенләнеше юлын индерегеҙ')

    def click_browse(self):  # Обработка нажатия на кнопку 'browse'
        if self.lan == 1:
            folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите папку')
        elif self.lan == 0:
            folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the folder')
        elif self.lan == 2:
            folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Абярыце тэчку')
        elif self.lan == 3:
            folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Папкае быръе')
        elif self.lan == 4:
            folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Папканы сайлагыз')
        else:
            folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Папканы һайлағыҙ')
        self.edt1.setText(str(folderpath).replace('/', "\\"))

    def click_next(self):  # Обработка нажатия на кнопку 'next'
        global Gkey
        try:
            if self.edt1.text():
                # Создание окна с задаванием ключа
                q = QInputDialog()
                if self.lan == 0:
                    text, ok = q.getText(self, 'Think of a password',
                                         'Enter:')
                elif self.lan == 1:
                    text, ok = q.getText(self, 'Придумайте пароль',
                                         'Введите:')
                elif self.lan == 2:
                    text, ok = q.getText(self, 'Прыдумайце пароль', 'Увядзіце:')
                elif self.lan == 3:
                    text, ok = q.getText(self, 'Пароль малпам', 'Пыро:')
                elif self.lan == 4:
                    text, ok = q.getText(self, 'Серсүз уйлап табыгыз', 'Языгыз:')
                else:
                    text, ok = q.getText(self, 'Пароль уйлап табығыҙ', 'Индерегеҙ:')
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
                            d.create_settings(self.edt1.text(), self.lan)

                            self.close()  # Закрываем окно
                            self.wm = MainWindow()  # Открываем основное окно
                            self.wm.show()
                        except sqlite3.Error as error:
                            pass
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
        v = QVBoxLayout(self)
        lbl1.setFont(font)

        self.lbl2 = QLabel('Давайте начнём! Введите путь папки назначения:')
        self.lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Выравнивание по центру

        layout = QFormLayout(self)
        v.addLayout(layout)
        layout.addWidget(lbl1)
        layout.addWidget(self.lbl2)
        l2 = QHBoxLayout(self)
        l2.addWidget(self.edt1)
        l2.addWidget(self.btn2)
        l2.addWidget(self.btn)
        layout.addItem(l2)
        layout.setSpacing(25)
        v.addWidget(self.change_languages)
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

        self.open = 'Открыть'
        self.delete = 'Удалить'

        self.setFocus()  # Устанавливаем фокус на окне, это понадобится для обновления списка заметок
        app.focusChanged.connect(lambda: self.update_sp())

        self.shortcut_delete = QShortcut(QKeySequence('Del'), self)  # Сочетание клавиш для удаления заметки

        self.lis.installEventFilter(self)
        self.search.textChanged.connect(lambda: self.search_sp())
        self.initUI()

    def changed_lan(self, number):
        if number == 0:
            self.create_note.setText('Create a note')
            self.go_settings.setText('Settings')
            self.search.setPlaceholderText('Search...')
            self.setWindowTitle('PyNote: Main window')
            self.open = 'Open'
            self.delete = 'Delete'
        elif number == 1:
            self.create_note.setText('Создать заметку')
            self.go_settings.setText('Настройки')
            self.search.setPlaceholderText('Найти...')
            self.setWindowTitle('PyNote: Главный экран')
            self.open = 'Открыть'
            self.delete = 'Удалить'
        elif number == 2:
            self.create_note.setText('Стварыць нататку')
            self.go_settings.setText('Налады')
            self.search.setPlaceholderText('Знайсці...')
            self.setWindowTitle('PyNote: Галоўны экран')
            self.open = 'Адкрыць'
            self.delete = 'Выдаліць'
        elif number == 3:
            self.create_note.setText('Заметка кылдыт')
            self.go_settings.setText('Настройкаосыз')
            self.search.setPlaceholderText('Шедьтыны...')
            self.setWindowTitle('PyNote: Валтӥсь экран')
            self.open = 'Усьтыны'
            self.delete = 'Кошкыны'
        elif number == 4:
            self.create_note.setText('Искәрмә ясау')
            self.go_settings.setText('Көйләүләр')
            self.search.setPlaceholderText('Табарга...')
            self.setWindowTitle('PyNote: төп экран')
            self.open = 'Ачу'
            self.delete = 'Бетерү'
        elif number == 5:
            self.create_note.setText('Билдә яһау')
            self.go_settings.setText('Көйләүҙәр')
            self.search.setPlaceholderText('Табырға...')
            self.setWindowTitle('PyNote: Төп экран')
            self.open = 'Асыу'
            self.delete = 'Алып ташлау'

    def search_sp(self):  # Поиск по списку заметок
        n_sp = list(filter(lambda x: self.search.text() in x, self.base_sp))
        self.lis.clear()
        self.lis.addItems(n_sp)

    def eventFilter(self, source, event):
        global open_or_delete
        if event.type() == event.Type.ContextMenu and source is self.lis:
            menu = QMenu()

            open_action = QAction(self.open, self)
            open_action.triggered.connect(lambda: self.open_note())

            delete_action = QAction(self.delete, self)
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
        self.changed_lan(self.database.get_language())
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
            n = self.database.get_language()
            if n == 0:
                p1 = 'Confirm password'
            elif n == 1:
                p1 = 'Подтвердите пароль'
            elif n == 2:
                p1 = 'Пацвердзіце пароль'
            elif n == 3:
                p1 = 'Пароль юнматэ'
            elif n == 4:
                p1 = 'Серсүзне раслагыз'
            else:
                p1 = 'Текстың йөкмәткеһен асыҡлау'
            dialog = ConfirmPasswordForNoteInputDialog(labels=[p1],
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
            self.ask_button.setText('✖')
        else:
            self.ask_button.setText('✔')
        self.ask_button.clicked.connect(lambda: self.click_ask())

        self.languages = ['English', 'Русский язык', 'Беларуская мова', 'Удмурт кыл', 'Татар теле', 'Башҡорт теле']
        self.change_lan = QComboBox()
        self.change_lan.setFont(font)
        self.change_lan.setPlaceholderText(get_name_by_num_lang(self.database.get_language()))  # предпросмотр
        self.change_lan.addItems(self.languages)  # Добавление списка разрешений в выпадающее окно
        self.change_lan.currentIndexChanged.connect(self.index_changed_lan)
        self.index_changed_lan(self.database.get_language())
        self.again = 'Введите пароль повторно'
        self.initUI()

    def index_changed_lan(self, i):
        self.database.set_language(i)
        if i == 0:
            self.setWindowTitle('PyNote: Settings')
            self.ask_pass.setText('Ask for key on login')
            self.new_password.setText('New password for each new note')
            self.change_resolution_note.setText('Resolve note window')
            self.change_resolution_main.setText('Main window resolution')
            self.again = 'Re-enter the password'
        elif i == 1:
            self.setWindowTitle('PyNote: Настройки')
            self.ask_pass.setText('Спрашивать ключ при входе')
            self.new_password.setText('Новый пароль для каждой новой заметки')
            self.change_resolution_note.setText('Разрешение окна заметок')
            self.change_resolution_main.setText('Разрешение главного окна')
            self.again = 'Введите пароль повторно'
        elif i == 2:
            self.setWindowTitle('PyNote: Налады')
            self.ask_pass.setText('ключ Пытацца пры ўваходзе')
            self.new_password.setText('Новы пароль для кожнай новай нататкі')
            self.change_resolution_note.setText('Дазвол вокны нататак')
            self.change_resolution_main.setText('Дазвол галоўнага акна')
            self.again = 'Паўторна увядзіце пароль'
        elif i == 3:
            self.setWindowTitle('PyNote: Настройкаосыз')
            self.ask_pass.setText('Усьтон юа пырон дыр')
            self.new_password.setText("Выль котькуд выль пароль заметкаос")
            self.change_resolution_note.setText('Юаське укноез заметкаос')
            self.change_resolution_main.setText('Юаське валтӥсь укноез')
            self.again = 'Кайта пароленыд пыриськод'
        elif i == 4:
            self.setWindowTitle('PyNote: Көйләүләр')
            self.ask_pass.setText('Сорарга ачкыч кергәндә')
            self.new_password.setText('һәр яңа язма өчен яңа серсүз')
            self.change_resolution_note.setText('Искәрмәләр тәрәзәсе резолюциясе')
            self.change_resolution_main.setText('Төп тәрәзә резолюциясе')
            self.again = 'Серсүзне кабат языгыз'
        else:
            self.setWindowTitle('PyNote: Көйләүҙәр')
            self.ask_pass.setText('Ингәндә асҡысты һорағыҙ')
            self.new_password.setText('Һәр яңы мәҡәлә өсөн яңы мәҡәлә')
            self.change_resolution_note.setText('Тәҙрәләрҙең рөхсәте')
            self.change_resolution_main.setText('Төп тәҙрә рөхсәте')
            self.again = 'Һүҙҙе ҡабатлау'

    def initUI(self):
        self.setGeometry(50, 100, 800, 600)
        # self.setWindowTitle('PyNote: Настройки')
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
        vertical.addWidget(self.change_lan)

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
        if self.ask_button.text() == '✖':
            self.database.set_aks_key(1)
            file = open('key.txt', 'w+')
            file.write('')
            file.close()
            self.ask_button.setText('✔')
        elif self.ask_button.text() == '✔':
            dialog = AreYouSureInputDialog(labels=[self.again])
            dialog.exec()
            self.ask_button.setText('✖')


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
        self.button_action = QAction("Сохранить                     CTRL+S", self)  # Создание кнопки в меню
        self.button_action.triggered.connect(lambda: self.click_save())  # Обработка нажатия
        self.shortcut_save = QShortcut(QKeySequence('Ctrl+s'), self)  # Сочетание клавиш на сохранение
        self.shortcut_save.activated.connect(lambda: self.click_save())

        self.button_action2 = QAction('Сохранить как... CTRL+SHIFT+S', self)  # Создание второй кнопки в меню
        self.button_action2.triggered.connect(lambda: self.click_save_as())  # Обработка нажатия
        self.shortcut_saveAs = QShortcut(QKeySequence('Ctrl+Shift+s'), self)  # Сочетание клавиш на сохранение как
        self.shortcut_saveAs.activated.connect(lambda: self.click_save_as())

        self.button_action3 = QAction('Выйти без сохранения', self)
        self.button_action3.triggered.connect(lambda: self.exit_w_s())

        self.scale_b1 = QAction('Приблизить                                CTRL+Up', self)
        self.scale_b1.triggered.connect(lambda: self.zoom_in())
        self.shortcut_zIn = QShortcut(QKeySequence('Ctrl+Up'), self)  # Сочетание клавиш на увеличение текста
        self.shortcut_zIn.activated.connect(lambda: self.zoom_in())

        self.scale_b2 = QAction('Отдалить                                    CTRL+Down', self)
        self.scale_b2.triggered.connect(lambda: self.zoom_out())
        self.shortcut_zOut = QShortcut(QKeySequence('Ctrl+Down'), self)  # Сочетание клавиш на уменьшение текста
        self.shortcut_zOut.activated.connect(lambda: self.zoom_out())

        self.scale_default = QAction('Вернуть приближение по умолчанию     CTRL+0', self)
        self.scale_default.triggered.connect(lambda: self.zoom_default())
        self.shortcut_zD = QShortcut(QKeySequence('Ctrl+0'), self)  # Сочетание клавиш для размера текста по умолчанию
        self.shortcut_zD.activated.connect(lambda: self.zoom_default())

        n = Database().get_language()
        file = "Файл"
        z = 'Приближение'
        o = 'Другое'
        if n == 0:
            file = 'File'
            z = 'Zoom'
            o = 'Other'
        elif n == 2:
            z = 'Набліжэнне'
        elif n == 3:
            z = 'Матэктон'
            o = 'Мукет'
        elif n == 4:
            z = 'Якынлашу'
            o = 'Башка'
        elif n == 5:
            z = 'Яҡынлашыуы'
            o = 'Башҡа'
        self.menu = self.menuBar()  # Инициализация меню
        file_menu = self.menu.addMenu(file)  # Название в меню
        zoom = self.menu.addMenu(z)
        other = self.menu.addMenu(o)

        file_menu.addAction(self.button_action)
        file_menu.addAction(self.button_action2)
        file_menu.addSeparator()
        file_menu.addAction(self.button_action3)

        zoom.addAction(self.scale_b1)
        zoom.addAction(self.scale_b2)
        zoom.addSeparator()
        zoom.addAction(self.scale_default)

        self.setCentralWidget(self.line)

        self.shortcut_csv = QShortcut(QKeySequence('Ctrl+shift+v'), self)  # Вставка csv таблиц
        self.shortcut_csv.activated.connect(lambda: self.parse_csv())

        self.other_action = QAction('Встать csv таблицу              Ctrl+Shift+V', self)
        self.other_action.triggered.connect(lambda: self.parse_csv())
        other.addAction(self.other_action)

        self.line.textChanged.connect(lambda: self.change_text())

        app.focusChanged.connect(lambda: self.changed_index_lan(Database().get_language()))  # Устанавливаем фокус для перевода

    def changed_index_lan(self, i):
        Database().set_language(i)
        if i == 0:
            if self.label != '':
                self.setWindowTitle(f'PyNote: {self.label} (Saved)')
            self.button_action.setText('Save                          CTRL+S')
            self.button_action2.setText('Save as...       CTRL+SHIFT+S')
            self.button_action3.setText('Exit without save')
            self.scale_b1.setText('Zoom in                                   CTRL+Up')
            self.scale_b2.setText('Zoom out                           CTRL+Down')
            self.scale_default.setText('Restore default scale                CTRL+0')
            self.other_action.setText('Insert csv table                Ctrl+Shift+V')
        elif i == 1:
            if self.label != '':
                self.setWindowTitle(f'PyNote: {self.label} (Сохранено)')
            self.button_action.setText('Сохранить                     CTRL+S')
            self.button_action2.setText('Сохранить как... CTRL+SHIFT+S')
            self.button_action3.setText('Выйти без сохранения')
            self.scale_b1.setText('Приблизить                                CTRL+Up')
            self.scale_b2.setText('Отдалить                                    CTRL+Down')
            self.scale_default.setText('Вернуть приближение по умолчанию     CTRL+0')
            self.other_action.setText('Встать csv таблицу              Ctrl+Shift+V')
        elif i == 2:
            if self.label != '':
                self.setWindowTitle(f'PyNote: {self.label} (Захавана)')
            self.button_action.setText('Захаваць\t\t\tCTRL+S')
            self.button_action2.setText('Захаваць як...\t\t\tCTRL+SHIFT+S')
            self.button_action3.setText('Выйсці без захавання')
            self.scale_b1.setText('Наблізіць\t\t\tCTRL+Up')
            self.scale_b2.setText('Аддаліць\t\t\tCTRL+Down')
            self.scale_default.setText('Вярнуць набліжэнне па змаўчанні\t\t\tCTRL+0')
            self.other_action.setText('Устаць csv табліцу\t\t\tCtrl+Shift+V')
        elif i == 3:
            if self.label != '':
                self.setWindowTitle(f'PyNote: {self.label} (Утьыны)')
            self.button_action.setText('Утьыны                     CTRL+S')
            self.button_action2.setText('Кызьы утёно... CTRL+SHIFT+S')
            self.button_action3.setText('Утёнъя сотэк потӥз')
            self.scale_b1.setText('Матэктэ                                CTRL+Up')
            self.scale_b2.setText('Висъяны                                    CTRL+Down')
            self.scale_default.setText('Матэгес вуэмез бере берыктыны умолчание     CTRL+0')
            self.other_action.setText('Таблицаосын султо csv              Ctrl+Shift+V')
        elif i == 4:
            if self.label != '':
                self.setWindowTitle(f'PyNote: {self.label} (Сакланган)')
            self.button_action.setText('Саклау                     CTRL+S')
            self.button_action2.setText('Ничек сакларга... CTRL+SHIFT+S')
            self.button_action3.setText('Сакланмыйча чыгу')
            self.scale_b1.setText('Якынайту                                CTRL+Up')
            self.scale_b2.setText('Ераклаштыру                                    CTRL+Down')
            self.scale_default.setText('Якынайту килешү буенча     CTRL+0')
            self.other_action.setText('Торыгыз csv таблицасы              Ctrl+Shift+V')
        else:
            if self.label != '':
                self.setWindowTitle(f'PyNote: {self.label} (Һаҡланған)')
            self.button_action.setText('Һаҡлап ҡалыу                     CTRL+S')
            self.button_action2.setText('Нисек һаҡларға... CTRL+SHIFT+S')
            self.button_action3.setText('Һаҡланмай сығыу')
            self.scale_b1.setText('Яҡынайтыу                                CTRL+Up')
            self.scale_b2.setText('Алыҫайтыу                                    CTRL+Down')
            self.scale_default.setText('Өндәшмәй генә яҡынайыу     CTRL+0')
            self.other_action.setText('Баҫыу csv таблица              Ctrl+Shift+V')

    def click_save(self):  # Функция обработки нажатия save
        if not self.editing:
            if self.previous_text == '' and self.previous_text != self.line.toPlainText():
                if Database().get_new_key_for_new_note() == 1:
                    n = Database().get_language()
                    p1 = ''
                    if n == 0:
                        p1 = 'Think of a password'
                    elif n == 1:
                        p1 = 'Придумайте пароль'
                    elif n == 2:
                        p1 = 'Прыдумайце пароль'
                    elif n == 3:
                        p1 = 'Малпасько пароль'
                    elif n == 4:
                        p1 = 'Серсүз уйлап табыгыз'
                    else:
                        p1 = 'Пароль уйлап табығыҙ'
                    dialog = GeneratePasswordForNoteInputDialog(labels=[p1])
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
        self.changed_index_lan(Database().get_language())

    def click_save_as(self):  # Функция обработки нажатия save as
        try:
            n = Database().get_language()
            if n == 0:
                file = QtWidgets.QFileDialog.getSaveFileName(None, 'Save', '/', "Text files (*.txt)")
            elif n == 1:
                file = QtWidgets.QFileDialog.getSaveFileName(None, 'Сохранить', '/', "Текстовые файлы (*.txt)")
            elif n == 2:
                file = QtWidgets.QFileDialog.getSaveFileName(None, 'Захаваць', '/', "Тэкставыя файлы (*.txt)")
            elif n == 3:
                file = QtWidgets.QFileDialog.getSaveFileName(None, 'Утьыны', '/', "Файл текстовой (*.txt)")
            elif n == 4:
                file = QtWidgets.QFileDialog.getSaveFileName(None, 'Саклау', '/', "Текст файллары (*.txt)")
            else:
                file = QtWidgets.QFileDialog.getSaveFileName(None, 'Һаҡлап ҡалыу', '/', "Текст архивтары (*.txt)")
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
        n = Database().get_language()
        if self.label != '':
            if n == 0:
                self.setWindowTitle(f'PyNote: {self.label} (Changes not saved)')
            elif n == 1:
                self.setWindowTitle(f'PyNote: {self.label} (Изменения не сохранены)')
            elif n == 2:
                self.setWindowTitle(f'PyNote: {self.label} (Змены не захаваныя)')
            elif n == 3:
                self.setWindowTitle(f'PyNote: {self.label} (Воштӥськонъёс ӧз утиськы)')
            elif n == 4:
                self.setWindowTitle(f'PyNote: {self.label} (Үзгәрешләр сакланмаган)')
            elif n == 5:
                self.setWindowTitle(f'PyNote: {self.label} (Үҙгәрештәр һаҡланмаған)')
        else:
            if n == 0:
                self.setWindowTitle('PyNote: Object (Not saved)')
            elif n == 1:
                self.setWindowTitle('PyNote: Объект (Не сохранено)')
            elif n == 2:
                self.setWindowTitle("PyNote: Аб'ект (не захавана)")
            elif n == 3:
                self.setWindowTitle("PyNote: Объектэз (ӧз)")
            elif n == 4:
                self.setWindowTitle('PyNote: Объект (сакланмаган)')
            elif n == 5:
                self.setWindowTitle('PyNote: Объект (һаҡланмаған)')

    def initUI(self):
        w, h = list(map(int, Database().get_resolution_note().split('x')))
        self.setGeometry(0, 0, w, h)
        n = Database().get_language()
        if n == 0:
            self.setWindowTitle('PyNote: Object')
        elif n == 1:
            self.setWindowTitle('PyNote: Объект')
        elif n == 2:
            self.setWindowTitle("PyNote: Аб'ект")
        elif n == 3:
            self.setWindowTitle("PyNote: Объектэз")
        elif n == 4:
            self.setWindowTitle('PyNote: Объект')
        elif n == 5:
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
            pass

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

    def create_settings(self, path, lan=1):
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
                                        key_entrance text,
                                        language integer
                                        )""")
                conn.commit()
                # language -> 0 - английский, 1 - русский, 2 - белорусский, 3 - удмуртский, 4 - татарский,
                # 5 - башкирский
                # 0 - False, 1 - True
                c.execute(f'insert into settings values (0, "1366x768", "800x600", 0, 1, "", {lan})')
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

    def get_language(self) -> int:  # Получить номер языка
        try:
            conn = sqlite3.connect(f'{Database().get_path()}\Settings.db')
            c = conn.cursor()
            c.execute('select language from settings where identity=0')
            value = c.fetchone()
            conn.close()
            return value[0]
        except BaseException:
            return 1

    def set_language(self, value):
        try:
            conn = sqlite3.connect(f'{Database().get_path()}\Settings.db')
            c = conn.cursor()
            c.execute(f'update settings set language={value}')
            conn.commit()
            conn.close()
        except BaseException:
            print('ETERNAL ERROR: LANGUAGE')

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


class GeneratePasswordForNoteInputDialog(QDialog):  # Создание пароля для новой заметки
    def __init__(self, labels, parent=None):
        super().__init__(parent)
        self.database = Database()
        self.setWindowIcon(QIcon('pynote.png'))
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        n = self.database.get_language()
        if n == 0:
            self.setWindowTitle('Think of a password')
        elif n == 1:
            self.setWindowTitle('Придумайте пароль')
        elif n == 2:
            self.setWindowTitle('Прыдумайце пароль')
        elif n == 3:
            self.setWindowTitle('Малпасько пароль')
        elif n == 4:
            self.setWindowTitle('Серсүз уйлап табыгыз')
        elif n == 5:
            self.setWindowTitle('Пароль уйлап табығыҙ')
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
        n = self.database.get_language()
        if n == 0:
            p1 = 'Password:'
        elif n == 1 or n == 2 or n == 3 or n == 5:
            p1 = 'Пароль:'
        else:
            p1 = 'Серсүз:'
        self.setWindowTitle(p1)
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
        n = self.database.get_language()
        if n == 0:
            self.setWindowTitle('Confirm password')
        elif n == 1:
            self.setWindowTitle('Подтвердите пароль')
        elif n == 2:
            self.setWindowTitle('Пацвердзіце пароль')
        elif n == 3:
            self.setWindowTitle('Пароль юнматэ')
        elif n == 4:
            self.setWindowTitle('Серсүзне раслагыз')
        else:
            self.setWindowTitle('Текстың йөкмәткеһен асыҡлау')

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
        n = Database().get_language()
        if n == 0:
            self.setWindowTitle('Are you sure? This action is not secure. Re-enter the password to confirm')
        elif n == 1:
            self.setWindowTitle('Вы уверены? Это действие не безопасно. Введите пароль повторно для подтверждения')
        elif n == 2:
            self.setWindowTitle('Ты ўпэўнены? Гэта дзеянне небяспечна. Паўторна увядзіце пароль для пацверджання')
        elif n == 3:
            self.setWindowTitle('Тӥледлы оске-а? Та уж безопасной ӧвӧл. Кайта возьматон понна пыртэм пароль')
        elif n == 4:
            self.setWindowTitle('Сез ышанасызмы? Бу гамәл куркынычсыз түгел. Раслау өчен серсүзне кабат языгыз')
        else:
            self.setWindowTitle('Ышанаһығыҙмы? Был хәрәкәт хәүефһеҙ түгел. Дәлилләү өсөн ҡабаттан пароль индерегеҙ')
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
            else:
                Database().create_database_(hash_code(self.getInputs()[1]), self.getInputs()[0])
            self.close()


if __name__ == "__main__":
    main()  # Запуск приложения
