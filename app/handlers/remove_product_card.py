from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm.exc import UnmappedInstanceError

from app.id_config import senders, recipients
from app.keyboards import static_keyboards as static_kb
from app.keyboards import async_keyboards as async_kb
from app.states.product_card import remove_product_card
from app.database import requests as rq

router = Router()


@router.message(F.text == 'Удалить карту товара')
async def add_article(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(remove_product_card.select_article)
        await message.answer('Выберите артикул:', reply_markup=await async_kb.all_articles_table())


@router.callback_query(F.data.startswith('article_'), remove_product_card.select_article)
async def check_all_orders(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        card_id = str(callback.data)[8:]
        await rq.remove_product_card(card_id)
        await callback.message.answer('Карта товара успешно удалена')
        await state.set_state(remove_product_card.select_article)
    except UnmappedInstanceError:
        await callback.message.answer('Данной карты товара не существует')

