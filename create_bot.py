from aiogram import Bot
from aiogram.dispatcher import Dispatcher

import os
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage=MemoryStorage()
load_dotenv()

BOT_NAME = os.getenv('TELEGRAM_BOT_NAME')
BOT_USER_ANSWERS_CHAT_ID = os.getenv('BOT_USER_ANSWERS_CHAT_ID')
MAIN_CHANNEL_CHAT_ID = os.getenv('MAIN_CHANNEL_CHAT_ID')
DB_FILE_NAME = os.getenv('DB_FILE_NAME')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
admin_chatid_list = [int(item) for item in ADMIN_CHAT_ID.split(',')]

bot = Bot(token=os.getenv('TELEGRAM_API_KEY'))
dp = Dispatcher(bot,storage=storage)

con = None
cur = None