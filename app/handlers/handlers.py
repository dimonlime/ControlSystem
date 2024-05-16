from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients
from app.keyboards import static_keyboards as static_kb

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.clear()
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как отправляющая сторона',
            reply_markup=static_kb.sender_keyboard)
    elif message.from_user.id in recipients:
        await state.clear()
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как принимающая сторона',
            reply_markup=static_kb.recipient_keyboard)


@router.message(F.text == 'Заказы')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Выберите действие:', reply_markup=static_kb.orders_keyboard)


@router.message(F.text == 'Назад')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Вы вернулись на главную страницу', reply_markup=static_kb.sender_keyboard)