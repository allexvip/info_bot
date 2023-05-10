import asyncio
import aioschedule
import logging
from aiogram import executor
from create_bot import *
from db import sqlite_db

logging.basicConfig(level=logging.INFO)


async def make_backup():
    await bot.send_document(BACKUP_CHAT_ID, open(DB_FILE_NAME, 'rb'))


async def scheduler():
    aioschedule.every().day.at("02:00").do(make_backup)
    print('Set backup at 02:00')
    while True:
        # print('check time')
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    print('Bot online')
    sqlite_db.sql_start()
    asyncio.create_task(scheduler())


# Configure logging
logging.basicConfig(level=logging.INFO)

from handlers import client, admin, other

admin.register_handlers_admin(dp)
client.register_handlers_client(dp)
other.register_handlers_other(dp)

executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
