import tkinter as tk
from tkinter import messagebox
import sqlalchemy
from sqlalchemy import orm
from datetime import datetime, timedelta
import random

from kindle_database import Base, Books, Word, Lookup
from data_from_gutenburg import get_book, get_gutenberg_details
from dictionary_search import get_word_definitions

engine = sqlalchemy.create_engine('sqlite:///kindle.db')
Base.metadata.create_all(engine)

class KindleApp(tk.Tk):
    '''This is the main window;
    it holds every screen as a stacked frame and swaps the ones that are visible'''

    def __init__(self):
        super().__init__()
        self.title("Kindle App")
        self.geometry("800x600")
        self.configure(bg="#f2e9dc")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in [HomePage,
                  SearchBookPage,
                  '''ReadBookPage,
                  ReadingPage,
                  DictionaryPage,
                  WordTesterPage,'''
                  ]:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, page_class,**kwargs):
        frame = self.frames[page_class]
        if hasattr(page_class,'on_show'):
            frame.on_show(**kwargs)
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f2e9dc")

        tk.Label(self, text="Kindle", font=("Georgia", 28), bg="#f2e9dc").pack(pady=40)

        buttons = [
            ["Search Books", SearchBookPage],
            '''("Read a Book", ReadBookPage),
            ("Dictionary", DictionaryPage),
            ("Word Tester", WordTesterPage),'''
        ]
        for item in buttons:
            text = item[0]
            page=item[1]
            tk.Button(self, text=text, width=20, height=2,
                      command=lambda p=page: controller.show_frame(p)).pack(pady=8)


class SearchBookPage(tk.Frame):
    pass

if __name__ == "__main__":
    app = KindleApp()
    app.mainloop()
