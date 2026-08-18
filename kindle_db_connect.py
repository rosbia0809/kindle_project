import time
from kindle_database import Word, Lookup
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///kindle.db')

with Session(engine) as session:
    all_words = session.query(Word).all()

    # for word in all_words:
    #     print(word.word, word.meaning)

    recent_lookups = (session.query(Lookup).join(Word).order_by(Lookup.time_stamp.desc()).all())

    # for lookup in recent_lookups:
    #     print(lookup.word.word, lookup.book_id, lookup.count)

    thirty_days_ago = int(time.time() * 1000) - (30 * 24 * 60 * 60 * 1000)

    recent_words = (session.query(Word).join(Lookup).filter(Lookup.time_stamp > thirty_days_ago).distinct().all())

    word_list = [w.word for w in recent_words]

print(word_list)