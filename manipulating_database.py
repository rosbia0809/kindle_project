import sqlalchemy
from sqlalchemy import orm, func
from kindle_database import Base, Books, Word, Bookmark, Lookup, Definition, WordStats
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
            #
            # if exists:
            #     w = exists
            # else:
            #     w = Word(
            #         word=str(u_w),
            #         meaning=str(defi),
            #         lookups=[],
            #     )
            #     session.add(w)
            #     session.commit()
            #
            # lookup = Lookup(
            #     word_id=w.word_id,
            #     book_id=book_id,
            #     time_stamp=datetime.now(),
            # )
            # session.add(lookup)
            # session.commit()

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

def add_bookmark(c_book_id, position: float):
    with orm.Session(engine) as session:
        bookmark = Bookmark(
            book_id=c_book_id,
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

def add_correct(word_def):
    with orm.Session(engine) as session:
        word_data = session.query(Definition).filter_by(
            meaning=str(word_def),
        ).first()

        word_tested = session.query(WordStats).filter_by(
            word_id=word_data.word_id,
        ).first()

        if word_tested is None:
            word_tested = WordStats(
                word_id=word_data.word_id,
                times_correct=1,
            )
            session.add(word_tested)
        else:
            word_tested.times_correct += 1
        session.commit()

def add_incorrect(word_def):
    with orm.Session(engine) as session:
        word_data = session.query(Definition).filter_by(
            meaning=str(word_def),
        ).first()

        word_tested = session.query(WordStats).filter_by(
            word_id=word_data.word_id,
        ).first()

        if word_tested is None:
            word_tested = WordStats(
                word_id=word_data.word_id,
                times_incorrect=1,
            )
            session.add(word_tested)
        else:
            word_tested.times_incorrect += 1
        session.commit()

def get_most_looked_up_words():
    """Searches the database for the most looked up words in the dictionary"""
    with orm.Session(engine) as session:
        results = (
            session.query(
                Word.word,
                func.count(Lookup.lookup_id)
            )
            .join(Lookup)
            .group_by(Word.word)
            .order_by(func.count(Lookup.lookup_id).desc())
            .limit(5)
            .all()
        )

    return results

def get_test_results():
    """Returns the number of times that the user has been (in)correct in their word tester"""
    with orm.Session(engine) as session:
        all_stats = session.query(WordStats).all()

        correct = sum(
            word.times_correct for word in all_stats
        )

        incorrect = sum(
            word.times_incorrect for word in all_stats
        )

    return correct, incorrect

def get_daily_lookups(n_days=None):
    """Returns the number of lookups being done each day in the last 30 days"""
    with orm.Session(engine) as session:
        query = session.query(Lookup.time_stamp)

        if n_days is not None:
            cutoff = datetime.now() - timedelta(days=n_days)
            query = query.filter(Lookup.time_stamp >= cutoff)

        lookups = query.all()

    daily_counts = {}

    for lookup in lookups:
        day = lookup.time_stamp.date()

        if day not in daily_counts:
            daily_counts[day] = 0

        daily_counts[day] += 1

    return daily_counts

# Make more for the validation i.e. if get ids returns none do something about that