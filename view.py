import tkinter.ttk as ttk
import tkinter.messagebox
import tkinter.font as tkFont
import tkinter as tk

from other_controls import HEADER_SIZE, HOME_COLOUR, new_question, check_answer, clean_word
from theme import Theme
from scraping_data import get_book, get_gutenberg_details, get_word_definitions, NoDefinition
from manipulating_database import get_latest_bookmark, add_bookmark, store_word, check_book_duplicate, store_book, \
    get_books_from_database, get_all_books

class HomeButton(tk.Button):
    '''A home page button that will appear on all pages'''
    def __init__(self, parent, controller,**kwargs):
        super().__init__(
            parent,
            text='Home',
            command=lambda: controller.show_frame(HomePage),
            foreground=HOME_COLOUR,
            font = controller.theme.body_font,
            **kwargs
        )

class KindleApp(tkinter.Tk):
    """This is the main window;
    it holds every screen as a stacked frame and swaps the ones that are visible"""

    def __init__(self):
        super().__init__()
        self.title("Kindle App")
        self.geometry("800x600")
        self.theme = Theme()

        self.theme.load()
        self.theme.add_listener(self.apply_theme)
        self.style = ttk.Style()
        self.style.theme_use('clam')

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in [HomePage,SearchBookPage,ReadBookPage,ReadingPage,DictionaryPage,WordTesterPage,ThemesPage,FontFrame,BackgroundFrame]:

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, page_class,**kwargs):
        frame = self.frames[page_class]
        if hasattr(page_class,'on_show'):
            frame.on_show(**kwargs)
        frame.tkraise()

    def apply_theme(self):
        bg = self.theme.background
        self.configure(bg=bg)

        self.style.configure('.', background=bg, font=self.theme.body_font)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, font=self.theme.body_font)
        self.style.configure('Custom.TLabel', background=bg, font=self.theme.header_font)
        self.style.configure('TButton', font=self.theme.body_font)
        self.style.configure('TEntry', font=self.theme.body_font)

        self._recolour_widgets(self,bg)

    def _recolour_widgets(self,widget,bg):
        if isinstance(widget, (tk.Text, tk.Button)):
            widget.configure(background=bg)

        for child in widget.winfo_children():
            self._recolour_widgets(child,bg)

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.style = ttk.Style()

        ttk.Label(self, text="Kindle", style='Custom.TLabel').pack(pady=40)

        buttons = [
            ["Search Books", SearchBookPage],
            ["Read a Book", ReadBookPage],
            ["Dictionary", DictionaryPage],
            ["Word Tester", WordTesterPage],
            ["Theme Changer", ThemesPage],
        ]

        for t, page in buttons:
            ttk.Button(self, text=str(t), width=20,
                       command=lambda p=page: controller.show_frame(p)).pack(pady=8,padx=50)

class SearchBookPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text='Search Books', style='Custom.TLabel').pack(pady=20)

        self.entry = ttk.Entry(self, width=40)
        self.entry.pack(pady=20)

        # this label will show whether the book has been found in Gutenberg Project or not
        self.status_label = ttk.Label(self, text='')
        self.status_label.pack(pady=20)

        ttk.Button(self, text="Search Books", command=self.search_book).pack(pady=5)

        HomeButton(self,controller).place(x=20,y=20)

    def download_book(self,title, author, id):
        book_text=get_book(id)
        '''
        try:
            book_text = get_book(id)
        except Exception as e:
            #find what exception this is and rename
            print(e)
            self.status_label.config(text=f"{title} could not be downloaded", fg='red', font=font, width=50)
            return
        '''
        # Do i need this?

        store_book(id,title,author,book_text)
        self.status_label.config(text=f"Book for {title} downloaded")


    def search_book(self):
        name = self.entry.get().strip()

        if not name:
            self.status_label.config(text="Please enter a book name")
            return

        self.status_label.config(text='Searching...')
        ''', fg='black', font=current_font, width=50'''
        self.update_idletasks()

        #calling get_gutenberg_details()
        result = get_gutenberg_details(name)

        if result is None:
            self.status_label.config(text=f"Book for {name} not found")
            ''', fg='red', font=current_font, width=50'''
            return

        g_title, g_author, g_id, g_scr = result
        # g_title = result[0]
        # g_author = result[1]
        # g_id = result[2]

        exists = check_book_duplicate(g_id)

        if exists:
            self.status_label.config(text=f"Book for {g_title} already downloaded")
            ''', fg='black', font=current_font, width=50'''
            return

        response = tkinter.messagebox.askyesno(title='Your book choice', message=f'Match level is {g_scr} out of 100 \n\nDo you want to download {g_title}')
        if response:
            self.download_book(g_title, g_author, g_id)
        else:
            self.status_label.config(text=f"No book downloaded")
            ''', fg='black', font=current_font, width=50'''

class ReadBookPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Your Books:", style='Custom.TLabel').pack(pady=20)

        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(pady=10,fill='both',expand=True)

        HomeButton(self,self.controller).place(x=20,y=20)

    def on_show(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        books = get_all_books()

        if not books:
            ttk.Label(self.list_frame, text='No books downloaded...').pack(pady=20)
            return

        for book in books:
            ttk.Button(
                self.list_frame,
                text=f"{book.book_title}, {book.book_author}",
                width=50,
                command=lambda b_id=book.book_id: self.controller.show_frame(ReadingPage, book_id=b_id)
            ).pack(pady=5)

class ReadingPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_book_id = None

        top_bar = ttk.Frame(self,height=60)
        top_bar.pack(fill='x')
        top_bar.propagate(False)

        self.title_label = ttk.Label(top_bar, text='',style='Custom.TLabel')
        self.title_label.place(x=100, y=20)

        HomeButton(self,self.controller).place(x=20,y=20)

        ttk.Button(
            top_bar,
            text='Bookmark Here',
            command=self.add_new_bookmark
        ).pack(side='right', padx=10, pady=10)

        text_frame = ttk.Frame(self)
        text_frame.pack(fill='both',expand=True,padx=10,pady=30)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side='right',fill='y')

        self.text_widget = tk.Text(
            text_frame,
            wrap='word',
            yscrollcommand=scrollbar.set,
            bg=controller.theme.background,
            relief='sunken',
            font=controller.theme.body_font,
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
        self.text_widget.delete(1.0, "end")
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
            tkinter.messagebox.showinfo('Bookmarked','Your place has been saved')

    def look_up_selected_word(self,event):
        self.add_new_bookmark(True)
        try:
            not_clean = self.text_widget.get('insert wordstart', 'insert wordend')
            word = clean_word(not_clean)
        except Exception as e:
            '''figure out what TclError is in tkk'''
            return

        if not word:
            return
        self.controller.show_frame(DictionaryPage, word=word, book_id=self.current_book_id)

class DictionaryPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_book_id = None

        ttk.Label(self, text='Dictionary', style='Custom.TLabel').pack(pady=20)

        self.entry = ttk.Entry(self, width=50)
        self.entry.pack(pady=10)

        ttk.Button(
            self,
            text='Search',
            command=self.search_word,
        ).pack(pady=5)

        self.result_frame = ttk.Frame(self)
        self.result_frame.pack(pady=10,fill='both',expand=True, padx=10,)

        scrollbar = ttk.Scrollbar(self.result_frame)
        scrollbar.pack(side='right',fill='y')

        self.result_text = tk.Text(
            self.result_frame,
            wrap='word',
            yscrollcommand=scrollbar.set,
            bg=controller.theme.background,
            relief='sunken',
            font=(controller.theme.body_font, 10)
        )
        self.result_text.pack(side='left',fill='both',expand=True,padx=10,pady=10)
        scrollbar.config(command=self.result_text.yview)

        HomeButton(self,self.controller).place(x=20,y=20)

    def on_show(self, book_id=None, word=None):
        self.current_book_id = book_id
        if word:
            self.entry.delete(0, "end")
            self.entry.insert(0, word)
            self.search_word()

    def search_word(self):
        self.result_text.delete('1.0', "end")

        word = self.entry.get().strip().lower()

        if not word:
            return

        try:
            definitions = get_word_definitions(word)
            store_word(definitions,word, self.current_book_id)

            for i in range(len(definitions)):
                self.result_text.insert('end', f'{i + 1} - {definitions[i]}\n')

        except NoDefinition:
            self.result_text.insert('1.0', f'Error - No definition for {word} found')
            return

class WordTesterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.correct_answer = None

        ttk.Label(self, text ='Word Testing', style='Custom.TLabel').pack(pady=20)

        self.question_label = ttk.Label(self, text='', wraplength=600)
        self.question_label.pack(pady=20)

        self.option_buttons = []
        for i in range(4):
            b = ttk.Button(self, text='', width=50)
            b.pack(pady=5)
            self.option_buttons.append(b)

        self.feedback_label = ttk.Label(self, text='')
        self.feedback_label.pack(pady=10)

        ttk.Button(
            self,
            text='Next Question',
            command = self.next_question
        ).pack(pady=10)

        HomeButton(self, self.controller).place(x=20, y=20)

    def on_show(self):
        self.next_question()

    def next_question(self):
        self.feedback_label.config(text='')

        question_details = new_question()

        if question_details is None:
            self.question_label.config(text='Not enough word history yet - look up some more words')
            for b in self.option_buttons:
                b.config(
                    text='',
                    state='disabled',
                    command=b.destroy
                )
            return

        self.correct_answer = question_details[2]
        self.question_label.config(text=f'What does {question_details[1]} mean?')

        for i in range(len(self.option_buttons)):
            b = self.option_buttons[i]
            b.update_idletasks()
            width=b.winfo_width()
            b.config(
                text=question_details[0][i],
                state='normal',
                wraplength=width,
                command=lambda o=question_details[0][i]: self.check_option(o)
            )

    def check_option(self, option):
        result = check_answer(option, self.correct_answer)

        if result:
            self.feedback_label.config(text='Correct!')
            """, fg='green'"""
        else:
            self.feedback_label.config(text='Incorrect!')
            """, fg='red'"""

class ThemesPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.style = ttk.Style()

        ttk.Label(self, text='Themes', style='Custom.TLabel').pack(pady=20)
        HomeButton(self, self.controller).place(x=20, y=20)


        theme_options = [
            ('Change Font', FontFrame),
            ('Change Background Colour', BackgroundFrame)
        ]
        
        for b, page in theme_options:
            ttk.Button(self, text=str(b), width=20,
                       command=lambda p=page: controller.show_frame(p)).pack(pady=8,padx=50)

class FontFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text='Changing Font...', style='Custom.TLabel').pack(pady=20)
        HomeButton(self, self.controller).place(x=20, y=20)

        font_buttons = [
            ("Times New Roman", 'Times New Roman'),
            ("Arial", 'Arial'),
            ("Courier", 'Courier'),
            ("Comic Sans", 'Comic Sans MS'),
            ("Sans Serif", 'Sans Serif'),
        ]

        for label, family in font_buttons:
            full_font = tkFont.Font(family=family, size=10, weight='bold')
            button = tk.Button(self, text=str(label), width=20, font=full_font)
            button.config(command=lambda f=family: controller.theme.set_font(f))
            button.pack(pady=8, padx=50)
    '''
    def change_font(self, new_font):
        current_font = new_font
        print(new_font)

        self.style.configure('TFrame',font=new_font)
        self.style.configure('TLabel',font=new_font)
        self.style.configure('TButton',font=new_font)
        self.style.configure('TCombobox',font=new_font)
        self.style.configure('TEntry',font=new_font)
        
        '''

class BackgroundFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text='Changing Background...', style='Custom.TLabel').pack(pady=20)
        HomeButton(self, self.controller).place(x=20, y=20)

        bg_buttons = [
            ('White', 'white'),
            ('Paper', '#f2e9dc'),
            ('Purple', 'purple')
        ]

        for label, colour in bg_buttons:
            button = tk.Button(self, text=str(label), width=20, background=colour)
            button.config(command=lambda c=colour: controller.theme.set_background(c))
            button.pack(pady=8, padx=50)
    '''
    def change_bg(self,new_bg_colour):
        bg_colour = new_bg_colour

        self.style.configure('TFrame',background=new_bg_colour)
        self.style.configure('Custom.TLabel',background=new_bg_colour)
        self.style.configure('TCombobox',background=new_bg_colour)
    '''