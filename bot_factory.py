import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TOKEN')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
