import asyncio
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
    create_date: Mapped[str] = mapped_column(String(25))
    change_date: Mapped[str] = mapped_column(String(25))
    internal_article: Mapped[str] = mapped_column(String(25))
    vendor_internal_article: Mapped[str] = mapped_column(String(50), nullable=True, default='Не заполнено')
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()
    color: Mapped[str] = mapped_column(String(50))
    shop_name: Mapped[str] = mapped_column(String(25))
    sending_method: Mapped[str] = mapped_column(String(25))
    order_image: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(String(25), default='Заказ не готов')
    flag: Mapped[bool] = mapped_column(default=False)


class Shipment(Base):
    __tablename__ = 'shipments'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    create_date: Mapped[str] = mapped_column(String(25))
    change_date: Mapped[str] = mapped_column(String(25), nullable=True, default=None)
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(String(25), default='Поставка отправлена')
    sending_method: Mapped[str] = mapped_column(String(25))
    sack_number: Mapped[int] = mapped_column(nullable=True, unique=True, default=None)
    fish: Mapped[int] = mapped_column(ForeignKey('fishes.id'))
    cheque: Mapped[int] = mapped_column(ForeignKey('cheques.id'))
    document_1_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    document_2_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    image_1_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    image_2_id: Mapped[str] = mapped_column(String(255), nullable=True, default=None)


class Cheque(Base):
    __tablename__ = 'cheques'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shipment_id: Mapped[int] = mapped_column(ForeignKey('shipments.id'), nullable=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    date: Mapped[str] = mapped_column(String(25))
    create_date: Mapped[str] = mapped_column(String(25))
    shop_name: Mapped[str] = mapped_column(String(25))
    cheque_number: Mapped[int] = mapped_column()
    vendor_internal_article: Mapped[int] = mapped_column()
    price: Mapped[int] = mapped_column()
    cheque_image_id: Mapped[str] = mapped_column(String(255))
    cheque_status: Mapped[str] = mapped_column(String(25), default='По чеку имеется отсрочка')
    payment_image: Mapped[str] = mapped_column(String(255), nullable=True, default=None)


class Fish(Base):
    __tablename__ = 'fishes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    shipment_id: Mapped[int] = mapped_column(ForeignKey('shipments.id'), nullable=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    fish_number: Mapped[int] = mapped_column()
    fish_date: Mapped[datetime] = mapped_column(String(25))
    weight: Mapped[int] = mapped_column()
    sack_count: Mapped[int] = mapped_column()
    sending_method: Mapped[str] = mapped_column(String(25))
    fish_image_id: Mapped[str] = mapped_column(String(255))


class ProductCard(Base):
    __tablename__ = 'product_cards'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article: Mapped[str] = mapped_column()
    image_id: Mapped[str] = mapped_column()
    color: Mapped[str] = mapped_column(String(50))
    shop_name: Mapped[str] = mapped_column(String(25))
    vendor_internal_article: Mapped[str] = mapped_column(String(50), nullable=True, default='Не заполнено')


class LogistWarehouse(Base):
    __tablename__ = 'logist_warehouse'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article: Mapped[str] = mapped_column(String(255))
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()


class FullfilmenttWarehouse(Base):
    __tablename__ = 'fullfilment_warehouse'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article: Mapped[str] = mapped_column(String(255))
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()


class WildberriesWarehouse(Base):
    __tablename__ = 'wildberries_warehouse'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article: Mapped[str] = mapped_column(String(255))
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()


class OzonWarehouse(Base):
    __tablename__ = 'ozon_warehouse'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article: Mapped[str] = mapped_column(String(255))
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()


class YandexWarehouse(Base):
    __tablename__ = 'yandex_warehouse'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article: Mapped[str] = mapped_column(String(255))
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()


class MovementHistory(Base):
    __tablename__ = 'movement_history'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    article: Mapped[str] = mapped_column(String(255))
    time: Mapped[str] = mapped_column(String(255))
    start: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    quantity_xs: Mapped[int] = mapped_column()
    quantity_s: Mapped[int] = mapped_column()
    quantity_m: Mapped[int] = mapped_column()
    quantity_l: Mapped[int] = mapped_column()
    file: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    comment: Mapped[str] = mapped_column(String(255), nullable=True)




async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 

