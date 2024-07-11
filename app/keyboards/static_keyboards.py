from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database import requests as rq


admin_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Система учета'), KeyboardButton(text='Система ОДДС')],
], resize_keyboard=True)

recipient_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать поставку')],
    [KeyboardButton(text='Чеки')]

], resize_keyboard=True)

sender_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заказ')],
    [KeyboardButton(text='Чеки'), KeyboardButton(text='Заказы')],
    [KeyboardButton(text='Информация по артикулам'), KeyboardButton(text='Редактировать данные')],
], resize_keyboard=True)

add_article_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить карту товара'), KeyboardButton(text='Удалить карту товара'), KeyboardButton(text='Список карт товара')],
    [KeyboardButton(text='Назад')]
], resize_keyboard=True)

# orders_keyboard = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Текущие заказы'), KeyboardButton(text='Изменить статус поставки'), KeyboardButton(text='Архив заказов')],
#     [KeyboardButton(text='Назад')],
# ], resize_keyboard=True)

orders_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Текущие заказы'), KeyboardButton(text='Архив заказов')],
    [KeyboardButton(text='Назад')],
], resize_keyboard=True)

cheques_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Горящие чеки'), KeyboardButton(text='Чеки с отсрочкой'), KeyboardButton(text='Архив чеков')],
    [KeyboardButton(text='Назад')],
], resize_keyboard=True)

pay_cheque = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплатить чек', callback_data='pay_cheque')],
], resize_keyboard=True)

vendor_internal_article = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить', callback_data='skip')]
])

recipient_order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить товар', callback_data='create_shipment')]
])

active_order_actions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Список поставок', callback_data='view_shipments')],
    [InlineKeyboardButton(text='Все данные', callback_data='all_data_order')],
    [InlineKeyboardButton(text='Отметить', callback_data='mark_order')],
    [InlineKeyboardButton(text='Отправить в архив', callback_data='close_order')],
])

archive_order_actions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Список поставок', callback_data='view_shipments')],
    [InlineKeyboardButton(text='Все данные', callback_data='all_data_order')],
])

close_order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить в архив', callback_data='send_to_archive'), InlineKeyboardButton(text='Назад', callback_data='back')],
])

shipment_actions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все данные', callback_data='all_data_shipment')],
])

edit_data = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Редактировать заказ'), KeyboardButton(text='Редактировать поставку')],
    [KeyboardButton(text='Назад')],
], resize_keyboard=True)

edit_order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кол-во товара S', callback_data='edit_quantity_s')],
    [InlineKeyboardButton(text='Кол-во товара M', callback_data='edit_quantity_m')],
    [InlineKeyboardButton(text='Кол-во товара L', callback_data='edit_quantity_l')],
    [InlineKeyboardButton(text='Способ отправки', callback_data='edit_sending_method')],
])


edit_shipment = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кол-во товара S', callback_data='edit_quantity_s')],
    [InlineKeyboardButton(text='Кол-во товара M', callback_data='edit_quantity_m')],
    [InlineKeyboardButton(text='Кол-во товара L', callback_data='edit_quantity_l')],
    [InlineKeyboardButton(text='Дата чека', callback_data='edit_cheque_date')],
    [InlineKeyboardButton(text='Номер чека', callback_data='edit_cheque_date')],
    [InlineKeyboardButton(text='Артикул поставщика', callback_data='edit_cheque_date')],
    [InlineKeyboardButton(text='Цена', callback_data='edit_price')],
    [InlineKeyboardButton(text='Номер FIS`', callback_data='edit_cheque_date')],
    [InlineKeyboardButton(text='Дата FIS`', callback_data='edit_cheque_date')],
    [InlineKeyboardButton(text='Вес', callback_data='edit_cheque_date')],
    [InlineKeyboardButton(text='Кол-во мешков', callback_data='edit_cheque_date')],
])