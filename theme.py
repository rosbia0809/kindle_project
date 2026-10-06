import tkinter.font as tkFont
import json

THEME_PATH = 'theme.json'
DEFAULT_FONT = 'Arial'
DEFAULT_BACKGROUND = '#f2e9dc'

class Theme:
    def __init__(self,
                 path=THEME_PATH
                 ):
        self.path = path
        self.background = DEFAULT_BACKGROUND
        self.font = DEFAULT_FONT
        self.body_font = tkFont.Font(family=self.font,size=12,weight='bold')
        self.header_font = tkFont.Font(family=self.font,size=20,weight='bold')
        self._listeners = []
        self.load()

        print(self.background)
        print(self.font)


    def load(self, path='theme.json'):
        try:
            with open(path, 'r') as file:
                t_data = file.readline()
                data = json.loads(t_data)

                self.background = data['background']
                self.font = data['font']
                self.set_font(self.font)
                self.set_background(self.background)

                print(data)

        except (FileNotFoundError):
            return

    def add_listener(self, call_listener):
        self._listeners.append(call_listener)

    def set_font(self, family):
        self.body_font.configure(family=family)
        self.header_font.configure(family=family)
        self._notify()

    def set_background(self, colour):
        self.background = colour
        self._notify()

        self.save()

    def _notify(self):
        for call_listener in self._listeners:
            call_listener()

        self.save()

    def save(self, path='theme.json'):
        with open(path, 'w') as file:
            json.dump({'background': self.background, 'font': self.font}, file)
