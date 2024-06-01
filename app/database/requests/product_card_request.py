from app.database.models import async_session
from app.database.models import Cheque, Order, Fish, ProductCard
from sqlalchemy import select


async def get_product_cards():
    async with async_session() as session:
        product_cards = await session.scalars(select(ProductCard))
        return product_cards


async def get_product_card(article):
    async with async_session() as session:
        product_card = await session.scalar(select(ProductCard).where(ProductCard.article == article))
        return product_card


async def create_product_card(article, vendor_article, color, shop_name, image_id):
    async with async_session() as session:
        session.add(
            ProductCard(article=article, vendor_internal_article=vendor_article, color=color, shop_name=shop_name,
                        image_id=image_id))
        await session.commit()


async def remove_product_card(article):
    async with async_session() as session:
        article = await session.scalar(select(ProductCard).where(ProductCard.article == article))
        await session.delete(article)
        await session.commit()
