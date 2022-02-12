import logging
from aiogram import executor
from create_bot import *
from db import sqlite_db

logging.basicConfig(level=logging.INFO)

async def on_startup(_):
    print('Bot online')
    sqlite_db.sql_start()

# Configure logging
logging.basicConfig(level=logging.INFO)

from handlers import client, admin, other

admin.register_handlers_admin(dp)
client.register_handlers_client(dp)
other.register_handlers_other(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)



#
# from aiogram import Bot, Dispatcher, executor, types
# from aiogram.types.chat_member import ChatMember
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.callback_data import CallbackData
#
# # logging.basicConfig(filename= LOGGING_FILE_NAME , encoding='utf-8', level=logging.DEBUG)
# API_TOKEN = TELEGRAM_BOT_API_KEY
#
# # Configure logging
# logging.basicConfig(level=logging.INFO)
#
# # Initialize bot and dispatcher
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)
# cur = con.cursor()
# admin_chatid_list = [int(item) for item in ADMIN_CHAT_ID.split(',')]
