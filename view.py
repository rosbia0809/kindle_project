import tkinter as tk
from tkinter import messagebox
import sqlalchemy
from datetime import datetime, timedelta
import random

from other_controls import HEADER_SIZE, HOME_COLOUR, bg_colour, font, clean_word
from scraping_data import get_book, get_gutenberg_details, get_word_definitions, NoDefinition
from manipulating_database import get_latest_bookmark, add_bookmark, store_word, check_book_duplicate, store_book, \
    get_books_from_database, get_all_books


class HomeButton(tk.Button):
    '''A home page button that will appear on all pages'''
    def __init__(self, parent, controller,**kwargs):
        super().__init__(
            parent,
            text='Home',
            fg=HOME_COLOUR,
            bg='white',
            font=font,
            command=lambda: controller.show_frame(HomePage),
            **kwargs
        )

class KindleApp(tk.Tk):
    """This is the main window;
    it holds every screen as a stacked frame and swaps the ones that are visible"""

    def __init__(self):
        super().__init__()
        self.title("Kindle App")
        self.geometry("800x600")
        self.configure(bg=bg_colour)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in [HomePage,SearchBookPage,ReadBookPage,ReadingPage,DictionaryPage]:
            '''
            WordTesterPage'''

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
        super().__init__(parent, bg=bg_colour)

        tk.Label(self, text="Kindle", font=(font, 28), bg=bg_colour).pack(pady=40)

        buttons = [
            ["Search Books", SearchBookPage],
            ["Read a Book", ReadBookPage],
            ["Dictionary", DictionaryPage],
            '''["Word Tester", WordTesterPage]'''
        ]
        for b in range (len(buttons)-1):
            t = buttons[b][0]
            page=buttons[b][1]
            tk.Button(self, text=str(t), width=20, height=2,
                      command=lambda p=page: controller.show_frame(p)).pack(pady=8,padx=50)

class SearchBookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=bg_colour)
        self.controller = controller

        tk.Label(self, text='Search Books', font=(font, HEADER_SIZE), bg=bg_colour).pack(pady=20)

        self.entry = tk.Entry(self,width=40)
        self.entry.pack(pady=20)

        # this label will show whether the book has been found in Gutenberg Project or not
        self.status_label = tk.Label(self, text='', bg=bg_colour, font=font)
        self.status_label.pack(pady=20)

        tk.Button(self, text="Search Books", command=self.search_book).pack(pady=5)

        HomeButton(self,controller).place(x=20,y=20)

    def search_book(self):
        name = self.entry.get().strip()

        if not name:
            self.status_label.config(text="Please enter a book name")
            return

        self.status_label.config(text='Searching...', fg='black', font=font)
        self.update_idletasks()

        #calling get_gutenberg_details()
        result = get_gutenberg_details(name)

        if result is None:
            self.status_label.config(text=f"Book for {name} not found", fg='red', font=font)
            return

        g_title = result[0]
        g_author = result[1]
        g_id = result[2]

        exists = check_book_duplicate(g_id)
        if exists:
            self.status_label.config(text=f"Book for {g_title} already downloaded", fg='black', font=font)
            return

        try:
            book_text = get_book(g_id)
        except Exception:
            self.status_label.config(text=f"{g_title} could not be downloaded", fg='red', font=font)
            return

        store_book(g_id,g_title,g_author,book_text)
        self.status_label.config(text=f"Book for {g_title} downloaded", fg='green', font=font)

class ReadBookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=bg_colour)
        self.controller = controller

        tk.Label(self, text="Your Books:", font=(font, HEADER_SIZE), bg=bg_colour).pack(pady=20)

        self.list_frame = tk.Frame(self, bg=bg_colour)
        self.list_frame.pack(pady=10,fill='both',expand=True)

        HomeButton(self,self.controller).place(x=20,y=20)

    def on_show(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        books = get_all_books()

        if not books:
            tk.Label(self.list_frame, text='No books downloaded...', font=font, bg=bg_colour).pack(pady=20)
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
        super().__init__(parent, bg=bg_colour)
        self.controller = controller
        self.current_book_id = None

        top_bar = tk.Frame(self, bg=bg_colour, height=60)
        top_bar.pack(fill='x')
        top_bar.propagate(False)

        self.title_label = tk.Label(top_bar, text='', font=(font, HEADER_SIZE), bg=bg_colour)
        self.title_label.place(x=100, y=20)

        HomeButton(self,self.controller).place(x=20,y=20)

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
            bg=bg_colour,
            relief='sunken',
            font=font,
        )
        self.text_widget.pack(side='left',fill='both',expand=True,padx=10,pady=10)
        scrollbar.config(command=self.text_widget.yview)

        #double-click a word to look it up
        self.text_widget.bind("<Double-Button-1>",self.look_up_selected_word)

    def on_show(self, book_id=None):
        if book_id is None:
            return
        self.current_book_id = book_id

        book = get_books_from_database(book_id)

        self.title_label.config(text=f'{book.book_title}')
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0,f'{book.book_text}')

        last_bookmark = get_latest_bookmark(book_id)
        if last_bookmark:
            self.text_widget.update_idletasks()
            self.text_widget.yview_moveto(last_bookmark)

    def add_new_bookmark(self,dict=False):
        ''' This function adds a new bookmark
        the dict variable is used to identify whether the user wanted to add a bookmark
        if it is simply due to the use of the dictionary then a message box won't be used'''
        position = self.text_widget.yview()[0]
        add_bookmark(self.current_book_id, position)
        if not dict:
            messagebox.showinfo('Bookmarked','Your place has been saved')

    def look_up_selected_word(self,event):
        self.add_new_bookmark(True)
        try:
            not_clean = self.text_widget.get('insert wordstart', 'insert wordend')
            word = clean_word(not_clean)
        except tk.TclError:
            return

        if not word:
            return
        self.controller.show_frame(DictionaryPage, word=word, book_id=self.current_book_id)

class DictionaryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=bg_colour)
        self.controller = controller
        self.current_book_id = None

        tk.Label(self, text='Dictionary',font=(font, HEADER_SIZE), bg=bg_colour).pack(pady=20)

        self.entry = tk.Entry(self, width=50)
        self.entry.pack(pady=10)

        tk.Button(
            self,
            text='Search',
            command=self.search_word,
        ).pack(pady=5)

        self.result_frame = tk.Frame(self, bg=bg_colour)
        self.result_frame.pack(pady=10,fill='both',expand=True, padx=10,)

        scrollbar = tk.Scrollbar(self.result_frame)
        scrollbar.pack(side='right',fill='y')

        self.result_text = tk.Text(
            self.result_frame,
            wrap='word',
            yscrollcommand=scrollbar.set,
            bg=bg_colour,
            relief='sunken',
            font=(font,10)
        )
        self.result_text.pack(side='left',fill='both',expand=True,padx=10,pady=10)
        scrollbar.config(command=self.result_text.yview)

        HomeButton(self,self.controller).place(x=20,y=20)

    def on_show(self, book_id=None, word=None):
        self.current_book_id = book_id
        if word:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, word)
            self.search_word()

    def search_word(self):
        self.result_text.delete('1.0',tk.END)

        word = self.entry.get().strip().lower()

        if not word:
            return

        try:
            definitions = get_word_definitions(word)
            for i in range(len(definitions)):
                self.result_text.insert('end', f'{i + 1} - {definitions[i]}\n')

        except NoDefinition:
            self.result_text.insert('1.0', f'Error - No definition for {word} found')
            return
'''
class WordPage(tk.Frame):
    def __init__(self, parent, controller):
        pass'''