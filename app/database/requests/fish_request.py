from app.database.models import async_session
from app.database.models import Cheque, Order, Fish, ProductCard
from sqlalchemy import select


async def create_fish_db(order_id, fish_number, fish_date, weight, sack_count, sending_method, fish_image_id):
    async with async_session() as session:
        session.add(
            Fish(order_id=order_id, fish_number=fish_number, fish_date=fish_date, weight=weight, sack_count=sack_count,
                 sending_method=sending_method, fish_image_id=fish_image_id))
        await session.commit()


async def get_last_fish(order_id):
    async with async_session() as session:
        fishes = await session.scalars(select(Fish).where(Fish.order_id == order_id).order_by(Fish.id.desc()))
        return fishes


async def get_fish(shipment_id):
    async with async_session() as session:
        fish = await session.scalar(select(Fish).where(Fish.shipment_id == shipment_id))
        return fish


async def insert_shipment_id(fish_id, shipment_id):
    async with async_session() as session:
        fish = await session.scalar(select(Fish).where(Fish.id == fish_id))
        fish.shipment_id = shipment_id
        await session.commit()


async def get_all_fishes():
    async with async_session() as session:
        fishes = await session.scalars(select(Fish))
        return fishes