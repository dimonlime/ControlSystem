from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.id_config import senders, recipients, admin
from app.keyboards import static_keyboards as static_kb
from app.states.product_card import create_product_card
from odds.app import keyboards as kb

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if message.from_user.id in senders and message.from_user.id not in admin:
        await state.clear()
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как отправляющая сторона',
            reply_markup=static_kb.sender_keyboard)
    elif message.from_user.id in recipients and message.from_user.id not in admin:
        await state.clear()
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как принимающая сторона',
            reply_markup=static_kb.recipient_keyboard)
    elif message.from_user.id in admin:
        await state.clear()
        await message.answer(
            f'{message.from_user.first_name} добро пожаловать, вы авторизованы как администратор',
            reply_markup=static_kb.admin_keyboard)
    else:
        await message.answer('У вас не доступа к этой функции.')


@router.message(Command(commands='create_product_card'))
async def start(message: Message, state: FSMContext):
    if message.from_user.id in senders:
        await state.clear()
        await message.answer(
            f'Меню создания карты товара',
            reply_markup=static_kb.add_article_keyboard)
    else:
        await state.clear()
        await message.answer('У вас нет доступа к этой функции')


@router.message(F.text == 'Заказы')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Выберите действие:', reply_markup=static_kb.orders_keyboard)


@router.message(F.text == 'Чеки')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Выберите действие:', reply_markup=static_kb.cheques_keyboard)


@router.message(F.text == 'Система учета')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in admin and message.from_user.id in senders:
        await message.answer('Выберите действие:', reply_markup=static_kb.sender_keyboard)
    elif message.from_user.id in admin and message.from_user.id in recipients:
        await message.answer('Выберите действие:', reply_markup=static_kb.recipient_keyboard)
    else:
        await message.answer('У вас нет доступа к данной функции')


@router.message(F.text == 'Система ОДДС')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in admin:
        await message.answer('Выберите действие:', reply_markup=kb.mainKeyboard)
    else:
        await message.answer('У вас нет доступа к данной функции')


@router.message(F.text == 'Назад')
async def check_all_orders(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in senders:
        await message.answer('Вы вернулись на главную страницу', reply_markup=static_kb.sender_keyboard)
    elif message.from_user.id in recipients:
        await message.answer('Вы вернулись на главную страницу', reply_markup=static_kb.recipient_keyboard)
