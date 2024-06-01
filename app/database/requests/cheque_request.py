from app.database.models import async_session
from app.database.models import Cheque, Order, Fish, ProductCard
from sqlalchemy import select


async def create_cheque_db(order_id, create_date, date, shop_name, cheque_number, vendor_internal_article, price,
                           image_id):
    async with async_session() as session:
        session.add(Cheque(order_id=order_id, create_date=create_date, date=date, shop_name=shop_name,
                           cheque_number=cheque_number,
                           vendor_internal_article=vendor_internal_article, price=price, cheque_image_id=image_id))
        await session.commit()


async def get_last_cheque(order_id):
    async with async_session() as session:
        cheque = await session.scalars(select(Cheque).where(Cheque.order_id == order_id).order_by(Cheque.id.desc()))
        return cheque


async def get_cheque(shipment_id):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.shipment_id == shipment_id))
        return cheque


async def get_cheque_2(cheque_id):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.id == cheque_id))
        return cheque


async def get_all_cheques():
    async with async_session() as session:
        cheques = await session.scalars(select(Cheque))
        return cheques


async def insert_shipment_id(cheque_id, shipment_id):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.id == cheque_id))
        cheque.shipment_id = shipment_id
        await session.commit()


async def insert_payment_image(cheque_id, payment_image_id):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.id == cheque_id))
        cheque.payment_image = payment_image_id
        cheque.cheque_status = 'Чек оплачен'
        await session.commit()


async def set_status(cheque_id, status):
    async with async_session() as session:
        cheque = await session.scalar(select(Cheque).where(Cheque.id == cheque_id))
        cheque.cheque_status = status
        await session.commit()


async def get_fire_cheques():
    async with async_session() as session:
        cheques = await session.scalars(select(Cheque).where(Cheque.cheque_status == 'Чек не оплачен по истечению 2-ух недель'))
        return cheques


async def get_delay_cheques():
    async with async_session() as session:
        cheques = await session.scalars(select(Cheque).where(Cheque.cheque_status == 'По чеку имеется отсрочка'))
        return cheques


async def get_paid_cheques():
    async with async_session() as session:
        cheques = await session.scalars(select(Cheque).where(Cheque.cheque_status == 'Чек оплачен'))
        return cheques
