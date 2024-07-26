from datetime import datetime

from app.database.models import async_session
from app.database.models import Cheque, Order, Fish, ProductCard, Shipment
from sqlalchemy import select


async def create_shipment_db(order_id, create_date, quantity_xs, quantity_s, quantity_m, quantity_l, sending_method, fish_id,
                             cheque_id):
    async with async_session() as session:
        session.add(
            Shipment(order_id=order_id, create_date=create_date, change_date=create_date, quantity_xs=quantity_xs, quantity_s=quantity_s, quantity_m=quantity_m,
                     quantity_l=quantity_l,
                     sending_method=sending_method, fish=fish_id, cheque=cheque_id))
        await session.commit()


async def get_last_ship(order_id):
    async with async_session() as session:
        shipment = await session.scalars(
            select(Shipment).where(Shipment.order_id == order_id).order_by(Shipment.id.desc()))
        return shipment


async def get_shipments(order_id):
    async with async_session() as session:
        shipments = await session.scalars(select(Shipment).where(Shipment.order_id == order_id))
        return shipments


async def get_shipment(shipment_id):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        return shipment


async def get_all_shipments():
    async with async_session() as session:
        shipments = await session.scalars(select(Shipment))
        return shipments


async def insert_image_1(shipment_id, image_id):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.image_1_id = image_id
        await session.commit()


async def insert_image_2(shipment_id, image_id):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.image_2_id = image_id
        await session.commit()


async def insert_document_1(shipment_id, document_id):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.document_1_id = document_id
        await session.commit()


async def insert_document_2(shipment_id, document_id):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.document_2_id = document_id
        await session.commit()


async def set_status(shipment_id, status):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.status = status
        shipment.change_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        await session.commit()


async def insert_quantity_s(shipment_id, quantity_s):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.quantity_s = quantity_s
        await session.commit()


async def insert_quantity_m(shipment_id, quantity_m):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.quantity_m = quantity_m
        await session.commit()


async def insert_quantity_l(shipment_id, quantity_l):
    async with async_session() as session:
        shipment = await session.scalar(select(Shipment).where(Shipment.id == shipment_id))
        shipment.quantity_l = quantity_l
        await session.commit()
