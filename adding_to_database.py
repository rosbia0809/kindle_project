import sqlalchemy
from sqlalchemy import orm
from kindle_database import Base, Books, Word, Bookmark
from data_from_gutenburg import get_book, get_gutenberg_details
from dictionary_search import get_word_definitions
from datetime import datetime


class NoDefinition(Exception):
    pass


class CurrentTimeError(Exception):
    pass


engine = sqlalchemy.create_engine('sqlite:///kindle.db')
Base.metadata.create_all(engine)


def store_book(name: str):
    g_title = get_gutenberg_details(name)[0]
    g_author = get_gutenberg_details(name)[1]
    g_id = get_gutenberg_details(name)[2]

    if g_id is None:
        print(f'no gutenberg id found for {name}')
        return

    book_text = get_book(g_id)

    with orm.Session(engine) as session:
        book = Books(
            book_id=str(g_id),
            book_title=str(g_title),
            book_author=str(g_author),
            book_text=str(book_text),
        )
        session.add(book)
        session.commit()

        print(f'{name} added to database')


def store_word(u_w: str):
    try:
        u_def = get_word_definitions(u_w)

        try:
            now = datetime.now()

            for defi in u_def:
                with orm.Session(engine) as session:
                    w = Word(
                        word=str(u_w),
                        meaning=str(defi),
                        lookups=[],
                    )
                session.add(w)
                session.commit()

                print(f'{u_w} word added to database')

        except CurrentTimeError:
            print('Error getting current date/time')
    except NoDefinition:
        print('No definition found')

        # FINISH THIS

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

# Make more for the validation i.e. if get ids returns none do something about that