from datetime import datetime

from app.database.models import async_session
from app.database.models import LogistWarehouse
from sqlalchemy import select


async def create_logist_warehouse_db(article, quantity_xs, quantity_s, quantity_m, quantity_l):
    async with async_session() as session:
        session.add(
            LogistWarehouse(article=article, quantity_xs=quantity_xs, quantity_s=quantity_s, quantity_m=quantity_m,
                            quantity_l=quantity_l))
        await session.commit()


async def add_logist_warehouse_db(logist_id, quantity_xs, quantity_s, quantity_m, quantity_l):
    async with async_session() as session:
        logist = await session.scalar(select(LogistWarehouse).where(LogistWarehouse.id == logist_id))
        logist.quantity_xs += quantity_xs
        logist.quantity_s += quantity_s
        logist.quantity_m += quantity_m
        logist.quantity_l += quantity_l
        await session.commit()


async def get_logist_warehouse():
    async with async_session() as session:
        logist = await session.scalars(select(LogistWarehouse))
        return logist
