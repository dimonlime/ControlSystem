from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Column, DateTime, Float, create_engine, Integer

engine = create_engine('sqlite:///../db1.sqlite3', echo=True)


class Base(DeclarativeBase):
    pass


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    amount = Column(Float, nullable=True)
    date = Column(String, nullable=False)


class Income(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    amount = Column(Float, nullable=True)
    date = Column(String, nullable=False)


def create_tables(engine):
    Base.metadata.create_all(engine)
