from datetime import datetime

from app.database.models import async_session
from app.database.models import Cheque, Order, Fish, ProductCard
from sqlalchemy import select


async def create_order_db(create_date, change_date, internal_article, vendor_internal_article, quantity_s, quantity_m,
                          quantity_l, color, shop_name, sending_method, order_image):
    async with async_session() as session:
        session.add(Order(create_date=create_date, change_date=change_date, internal_article=internal_article,
                          vendor_internal_article=vendor_internal_article, quantity_s=quantity_s, quantity_m=quantity_m,
                          quantity_l=quantity_l, color=color, shop_name=shop_name, sending_method=sending_method,
                          order_image=order_image))
        await session.commit()


async def all_orders():
    async with async_session() as session:
        orders = await session.scalars(select(Order))
        return orders


async def get_order(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        return order


async def set_status(order_id, status):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.status = status
        order.change_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        await session.commit()


async def get_orders_by_article(internal_article):
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.internal_article == internal_article))
        return orders


async def insert_quantity_s(order_id, quantity_s):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.quantity_s = quantity_s
        await session.commit()


async def insert_quantity_m(order_id, quantity_m):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.quantity_m = quantity_m
        await session.commit()


async def insert_quantity_l(order_id, quantity_l):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.quantity_l = quantity_l
        await session.commit()


async def insert_sending_method(order_id, sending_method):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.sending_method = sending_method
        await session.commit()


async def mark_order(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        if order.flag:
            order.flag = False
        else:
            order.flag = True
        await session.commit()