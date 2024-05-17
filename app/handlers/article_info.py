from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database import requests as rq

from app.states.check_article import check_articles

router = Router()


"""Создание заказа--------------------------------------------------------------------------------------------------"""


@router.message(F.text == 'Информация по артикулам')
async def view_articles(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(check_articles.select_article)
        await message.answer('Выберите артикул:', reply_markup=await async_kb.all_articles())


@router.callback_query(F.data.startswith('article_'), check_articles.select_article)
async def get_article_info(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        article = str(callback.data)[8:]
        orders = await rq.get_orders_by_article(article)
        sum_all = 0
        sum_s_all = 0
        sum_m_all = 0
        sum_l_all = 0

        sum_create = 0
        sum_s_create = 0
        sum_m_create = 0
        sum_l_create = 0

        sum_job = 0
        sum_s_job = 0
        sum_m_job = 0
        sum_l_job = 0

        sum_ready = 0
        sum_s_ready = 0
        sum_m_ready = 0
        sum_l_ready = 0

        sum_log = 0
        sum_s_log = 0
        sum_m_log = 0
        sum_l_log = 0

        sum_msk = 0
        sum_s_msk = 0
        sum_m_msk = 0
        sum_l_msk = 0

        sum_warehouse = 0
        sum_s_warehouse = 0
        sum_m_warehouse = 0
        sum_l_warehouse = 0

        sum_wb_send = 0
        sum_s_wb_send = 0
        sum_m_wb_send = 0
        sum_l_wb_send = 0

        for order in orders:
            if order.order_status != 'Принято на складе WB':
                sum_all += order.S + order.M + order.L
                sum_s_all += order.S
                sum_m_all += order.M
                sum_l_all += order.L
            if order.order_status == 'Заказ создан':
                sum_create += order.S + order.M + order.L
                sum_s_create += order.S
                sum_m_create += order.M
                sum_l_create += order.L
            if order.order_status == 'Передан в работу поставщику':
                sum_job += order.S + order.M + order.L
                sum_s_job += order.S
                sum_m_job += order.M
                sum_l_job += order.L
            if order.order_status == 'Готов':
                sum_ready += order.S + order.M + order.L
                sum_s_ready += order.S
                sum_m_ready += order.M
                sum_l_ready += order.L
            if order.order_status == 'Передан в логистику':
                sum_log += order.S + order.M + order.L
                sum_s_log += order.S
                sum_m_log += order.M
                sum_l_log += order.L
            if order.order_status == 'Пришел в Москву':
                sum_msk += order.S + order.M + order.L
                sum_s_msk += order.S
                sum_m_msk += order.M
                sum_l_msk += order.L
            if order.order_status == 'Принято на складе подрядчика':
                sum_warehouse += order.S + order.M + order.L
                sum_s_warehouse += order.S
                sum_m_warehouse += order.M
                sum_l_warehouse += order.L
            if order.order_status == 'Отправлено на склад WB':
                sum_wb_send += order.S + order.M + order.L
                sum_s_wb_send += order.S
                sum_m_wb_send += order.M
                sum_l_wb_send += order.L

        await callback.message.answer(f'Артикул: {article}\n'
                                      f'Общее кол-во товара: {sum_all}\n'
                                      f'Кол-во товара размера S: {sum_s_all}\n'
                                      f'Кол-во товара размера M: {sum_m_all}\n'
                                      f'Кол-во товара размера L: {sum_l_all}\n'
                                      f'-------"Заказ создан"-------\n'
                                      f'Общее кол-во товара: {sum_create}\n'
                                      f'Кол-во товара размера S: {sum_s_create}\n'
                                      f'Кол-во товара размера M: {sum_m_create}\n'
                                      f'Кол-во товара размера L: {sum_l_create}\n'
                                      f'-------"Передан в работу поставщику"-------\n'
                                      f'Общее кол-во товара: {sum_job}\n'
                                      f'Кол-во товара размера S: {sum_s_job}\n'
                                      f'Кол-во товара размера M: {sum_m_job}\n'
                                      f'Кол-во товара размера L: {sum_l_job}\n'
                                      f'-------"Готов"-------\n'
                                      f'Общее кол-во товара: {sum_ready}\n'
                                      f'Кол-во товара размера S: {sum_s_ready}\n'
                                      f'Кол-во товара размера M: {sum_m_ready}\n'
                                      f'Кол-во товара размера L: {sum_l_ready}\n'
                                      f'-------"Передан в логистику"-------\n'
                                      f'Общее кол-во товара: {sum_log}\n'
                                      f'Кол-во товара размера S: {sum_s_log}\n'
                                      f'Кол-во товара размера M: {sum_m_log}\n'
                                      f'Кол-во товара размера L: {sum_l_log}\n'
                                      f'-------"Пришел в Москву"-------\n'
                                      f'Общее кол-во товара: {sum_msk}\n'
                                      f'Кол-во товара размера S: {sum_s_msk}\n'
                                      f'Кол-во товара размера M: {sum_m_msk}\n'
                                      f'Кол-во товара размера L: {sum_l_msk}\n'
                                      f'-------"Принято на складе подрядчика"-------\n'
                                      f'Общее кол-во товара: {sum_warehouse}\n'
                                      f'Кол-во товара размера S: {sum_s_warehouse}\n'
                                      f'Кол-во товара размера M: {sum_m_warehouse}\n'
                                      f'Кол-во товара размера L: {sum_l_warehouse}\n'
                                      f'-------"Отправлено на склад WB"-------\n'
                                      f'Общее кол-во товара: {sum_wb_send}\n'
                                      f'Кол-во товара размера S: {sum_s_wb_send}\n'
                                      f'Кол-во товара размера M: {sum_m_wb_send}\n'
                                      f'Кол-во товара размера L: {sum_l_wb_send}\n'
                                      )
    except ValueError:
        await callback.message.answer('Ошибка, попробуйте еще раз')

