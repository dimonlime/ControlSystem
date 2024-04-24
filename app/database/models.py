from datetime import datetime
from sqlalchemy import String, ForeignKey, Null, Text, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import json

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    delivery_id: Mapped[int] = mapped_column(nullable=True, default=None)
    date: Mapped[datetime] = mapped_column(String(25), default=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    change_date: Mapped[datetime] = mapped_column(String(25), default=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    internal_article: Mapped[str] = mapped_column(String(25), nullable=True, default=None)
    S: Mapped[int] = mapped_column(nullable=True, default=None)
    M: Mapped[int] = mapped_column(nullable=True, default=None)
    L: Mapped[int] = mapped_column(nullable=True, default=None)
    vendor_name: Mapped[str] = mapped_column(String(25), nullable=True, default=None)
    sending_method: Mapped[str] = mapped_column(String(25), nullable=True, default=None)
    order_image_id: Mapped[int] = mapped_column(nullable=True, default=None)
    order_status: Mapped[str] = mapped_column(String(25), nullable=True, default='Заказ создан')
    cheque_image_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    fish: Mapped[int] = mapped_column(nullable=True, default=None)
    sack_number: Mapped[int] = mapped_column(nullable=True, unique=True)
    fact_S: Mapped[int] = mapped_column(nullable=True, default=None)
    fact_M: Mapped[int] = mapped_column(nullable=True, default=None)
    fact_L: Mapped[int] = mapped_column(nullable=True, default=None)
    sack_images = Column(Text, nullable=True, default=None)


class Cheque(Base):
    __tablename__ = 'cheques'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(String(25), default=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    cheque_date: Mapped[datetime] = mapped_column(String(25), default=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    vendor_name: Mapped[str] = mapped_column(String(25), nullable=True, default=None)
    cheque_number: Mapped[int] = mapped_column(nullable=True, default=None)
    vendor_article: Mapped[int] = mapped_column(nullable=True, default=None)
    price: Mapped[int] = mapped_column(nullable=True, default=None)
    cheque_image_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    cheque_status: Mapped[str] = mapped_column(String(25), default='По чеку имеется отсрочка')
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    payment_image: Mapped[str] = mapped_column(String(255), nullable=True, default=None)


class Fish(Base):
    __tablename__ = 'fishes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    fish: Mapped[int] = mapped_column(nullable=True, default=None)
    date: Mapped[datetime] = mapped_column(String(25), nullable=True, default=None)
    weight: Mapped[int] = mapped_column(nullable=True, default=None)
    sack_count: Mapped[int] = mapped_column(nullable=True, default=None)
    sending_method: Mapped[str] = mapped_column(String(25), nullable=True, default=None)
    fish_image_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
