from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

mainKeyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Получить отчет')]
], resize_keyboard=True, input_field_placeholder='Выберите действие...')