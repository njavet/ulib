from sqlalchemy import ForeignKey
from typing import Optional
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            relationship)


class Base(DeclarativeBase):
    __abstract__ = True
    key: Mapped[int] = mapped_column(primary_key=True)


class Category(Base):
    __tablename__ = 'category'
    name: Mapped[str] = mapped_column(unique=True)

    emojis: Mapped[list['Emoji']] = relationship(back_populates='_category',
                                                 cascade='all, delete-orphan')


class Emoji(Base):
    __tablename__ = 'emoji'
    emoji_base: Mapped[str] = mapped_column(unique=True)
    emoji_ext: Mapped[Optional[str]] = mapped_column()
    emoji_name: Mapped[str] = mapped_column(unique=True)
    unit_name: Mapped[str] = mapped_column(unique=True)
    category: Mapped[int] = mapped_column(ForeignKey(Category.key))

    _category: Mapped['Category'] = relationship(back_populates='emojis')
    units: Mapped[list['Unit']] = relationship(back_populates='_emoji',
                                               cascade='all, delete-orphan')


class Unit(Base):
    __tablename__ = 'unit'
    unix_timestamp: Mapped[float] = mapped_column()
    emoji: Mapped[int] = mapped_column(ForeignKey(Emoji.key))

    _emoji: Mapped['Emoji'] = relationship(back_populates='units')
    messages: Mapped['Message'] = relationship(back_populates='units',
                                               cascade='all, delete-orphan')


class Message(Base):
    __tablename__ = 'message'
    payload: Mapped[str] = mapped_column()
    comment: Mapped[Optional[str]] = mapped_column()
    unit: Mapped[int] = mapped_column(ForeignKey(Unit.key))

    units: Mapped['Unit'] = relationship(back_populates='messages')


class Keiko(Base):
    __abstract__ = True
    unit: Mapped[int] = mapped_column(ForeignKey(Unit.key))
