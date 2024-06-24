from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram import types
import odds.app.keyboards as kb
from odds.app.parse import initial

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f'{message.from_user.first_name}, добро пожаловать', reply_markup=kb.mainKeyboard)


@router.message(F.text == 'Получить отчет')
async def check_article(message: Message):
    initial()
    await message.answer_document(document=types.FSInputFile("odds\\excel_files\\report_ODDS.xlsx"))
