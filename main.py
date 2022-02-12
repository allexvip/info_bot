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

