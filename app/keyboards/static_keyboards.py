from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import id_config
from app.database import requests as rq


recipient_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать поставку')],
    [KeyboardButton(text='Чеки')]

], resize_keyboard=True)

sender_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заказ')],
    [KeyboardButton(text='Чеки'), KeyboardButton(text='Заказы')],
    # [KeyboardButton(text='Информация по артикулам')]
], resize_keyboard=True)

add_article_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить карту товара'), KeyboardButton(text='Удалить карту товара'), KeyboardButton(text='Список карт товара')],
    [KeyboardButton(text='Назад')]
], resize_keyboard=True)

orders_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Текущие заказы'), KeyboardButton(text='Изменить статус поставки'), KeyboardButton(text='Архив заказов')],
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

order_actions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Список поставок', callback_data='view_shipments')],
    [InlineKeyboardButton(text='Все данные', callback_data='all_data_order')],
    # [InlineKeyboardButton(text='Редактировать данные', callback_data='edit_data')]
])

shipment_actions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все данные', callback_data='all_data_shipment')],
])
