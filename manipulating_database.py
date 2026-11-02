import sqlalchemy
from sqlalchemy import orm
from kindle_database import Base, Books, Word, Bookmark, Lookup, Definition
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
        try:
            word_exists = session.query(Word).filter_by(
            word=str(u_w),
            ).first()

            if word_exists is None:
                word_exists = Word(
                    word=str(u_w),
                )
                session.add(word_exists)
                session.flush()

            for defi in u_def:
                def_exists = session.query(Definition).filter_by(
                    word_id=word_exists.word_id,
                    meaning=defi,
                ).first()

                if def_exists is None:
                    new_definition = Definition(
                        meaning=defi,
                        word=word_exists
                    )
                    session.add(new_definition)

            new_lookup = Lookup(
                word=word_exists,
                book_id=book_id,
            )

            session.add(new_lookup)


            session.commit()

        except Exception:
            session.rollback()
            raise
        '''
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

        session.commit()'''

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
            .options(orm.selectinload(Word.definitions))
            .join(Lookup)
            .filter(Lookup.time_stamp >= cutoff)
            .distinct()
            .all()
        )
    return recent_words

def get_all_words():
    with (orm.Session(engine) as session):
        all_word = session.query(Word).options(orm.selectinload(Word.definitions)).all()
    return all_word

# Make more for the validation i.e. if get ids returns none do something about that