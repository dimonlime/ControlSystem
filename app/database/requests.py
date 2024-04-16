from app.database.models import async_session
from app.database.models import Cheque, Order
from sqlalchemy import select


async def create_cheque_db(vendor_name, price, image, order_id):
    async with async_session() as session:
        session.add(Cheque(vendor_name=vendor_name, price=price, cheque_image_id=image, order_id=order_id))
        await session.commit()


async def create_order_db(internal_article, s, m, l, vendor_name, sending_method, image_id):
    async with async_session() as session:
        session.add(Order(internal_article=internal_article, S=s, M=m, L=l, vendor_name=vendor_name,
                          sending_method=sending_method, order_image_id=image_id))
        await session.commit()


async def get_cheque(cheque_id):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.id == cheque_id))
        return cheque


async def get_order(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        return order


async def set_order_cheque_image(order_id, cheque_image_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.cheque_image_id = cheque_image_id
        await session.commit()


async def available_orders():
    async with async_session() as session:
        orders = await session.scalars(select(Order).where(Order.order_status == 'Передан в логистику'))
        if not orders:
            return -1
        else:
            return orders


async def all_orders():
    async with async_session() as session:
        orders = await session.scalars(select(Order))
        if not orders:
            return -1
        else:
            return orders


async def all_cheques():
    async with async_session() as session:
        cheques = await session.scalars(select(Cheque))
        return cheques


async def delay_cheques():
    async with async_session() as session:
        cheques = await session.scalars(select(Cheque).where(Cheque.cheque_status == 'По чеку имеется отсрочка'))
        return cheques


async def set_payment_image(cheque_id, payment_image_id):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.id == cheque_id))
        cheque.payment_image = payment_image_id
        await session.commit()


async def set_cheque_status(cheque_id, cheque_status):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.id == cheque_id))
        cheque.cheque_status = cheque_status
        await session.commit()


async def edit_order_status(order_id, order_status):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.order_status = order_status
        await session.commit()


async def set_order_fish(order_id, fish_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        order.fish = fish_id
        await session.commit()


async def get_fish(order_id):
    async with async_session() as session:
        order = await session.scalar(select(Order).where(Order.id == order_id))
        return order.fish
