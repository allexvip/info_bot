from aiogram import types, Dispatcher
from create_bot import *
from db.sqlite_db import *
from aiogram.utils.callback_data import CallbackData
from keyboards import kb_client
from aiogram.types import ReplyKeyboardRemove
from db import sqlite_db

'''******************** Client part ********************************'''


# again
async def send_projects_list(message: types.Message):
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.chat.id, message.chat.username, message.text))
    await send_sql(
        "INSERT INTO users (`chat_id`,`username`,`first_name`,`last_name`,`upd`) SELECT '{0}','{1}','{2}','{3}',datetime('now') where (select count(*) from `users` where chat_id='{0}')=0".format(
            message.chat.id,
            message.chat.username,
            message.chat.first_name,
            message.chat.last_name,
        ))

    await message.answer("""Предлагаю написать:

 - 🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов жмите /alimentover

💡 как вставить текст /help
 """)


@dp.message_handler(commands=['set_city'])
async def set_city(message: types.Message):
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.chat.id, message.chat.username, message.text))
    # ----keyboard
    vote_region_cb = CallbackData('vote', 'action', 'amount')  # post:<action>:<amount>
    region_data = await get_data("SELECT id,name FROM region WHERE country_id=0 ORDER BY name")
    region_dict = dict(region_data)

    def get_keyboard(dict, action):
        urlkb = types.InlineKeyboardMarkup(row_width=3)
        inline_buttons_list = []
        for key in dict.keys():
            inline_buttons_list.append(types.InlineKeyboardButton(dict[key],
                                                                  callback_data=vote_region_cb.new(action=action,
                                                                                                   amount=key), ), )
        urlkb.add(*inline_buttons_list)
        return urlkb

    await message.answer('Для совместных походов к народным избранникам в регионах нам нужно чтобы Вы выбрали Ваш регион:', reply_markup=get_keyboard(region_dict, 'region'))

    @dp.callback_query_handler(vote_region_cb.filter(action='region'))
    async def vote_up_cb_handler(query: types.CallbackQuery, callback_data: dict):
        amount = int(callback_data['amount'])
        global city_dict
        city_data = await get_data("SELECT rowid,name FROM city WHERE region_id={} ORDER BY name".format(amount))
        city_dict = dict(city_data)
        await send_sql(
            "UPDATE users set region_id = '{0}' where chat_id='{1}'".format(
                amount,
                query.message.from_user.id
            ))
        await bot.edit_message_text('Вы выбрали: {0}'.format(region_dict[amount]),
                                    query.from_user.id,
                                    query.message.message_id,
                                    reply_markup=None)
        await query.message.answer('Спасибо! 👍 Пока выбираем регион, в будущем добавим города.\n\nЧтобы исправить Ваш регион - используйте /set_city')
        await send_projects_list(query.message)
        # await bot.edit_message_text('{}'.format(region_dict[amount]), query.from_user.id,
        #                             query.message.message_id,
        #                             reply_markup=get_keyboard(city_dict, 'city'))

    @dp.callback_query_handler(vote_region_cb.filter(action='city'))
    async def vote_up_cb_handler(query: types.CallbackQuery, callback_data: dict):
        amount = int(callback_data['amount'])
        await send_sql(
            "UPDATE users set city_id = '{0}' where chat_id={1}".format(
                amount,
                query.message.from_user.id
            ))
        await bot.edit_message_text('Вы выбрали: {0}, {1}'.format(query.message.text, city_dict[amount]),
                                    query.from_user.id,
                                    query.message.message_id,
                                    reply_markup=None)
        await query.message.answer('Спасибо! 👍\n\nЧтобы исправить Ваш регион и город используйте /set_city')
        await send_projects_list(query.message)


@dp.message_handler(commands=['my_appeals'])
async def send_my_appeals(message: types.Message):
    await message.answer(str(message.chat.id) + '\n\n' + message.text)
    list = await get_users_votes('alijail')
    for item in list:
        if item[0] == message.chat.id:
            await message.answer('Вы писали:\n\n{}'.format(item[2]))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # await message.answer(message.chat.id)
    # user_channel_status = await bot.get_chat_member(chat_id=-1001176029164, user_id=message.chat.id)
    # if user_channel_status["status"] != 'left':
    #     await message.answer('text if in group')
    # else:
    #     await message.answer('text if not in group')
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.chat.id, message.chat.username, message.text))
    await send_sql(
        "INSERT INTO users (`chat_id`,`username`,`first_name`,`last_name`,`upd`) SELECT '{0}','{1}','{2}','{3}',datetime('now') where (select count(*) from `users` where chat_id='{0}')=0".format(
            message.chat.id,
            message.chat.username,
            message.chat.first_name,
            message.chat.last_name,
        ))

    await message.answer("""Добро пожаловать!
Я помогу подать обращение в Госдуму и Совету Федерации.

Актуальные инициативы:
- 🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов жмите /alimentover

💡 как вставить текст /help
""")
    res = await get_data("select region_id from users where chat_id = {} limit 1".format(message.from_user.id))
    if res[0][0] == None:
        await set_city(message)


""" - ‼️ Жалоба на законопроекты о введении уголовного наказания за частичную неуплату алиментов жмите /alijail """


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("""Как писать обращения и жалобы в ГосДуму с помощью бота от Семейного Фронта. ВИДЕОИНСТРУКЦИЯ
https://www.youtube.com/watch?v=dWvOrnXiLkg

Видео инструкция по установке и использованию расширения для вставки текста:
https://youtu.be/hVAcztBylIc

Ссылка на само расширение: https://cloud.mail.ru/public/MuK2/CJSZQJc9w

Ещё инструкция (универсальная) по вставке текста:
https://vinadm.blogspot.com/2017/04/chrome-letterskremlinru.html

Жмите /start""")


@dp.message_handler(commands=['get_unconfirmed_votes', 'get_uv'])
async def send_unconfirmed_votes(message: types.Message):
    repo = repository.RepositorySQLite()
    repo.connection = con
    repo.cursor = cur
    votes = repo.get_unconfirmed_votes_by_chat(message.chat.id)
    text = ''
    for v in votes:
        formated_str = '{deputy} ({project_name}) - /{confirm_link}'.format(
            deputy=v.deputy.full_name,
            project_name=v.project.short_name,
            confirm_link=v.get_confirm_link()
        )
        print(formated_str)
        text += '{0}\n'.format(formated_str)

    await message.answer(text)


@dp.message_handler(regexp='(^[\/]+[a-z].*)')
async def send_project_info(message: types.Message):
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.chat.id, message.chat.username, message.text))

    # write projects content
    flag_done = False
    project = message.text.replace('/', '')
    sql = """SELECT d.rowid,`dep`,`link_send`,d.person_type FROM deps d
LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}'
WHERE v.dep_id IS null
ORDER BY RANDOM()
LIMIT 1""".format(project)
    a = await send_sql(sql)
    if not a:
        """ if all deps already used for first round then we use individual dep for user"""
        sql = """SELECT d.rowid,`dep`,`link_send`,d.person_type FROM deps d
    LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id='{1}'
    WHERE v.dep_id IS null and person_type='sf'
    ORDER BY RANDOM()
    LIMIT 1""".format(project, message.chat.id)
        a = await send_sql(sql)
        if not a:
            flag_done = True
    project_obj = await send_sql(
        "select `desc` from projects where project_code in ('{0}') limit 1".format(project))
    # project_desc = project_obj[0]

    if not flag_done:
        dep_id = str(a[0])
        dep_name = str(a[1])
        link_send = str(a[2])
        person_type = str(a[3])
        if 'sf' in person_type:
            person_type_str = "Совет Федерации"
        else:
            person_type_str = "ГосДума"

        # ----keyboard
        vote_cb = CallbackData('vote', 'action', 'amount')  # post:<action>:<amount>

        def get_keyboard(amount):
            return types.InlineKeyboardMarkup().row(
                types.InlineKeyboardButton('Отправлено 👍', callback_data=vote_cb.new(action='voted',
                                                                                      amount='/' + dep_id + '_' + project),
                                           ),
            )

        @dp.callback_query_handler(vote_cb.filter(action='voted'))
        async def vote_up_cb_handler(query: types.CallbackQuery, callback_data: dict):
            # logging.info(callback_data)
            # for write in db votes
            await send_sql(
                "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                    query.message.chat.id, query.message.chat.username, callback_data['amount']))
            project_code = callback_data['amount'].split('_')[1]
            dep_id = callback_data['amount'].split('_')[0].replace('/', '')
            await send_sql(
                "INSERT INTO votes (`chat_id`,`user_answer`,`project_code`,`dep_id`,`upd`) VALUES ('{0}','{1}','{2}','{3}',datetime('now'))".format(
                    query.message.chat.id,
                    callback_data['amount'],
                    project_code,
                    dep_id))
            await bot.edit_message_text(query.message.text, query.from_user.id, query.message.message_id,
                                        reply_markup=None)
            await query.message.answer(f"""✅ Пометил у себя. Спасибо за Ваше участие! 🙂 Вместе мы сила! 💪💪💪 """)
            await send_projects_list(query.message)

        @dp.callback_query_handler(vote_cb.filter(action='up'))
        async def vote_up_cb_handler(query: types.CallbackQuery, callback_data: dict):
            logging.info(callback_data)
            amount = int(callback_data['amount'])
            amount += 1
            await bot.edit_message_text(f'You voted up! Now you have {amount} votes.',
                                        query.from_user.id,
                                        query.message.message_id,
                                        reply_markup=get_keyboard(amount))

        @dp.callback_query_handler(vote_cb.filter(action='down'))
        async def vote_down_cb_handler(query: types.CallbackQuery, callback_data: dict):
            amount = int(callback_data['amount'])
            amount -= 1
            await bot.edit_message_text(f'You voted down! Now you have {amount} votes.',
                                        query.from_user.id,
                                        query.message.message_id,
                                        reply_markup=get_keyboard(amount))

        # ----keyboard end

        text_appeal = """Разово скачайте файл законопроекта: https://vk.cc/c7LhIc

Примерный текст обращения здесь: https://semfront.ru/prog/texter.php?case=alimentover&user={0}&face={1}

Выбираете тип 'Заявление' и обязательно приложите файл законопроекта к обращению.  """.format(
            message.from_user.id, dep_name.replace(' ', '%20'))
        await message.answer(
            f"{dep_name} ({person_type_str})\n\n{text_appeal} \n\nПишем сюда: {link_send}\n\nПосле отправки пожалуйста нажмите кнопку 'Отправлено 👍' \n\n💡 как вставить текст /help"
            , reply_markup=get_keyboard(0))
    else:
        await message.answer("""✅ Спасибо Вам за то, что вы отправили обращения всем парламентариям! 💪💪💪 
    Список актуальных инициатив /start
                         """)


@dp.message_handler(regexp='^[\/]+[\w].*[_]+[A-Za-z].*')
async def write_command(message: types.Message):
    # for write in db votes
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.chat.id, message.chat.username, message.text))
    project_code = message.text.split('_')[1]
    dep_id = message.text.split('_')[0].replace('/', '')
    await send_sql(
        "INSERT INTO votes (`chat_id`,`user_answer`,`project_code`,`dep_id`,`upd`) VALUES ('{0}','{1}','{2}','{3}',datetime('now'))".format(
            message.chat.id,
            message.text,
            project_code,
            dep_id))
    await message.answer("""✅ Пометил у себя. Спасибо за Ваше участие! 🙂 Вместе мы сила! 💪💪💪

Чтобы ещё написать другому парламентарию нажмите: /{0} .

Список актуальных инициатив /start""".format(project_code))


def register_handlers_client(dp: Dispatcher):
    dp.message_handler(set_city)
    dp.message_handler(send_my_appeals)
    dp.message_handler(send_welcome)
    dp.message_handler(send_help)
    dp.message_handler(send_unconfirmed_votes)
    dp.message_handler(send_project_info)
    dp.message_handler(write_command)
