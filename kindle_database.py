import sqlalchemy
import datetime
from sqlalchemy import orm
from typing import Optional


class Base(orm.DeclarativeBase, orm.MappedAsDataclass):
    pass

class Word(Base):
    __tablename__ = "WORDS"

    word_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
        init=False,
        autoincrement=True,
    )

    word: orm.Mapped[str] = orm.mapped_column(
        unique=True,
    )

    definitions: orm.Mapped[list["Definition"]] = orm.relationship(
        back_populates="word",
        default_factory=list,
        cascade="all, delete-orphan",
    )

    lookups: orm.Mapped[list["Lookup"]] = orm.relationship(
        back_populates="word",
        default_factory=list,
    )

class Definition(Base):
    __tablename__ = "DEFINITIONS"

    __table_args__ = (
        sqlalchemy.UniqueConstraint(
            "word_id",
            "meaning",
        ),
    )

    definition_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
        init=False,
        autoincrement=True,
    )

    word_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey("WORDS.word_id"),
        init=False,
    )

    meaning: orm.Mapped[str] = orm.mapped_column()

    word: orm.Mapped["Word"] = orm.relationship(
        back_populates="definitions",
    )

class Lookup(Base):
    __tablename__ = "LOOKUPS"

    lookup_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
        init=False,
        autoincrement=True,
    )

    word_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey("WORDS.word_id"),
        init=False,
    )

    book_id: orm.Mapped[Optional[int]] = orm.mapped_column(
        sqlalchemy.ForeignKey("BOOKS.book_id"),
        default=None,
    )

    time_stamp: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default_factory=datetime.datetime.now,
    )

    word: orm.Mapped["Word"] = orm.relationship(
        back_populates="lookups",
        default=None,
    )

    book: orm.Mapped[Optional["Books"]] = orm.relationship(
        back_populates="lookups",
        default=None,
    )

class Books(Base):
    __tablename__ = "BOOKS"

    book_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
    )

    book_title: orm.Mapped[str] = orm.mapped_column()

    book_author: orm.Mapped[str] = orm.mapped_column()

    book_text: orm.Mapped[str] = orm.mapped_column()

    lookups: orm.Mapped[list["Lookup"]] = orm.relationship(
        back_populates="book",
        default_factory=list,
    )

    bookmarks: orm.Mapped[list["Bookmark"]] = orm.relationship(
        back_populates="book",
        default_factory=list,
        cascade="all, delete-orphan",
    )

class Bookmark(Base):
    __tablename__ = "BOOKMARKS"

    bookmark_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
        init=False,
        autoincrement=True,
    )

    book_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey("BOOKS.book_id"),
    )

    position: orm.Mapped[float] = orm.mapped_column()

    time_stamp: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default_factory=datetime.datetime.now,
    )

    book: orm.Mapped["Books"] = orm.relationship(
        back_populates="bookmarks",
        init=False,
    )

class WordStats(Base):
    __tablename__ = "WORD_STATS"

    stats_id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True,
        autoincrement=True,
        init=False,
    )
    word_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey("WORDS.word_id"),
    )
    times_correct: orm.Mapped[int] = orm.mapped_column(
        default=0,
    )
    times_incorrect: orm.Mapped[int] = orm.mapped_column(
        default=0,
    )
    last_tested: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default_factory=datetime.datetime.now,
    )
