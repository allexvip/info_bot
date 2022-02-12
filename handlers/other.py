from aiogram import types, Dispatcher
from create_bot import *
from db.sqlite_db import *
from aiogram.utils.callback_data import CallbackData
from aiogram.types.chat_member import ChatMember

'''******************** Common part ********************************'''


# @dp.message_handler(lambda message: 'тест' in message.text)
# async def taxi(message: types.Message):
#     await message.answer('тест')

@dp.message_handler(lambda message: 'test' in message.text)
async def taxi(message: types.Message):
    answ = await bot.get_chat_member(chat_id=-613736018, user_id=message.from_user.id)
    print(answ['status'])
    await message.answer(str(answ['status']))
    # await message.delete()


@dp.message_handler()
async def echo(message: types.Message):
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.chat.id,
            message.chat.username,
            message.text))
    user_info = await bot.get_chat_member(chat_id=-613736018, user_id=message.from_user.id)
    answ_text = '@{} {}\n({} {} {})'.format(message.from_user.username, user_info['status'],
                                            message.from_user.first_name,
                                            message.from_user.last_name, message.from_user.id)
    await bot.send_message(BOT_USER_ANSWERS_CHAT_ID, answ_text)
    await message.send_copy(chat_id=BOT_USER_ANSWERS_CHAT_ID, disable_notification=True, reply_to_message_id=True)
    await message.answer('Ничего не понял. Помощь /help')
    await message.delete()


def register_handlers_other(dp: Dispatcher):
    dp.message_handler(echo)
