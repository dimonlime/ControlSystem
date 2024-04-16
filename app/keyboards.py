from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database import requests as rq
import json

recipient_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Изменить статус заказа')],
    [KeyboardButton(text='Проверить чеки')]

], resize_keyboard=True)

sender_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заказ')],
    [KeyboardButton(text='Просмотреть чеки')]
], resize_keyboard=True)

test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вывести список заказов', callback_data='test')]
])

cheques_category = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все чеки', callback_data='all_chques')],
    [InlineKeyboardButton(text='Чеки с отсрочкой', callback_data='delay_cheques')],
    [InlineKeyboardButton(text='Горящие чеки', callback_data='fire_cheques')]
])

cheques_category_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Не оплаченные чеки', callback_data='unpaid_cheques')],
    [InlineKeyboardButton(text='Оплаченные чеки', callback_data='paid_cheques')]
])

select_cheque = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплатить чек', callback_data='pay_cheque')]
])


async def inline_sending_method():
    keyboard = InlineKeyboardBuilder()
    for method in id_config.sending_method:
        keyboard.add(InlineKeyboardButton(text=method, callback_data=f'method_{method}'))
    return keyboard.adjust(3).as_markup()


async def inline_order_status():
    keyboard = InlineKeyboardBuilder()
    for status in id_config.order_status:
        keyboard.add(InlineKeyboardButton(text=status, callback_data=f'status_{status}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_orders():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_orders()
    for order in data:
        keyboard.add(InlineKeyboardButton(text=f'Id заказа: "{order.id}"; Статус заказа: "{order.order_status}"',
                                          callback_data=f'edit_status_{order.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_all_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        keyboard.add(InlineKeyboardButton(text=f'ID чека: "{cheque.id}"; Статус чека: "{cheque.cheque_status}"',
                                          callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_delay_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.delay_cheques()
    for cheque in data:
        keyboard.add(InlineKeyboardButton(text=f'ID чека: "{cheque.id}"; Статус чека: "{cheque.cheque_status}"',
                                          callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_fire_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        cheque_date = datetime.strptime(cheque.date, "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - cheque_date) >= timedelta(days=14) and (cheque.cheque_status == 'По чеку имеется отсрочка'
                                                                    or cheque.cheque_status == 'Чек не оплачен по истечению 2 недель'):
            await rq.set_cheque_status(cheque.id, 'Чек не оплачен по истечению 2 недель')
            keyboard.add(InlineKeyboardButton(text=f'ID чека: "{cheque.id}"; Статус чека: "{cheque.cheque_status}"',
                                              callback_data=f'pay_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_unpaid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        if cheque.cheque_status == 'По чеку имеется отсрочка' or cheque.cheque_status == 'Чек не оплачен по истечению 2 недель':
            keyboard.add(InlineKeyboardButton(text=f'ID чека: "{cheque.id}"; Статус чека: "{cheque.cheque_status}"',
                                              callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_paid_cheques():
    keyboard = InlineKeyboardBuilder()
    data = await rq.all_cheques()
    for cheque in data:
        if cheque.cheque_status == 'Чек оплачен':
            keyboard.add(InlineKeyboardButton(text=f'ID чека: "{cheque.id}"; Статус чека: "{cheque.cheque_status}"',
                                              callback_data=f'view_cheque_{cheque.id}'))
    return keyboard.adjust(1).as_markup()


async def inline_available_orders():
    keyboard = InlineKeyboardBuilder()
    data = await rq.available_orders()
    for order in data:
        keyboard.add(InlineKeyboardButton(text=f'Id заказа: {order.id}; Дата заказа {order.date}',
                                          callback_data=f'{order.id}'))
    return keyboard.adjust(1).as_markup()
