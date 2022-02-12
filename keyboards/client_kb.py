from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # , ReplyKeyboardRemove

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)  # one_time_keyboard=True

kb_client.add(KeyboardButton('/Start')).row(KeyboardButton('/alimentover'), KeyboardButton(
    '/help'))  # .row(KeyboardButton('Поделиться номером', request_contact=True),KeyboardButton('Отправить где я',request_location=True))
# kb_client.row(b1,b2,b3)
# kb_client.add(b1).add(b2).insert(b3)
