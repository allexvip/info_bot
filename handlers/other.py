from aiogram import types, Dispatcher
from create_bot import *
from db.sqlite_db import *
from aiogram.utils.callback_data import CallbackData

'''******************** Common part ********************************'''

# @dp.message_handler(lambda message: 'тест' in message.text)
async def taxi(message: types.Message):
    await message.answer('тест')

# @dp.message_handler()
async def echo(message: types.Message):
    await send_sql("INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id,
                       message.chat.username,
                       message.text))

    await message.answer('Ничего не понял. Помощь /help')
    await message.delete()

def register_handlers_other(dp : Dispatcher):
    dp.message_handler(echo)