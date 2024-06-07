from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.id_config import senders
from app.keyboards import async_keyboards as async_kb
from app.keyboards import static_keyboards as static_kb
from app.database.requests import order_request as order_rq
from app.database.requests import shipment_request as ship_rq

from app.states.article import check_article

router = Router()


@router.message(F.text == 'Информация по артикулам')
async def view_articles(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.set_state(check_article.select_article)
        await message.answer('Выберите артикул:', reply_markup=await async_kb.all_articles())


@router.callback_query(F.data.startswith('article_'), check_article.select_article)
async def get_article_info(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        article = str(callback.data)[8:]
        orders = await order_rq.get_orders_by_article(article)
        sum_all = 0
        sum_s_all = 0
        sum_m_all = 0
        sum_l_all = 0

        sum_send = 0
        sum_s_send = 0
        sum_m_send = 0
        sum_l_send = 0

        sum_moscow = 0
        sum_s_moscow = 0
        sum_m_moscow = 0
        sum_l_moscow = 0

        sum_vendor = 0
        sum_s_vendor = 0
        sum_m_vendor = 0
        sum_l_vendor = 0

        sum_wb = 0
        sum_s_wb = 0
        sum_m_wb = 0
        sum_l_wb = 0

        for order in orders:
            shipments = await ship_rq.get_shipments(order.id)
            for shipment in shipments:
                if shipment.status != 'Принята на складе WB':
                    sum_all += shipment.quantity_s + shipment.quantity_m + shipment.quantity_l
                    sum_s_all += shipment.quantity_s
                    sum_m_all += shipment.quantity_m
                    sum_l_all += shipment.quantity_l
                if shipment.status == 'Поставка отправлена':
                    sum_send += shipment.quantity_s + shipment.quantity_m + shipment.quantity_l
                    sum_s_send += shipment.quantity_s
                    sum_m_send += shipment.quantity_m
                    sum_l_send += shipment.quantity_l
                if shipment.status == 'Пришла в Москву':
                    sum_moscow += shipment.quantity_s + shipment.quantity_m + shipment.quantity_l
                    sum_s_moscow += shipment.quantity_s
                    sum_m_moscow += shipment.quantity_m
                    sum_l_moscow += shipment.quantity_l
                if shipment.status == 'Принята на складе ПД':
                    sum_vendor += shipment.quantity_s + shipment.quantity_m + shipment.quantity_l
                    sum_s_vendor += shipment.quantity_s
                    sum_m_vendor += shipment.quantity_m
                    sum_l_vendor += shipment.quantity_l
                if shipment.status == 'Отправлена на склад WB':
                    sum_wb += shipment.quantity_s + shipment.quantity_m + shipment.quantity_l
                    sum_s_wb += shipment.quantity_s
                    sum_m_wb += shipment.quantity_m
                    sum_l_wb += shipment.quantity_l
        text = (f'Артикул: {article}\n'
               f'Всего: {sum_all} шт\n'
               f'S: {sum_s_all} M: {sum_m_all} L: {sum_l_all}\n')
        if sum_send != 0:
            text += (f'----------------------------------\n'
                    f'Статус: "Поставка отправлена"\n'
                    f'Общее кол-во товара: {sum_send}\n'
                    f'S: {sum_s_send} M: {sum_m_send} L: {sum_l_send}\n')
        if sum_moscow != 0:
            text += (f'----------------------------------\n'
                     f'Статус: "Пришла в Москву"\n'
                     f'Общее кол-во товара: {sum_moscow}\n'
                     f'S: {sum_s_moscow} M: {sum_m_moscow} L: {sum_l_moscow}\n')
        if sum_vendor != 0:
            text += (f'----------------------------------\n'
                     f'Статус: "Принята на складе ПД"\n'
                     f'Общее кол-во товара: {sum_vendor}\n'
                     f'S: {sum_s_vendor} M: {sum_m_vendor} L: {sum_l_vendor}\n')
        if sum_wb != 0:
            text += (f'----------------------------------\n'
                     f'Статус: "Отправлена на склад WB"\n'
                     f'Общее кол-во товара: {sum_wb}\n'
                     f'S: {sum_s_wb} M: {sum_m_wb} L: {sum_l_wb}\n')
        await callback.message.answer(text, parse_mode='Markdown')
    except ValueError:
        await callback.message.answer('Ошибка, попробуйте еще раз')