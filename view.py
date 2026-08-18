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
        for F in [HomePage,SearchBookPage,]:
            '''
            ReadBookPage,
            ReadingPage,
            DictionaryPage,
            WordTesterPage,'''

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

        tk.Label(self, text="Kindle", font=("Ariel", 28), bg="#f2e9dc").pack(pady=40)

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
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f2e9dc")
        self.controller = controller

        tk.Label(self,text='Search Books', font=("Ariel",20), bg="#f2e9dc").pack(pady=20)

        self.entry = tk.Entry(self,width=40)
        self.entry.pack(pady=20)

        # this label will show whether the book has been found in Gutenberg Project or not
        self.status_label = tk.Label(self,text='',bg="#f2e9dc")
        self.status_label.pack(pady=20)

        tk.Button(self, text="Search Books", command=self.search_book).pack(pady=5)
        tk.Button(
            self,
            text="Home",
            fg='brown',
            bg='white',
            command=lambda: controller.show_frame(HomePage)
        ).place(x=20,y=20)

    def search_book(self):
        name = self.entry.get().strip()

        if not name:
            self.status_label.config(text="Please enter a book name")
            return

        self.status_label.config(text='Searching...', fg='black')
        self.update_idletasks()

        #calling get_gutenberg_details()
        result = get_gutenberg_details(name)

        if result is None:
            self.status_label.config(text=f"Book for {name} not found", fg='red')
            return

        g_title = result[0]
        g_author = result[1]
        g_id = result[2]

        #checking for duplicates before downloading
        with orm.Session(engine) as session:
            exists = session.get(Books,str(g_id))
        if exists:
            self.status_label.config(text=f"Book for {g_title} already downloaded", fg='black')
            return

        try:
            book_text = get_book(g_id)
        except Exception:
            self.status_label.config(text=f"{g_title} could not be downloaded", fg='red')
            return

        #adding to database
        with orm.Session(engine) as session:
            book = Books(
                book_id=str(g_id),
                book_title=g_title,
                book_author=g_author,
                book_text=book_text,
            )
            session.add(book)
            session.commit()

        self.status_label.config(text=f"Book for {g_title} downloaded", fg='green')



if __name__ == "__main__":
    app = KindleApp()
    app.mainloop()
