import tkinter.font as tkFont
import tkinter as tk

THEME_PATH = 'theme.txt'

class Theme:
    def __init__(self,
                 path=THEME_PATH
                 ):
        self.path = path
        self.background = '#f2e9dc'
        self.body_font = tkFont.Font(family='Arial',size=12,weight='bold')
        self.header_font = tkFont.Font(family='Arial',size=20,weight='bold')
        self._listeners = []
        self.load()

    def load(self, path='theme.txt'):
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
                temp_family = lines[0].strip()
                temp_background = lines[1].strip()
        except (FileNotFoundError):
            return

        self.background = temp_background
        self.body_font.configure(family=temp_family)

    def add_listener(self, call_listener):
        self._listeners.append(call_listener)

    def set_font(self, family):
        self.body_font.configure(family=family)
        self.header_font.configure(family=family)
        self._notify()

    def set_background(self, colour):
        self.background = colour
        self._notify()

    def _notify(self):
        for call_listener in self._listeners:
            call_listener()

        self.save()

    def save(self, path='theme.txt'):
        with open(path, 'w') as file:
            file.write(self.body_font.actual('family') + '\n')
            file.write(self.background + '\n')
