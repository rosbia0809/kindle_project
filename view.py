import tkinter as tk
from tkinter import messagebox
import sqlalchemy
from sqlalchemy import orm
import string
from datetime import datetime, timedelta
import random

from kindle_database import Base, Books, Word, Lookup
from data_from_gutenburg import get_book, get_gutenberg_details
from dictionary_search import get_word_definitions
from adding_to_database import get_latest_bookmark, add_bookmark

BG_COLOUR = '#f2e9dc'
HOME_COLOUR = 'brown'
FONT = 'Ariel'
HEADER_SIZE = 20

engine = sqlalchemy.create_engine('sqlite:///kindle.db')
Base.metadata.create_all(engine)

class KindleApp(tk.Tk):
    """This is the main window;
    it holds every screen as a stacked frame and swaps the ones that are visible"""

    def __init__(self):
        super().__init__()
        self.title("Kindle App")
        self.geometry("800x600")
        self.configure(bg=BG_COLOUR)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in [HomePage,SearchBookPage,ReadBookPage,ReadingPage,]:
            '''
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
        super().__init__(parent, bg=BG_COLOUR)

        tk.Label(self, text="Kindle", font=(FONT, 28), bg=BG_COLOUR).pack(pady=40)

        buttons = [
            ["Search Books", SearchBookPage],
            ["Read a Book", ReadBookPage],
            '''
            ["Dictionary", DictionaryPage],
            ["Word Tester", WordTesterPage],'''
        ]
        for b in range (len(buttons)):
            t = buttons[b][0]
            page=buttons[b][1]
            tk.Button(self, text=str(t), width=20, height=2,
                      command=lambda p=page: controller.show_frame(p)).pack(pady=8,padx=50)

class SearchBookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.controller = controller

        tk.Label(self,text='Search Books', font=(FONT,HEADER_SIZE), bg=BG_COLOUR).pack(pady=20)

        self.entry = tk.Entry(self,width=40)
        self.entry.pack(pady=20)

        # this label will show whether the book has been found in Gutenberg Project or not
        self.status_label = tk.Label(self,text='',bg=BG_COLOUR,font=FONT)
        self.status_label.pack(pady=20)

        tk.Button(self, text="Search Books", command=self.search_book).pack(pady=5)
        tk.Button(
            self,
            text="Home",
            fg=HOME_COLOUR,
            bg='white',
            font=FONT,
            command=lambda: controller.show_frame(HomePage)
        ).place(x=20,y=20)

    def search_book(self):
        name = self.entry.get().strip()

        if not name:
            self.status_label.config(text="Please enter a book name")
            return

        self.status_label.config(text='Searching...', fg='black',font=FONT)
        self.update_idletasks()

        #make this into its own subroutine!!!
        #calling get_gutenberg_details()
        result = get_gutenberg_details(name)

        if result is None:
            self.status_label.config(text=f"Book for {name} not found", fg='red',font=FONT)
            return

        g_title = result[0]
        g_author = result[1]
        g_id = result[2]

        #checking for duplicates before downloading
        with orm.Session(engine) as session:
            exists = session.get(Books,str(g_id))
        if exists:
            self.status_label.config(text=f"Book for {g_title} already downloaded", fg='black',font=FONT)
            return

        try:
            book_text = get_book(g_id)
        except Exception:
            self.status_label.config(text=f"{g_title} could not be downloaded", fg='red',font=FONT)
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

        self.status_label.config(text=f"Book for {g_title} downloaded", fg='green',font=FONT)

class ReadBookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.controller = controller

        tk.Label(self, text="Your Books:", font=(FONT,HEADER_SIZE), bg=BG_COLOUR).pack(pady=20)

        self.list_frame = tk.Frame(self, bg=BG_COLOUR)
        self.list_frame.pack(pady=10,fill='both',expand=True)

        tk.Button(
            self,
            text="Home",
            fg=HOME_COLOUR,
            bg='white',
            font=FONT,
            command=lambda: controller.show_frame(HomePage)
        ).place(x=20, y=20)

    def on_show(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        #make into its own subroutine!!!
        with orm.Session(engine) as session:
            books = session.query(Books).all()

        if not books:
            tk.Label(self.list_frame, text='No books downloaded...', font=FONT, bg=BG_COLOUR).pack(pady=20)
            return

        for book in books:
            tk.Button(
                self.list_frame,
                text=f"{book.book_title}, {book.book_author}",
                width=50,
                command=lambda b_id=book.book_id: self.controller.show_frame(ReadingPage, book_id=b_id)
            ).pack(pady=5)

class ReadingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.controller = controller
        self.current_book_id = None

        top_bar = tk.Frame(self, bg=BG_COLOUR)
        top_bar.pack(fill='x')

        self.title_label = tk.Label(top_bar, text='', font=(FONT,16), bg=BG_COLOUR)
        self.title_label.place(x=200, y=20)

        tk.Button(
            self,
            text="Home",
            fg=HOME_COLOUR,
            bg='white',
            font=FONT,
            command=lambda: controller.show_frame(HomePage)
        ).place(x=20, y=20)

        tk.Button(
            top_bar,
            text='Bookmark Here',
            command=self.add_new_bookmark
        ).pack(side='right', padx=10, pady=10)

        text_frame = tk.Frame(self)
        text_frame.pack(fill='both',expand=True,padx=10,pady=30)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right',fill='y')

        self.text_widget = tk.Text(
            text_frame,
            wrap='word',
            yscrollcommand=scrollbar.set,
            bg=BG_COLOUR,
            relief='sunken',
            font=FONT,
        )
        self.text_widget.pack(side='left',fill='both',expand=True,padx=10,pady=10)
        scrollbar.config(command=self.text_widget.yview)

        #double-click a word to look it up
        self.text_widget.bind("<Double-Button-1>",self.look_up_selected_word)

    def on_show(self, book_id=None):
        if book_id is None:
            return
        self.current_book_id = book_id

        with orm.Session(engine) as session:
            book=session.get(Books, book_id)

        self.title_label.config(text=f'{book.book_title}')
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0,f'{book.book_text}')

        last_bookmark = get_latest_bookmark(book_id)
        if last_bookmark:
            self.text_widget.update_idletasks()
            self.text_widget.yview_moveto(last_bookmark)

    def add_new_bookmark(self):
        position = self.text_widget.yview()[0]
        add_bookmark(self.current_book_id, position)
        messagebox.showinfo('Bookmarked','Your place has been saved')

    def look_up_selected_word(self,event):
        try:
            not_clean = self.text_widget.get('insert wordstart', 'insert wordend')
            word = ''.join([char for char in not_clean if char not in string.punctuation])
        except tk.TclError:
            return

        if not word:
            return
        self.controller.show_frame(DictionaryPage, word=word, book_id=self.current_book_id)
