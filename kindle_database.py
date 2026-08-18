import sqlalchemy
import datetime
from gutenbergpy.parse.book import Book
from sqlalchemy import orm as orm

class Base(orm.DeclarativeBase, orm.MappedAsDataclass):
    pass

class Word(Base):
    __tablename__ = 'WORDS'

    word_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
        init=False,
        autoincrement=True,
    )
    word: orm.Mapped[str] = orm.mapped_column()
    meaning: orm.Mapped[str] = orm.mapped_column()
    lookups: orm.Mapped[list['Lookup']] = orm.relationship(
        default_factory=list,
    )

class Lookup(Base):
    __tablename__ = 'LOOKUPS'

    lookup_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
        init=False,
        autoincrement=True,
    )
    word_id: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.ForeignKey('WORDS.word_id'),
    )
    book_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey('BOOKS.book_id'),
    )

    time_stamp: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default=datetime.datetime.now(),
    )

class Books(Base):
    __tablename__ = 'BOOKS'

    book_id: orm.Mapped[str] = orm.mapped_column(
        primary_key=True,
        init=True,
    )
    book_title: orm.Mapped[str] = orm.mapped_column()
    book_author: orm.Mapped[str] = orm.mapped_column()
    book_text: orm.Mapped[str] = orm.mapped_column()
    lookups: orm.Mapped[list['Lookup']] = orm.relationship(
        default_factory=list,
    )

class Bookmark(Base):
    __tablename__ = 'BOOKMARKS'
    bookmark_id: orm.Mapped[int] = orm.mapped_column(primary_key=True, init=False, autoincrement=True)
    book_id: orm.Mapped[str] = orm.mapped_column(sqlalchemy.ForeignKey('BOOKS.book_id'))
    position: orm.Mapped[float] = orm.mapped_column()
    time_stamp: orm.Mapped[datetime.datetime] = orm.mapped_column(default_factory=datetime.datetime.now)