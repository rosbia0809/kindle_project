import sqlalchemy
from sqlalchemy import orm
from kindle_database import Base, Books, Word, Bookmark, Lookup
from scraping_data import get_book, get_gutenberg_details, get_word_definitions, NoDefinition
from datetime import datetime, timedelta

engine = sqlalchemy.create_engine('sqlite:///kindle.sqlite')
Base.metadata.create_all(engine)

def check_book_duplicate(book_id):
    with orm.Session(engine) as session:
        duplicate = session.get(Books, str(book_id))

    return duplicate

def store_book(book_id: int, title: str, author: str, text: str):
    with orm.Session(engine) as session:
        book = Books(
            book_id=book_id,
            book_title=title,
            book_author=author,
            book_text=text,
        )
        session.add(book)
        session.commit()

def get_books_from_database(id):
    with orm.Session(engine) as session:
        requested_book = session.get(Books, id)
        return requested_book

def get_all_books():
    with orm.Session(engine) as session:
        all_books = session.query(Books).all()

    return all_books

def store_word(u_def, u_w:str,book_id: int):
    with orm.Session(engine) as session:
        for defi in u_def:
            exists = session.query(Word).filter_by(word=str(u_w), meaning=defi).first()

            if exists:
                w = exists
            else:
                w = Word(
                    word=str(u_w),
                    meaning=str(defi),
                    lookups=[],
                )
                session.add(w)
                session.commit()

            lookup = Lookup(
                word_id=w.word_id,
                book_id=book_id,
                time_stamp=datetime.now(),
            )
            session.add(lookup)

        session.commit()

def get_latest_bookmark(book_id: int):
    with orm.Session(engine) as session:
        bookmark = (
            session.query(Bookmark)
            .filter_by(book_id=str(book_id))
            .order_by(Bookmark.time_stamp.desc())
            .first()
        )

        if bookmark:
            return bookmark.position
        else:
            return None

def add_bookmark(book_id: int, position: float):
    with orm.Session(engine) as session:
        bookmark = Bookmark(
            book_id=book_id,
            position=position,
        )
        session.add(bookmark)
        session.commit()

def get_recent_words():
    cutoff = datetime.now() - timedelta(days=30)
    with orm.Session(engine) as session:
        recent_words = (
            session.query(Word)
            .join(Lookup)
            .filter(Lookup.time_stamp >= cutoff)
            .distinct()
            .all()
        )
    return recent_words

def get_all_words():
    with orm.Session(engine) as session:
        all_word = session.query(Word).all()
    return all_word

# Make more for the validation i.e. if get ids returns none do something about that