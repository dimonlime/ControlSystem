from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database import requests as rq


recipient_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Изменить статус заказа')],
    [KeyboardButton(text='Проверить чеки')]

], resize_keyboard=True)

sender_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заказ')],
    [KeyboardButton(text='Просмотреть чеки')],
    [KeyboardButton(text='Посмотреть заказы')]
], resize_keyboard=True)

vendor_internal_article = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить', callback_data='skip')]
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
    [InlineKeyboardButton(text='Оплатить чек', callback_data='pay_cheque')],
    [InlineKeyboardButton(text='Данные заказа', callback_data='order_info')],
    [InlineKeyboardButton(text='Данные чека', callback_data='cheque_info')],
    [InlineKeyboardButton(text='Данные fish', callback_data='fish_info')],
    [InlineKeyboardButton(text='Фактические данные', callback_data='fact_info')],
    [InlineKeyboardButton(text='Все данные', callback_data='all_info')],
    [InlineKeyboardButton(text='Редактировать данные', callback_data='edit_order')],
])

view_info = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Данные заказа', callback_data='order_info')],
    [InlineKeyboardButton(text='Данные чека', callback_data='cheque_info')],
    [InlineKeyboardButton(text='Данные fish', callback_data='fish_info')],
    [InlineKeyboardButton(text='Фактические данные', callback_data='fact_info')],
    [InlineKeyboardButton(text='Все данные', callback_data='all_info')],
    [InlineKeyboardButton(text='Редактировать данные заказа', callback_data='edit_order')],
])

choose_value = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Внутренний артикул товара', callback_data='edit_product_article')],
    [InlineKeyboardButton(text='Внутренний артикул поставщика', callback_data='edit_vendor_article')],
    [InlineKeyboardButton(text='Кол-во S', callback_data='edit_s_quantity')],
    [InlineKeyboardButton(text='Кол-во M', callback_data='edit_m_quantity')],
    [InlineKeyboardButton(text='Кол-во L', callback_data='edit_l_quantity')],
    [InlineKeyboardButton(text='Цвет', callback_data='edit_color')],
    [InlineKeyboardButton(text='Название магазина', callback_data='edit_name')],
    [InlineKeyboardButton(text='Способ отправки', callback_data='edit_sending_method')]
])