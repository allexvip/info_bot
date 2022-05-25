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

    await message.answer("""🔻 Предлагаю написать ещё: 🔻 

 - 🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов жмите 
 👉 /alimentover

- 🔥 Совместное воспитание - письмо Бастрыкину
👉 /copb

💡 как вставить текст /help

 """)


@dp.message_handler(commands=['set_city'])
async def set_city(message: types.Message):
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.from_user.id, message.chat.username, message.text))
    # ----keyboard
    vote_region_cb = CallbackData('vote', 'action', 'amount')  # post:<action>:<amount>
    region_data = await get_data("SELECT id,name FROM region WHERE country_id=0 ORDER BY name")
    region_dict = dict(region_data)

    def get_keyboard(dict, action):
        urlkb = types.InlineKeyboardMarkup(row_width=1)
        inline_buttons_list = []
        for key in dict.keys():
            inline_buttons_list.append(types.InlineKeyboardButton(dict[key],
                                                                  callback_data=vote_region_cb.new(action=action,
                                                                                                   amount=key), ), )
        urlkb.add(*inline_buttons_list)
        return urlkb

    await message.answer(
        'Для совместных походов к народным избранникам в регионах нам нужно чтобы Вы выбрали Ваш регион:',
        reply_markup=get_keyboard(region_dict, 'region'))

    @dp.callback_query_handler(vote_region_cb.filter(action='region'))
    async def vote_up_cb_handler(query: types.CallbackQuery, callback_data: dict):
        amount = int(callback_data['amount'])
        global city_dict
        city_data = await get_data("SELECT rowid,name FROM city WHERE region_id={} ORDER BY name".format(amount))
        city_dict = dict(city_data)
        sql = "UPDATE users set region_id = '{0}' where chat_id='{1}'".format(
            amount,
            query.from_user.id
        )
        logging.info(f'{query.from_user.id} region_id: {amount}')
        await send_sql(sql)
        await bot.edit_message_text('Вы выбрали: {0}'.format(region_dict[amount]),
                                    query.from_user.id,
                                    query.message.message_id,
                                    reply_markup=None)
        await query.message.answer(
            'Спасибо! 👍 Пока выбираем регион, в будущем добавим города.\n\nЧтобы исправить Ваш регион - используйте /set_city')
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
                query.from_user.id
            ))
        logging.info(f'{query.from_user.id} region_id: {amount}')
        await bot.edit_message_text('Вы выбрали: {0}, {1}'.format(query.message.text, city_dict[amount]),
                                    query.from_user.id,
                                    query.message.message_id,
                                    reply_markup=None)
        await query.message.answer('Спасибо! 👍\n\nЧтобы исправить Ваш регион и город используйте /set_city')
        await send_projects_list(query.message)


@dp.message_handler(commands=['my_appeals'])
async def send_my_appeals(message: types.Message):
    sql = "select count(*) from votes where chat_id='{0}'".format(message.from_user.id)
    text = 'Общее кол-во Ваших обращений о введении верхней границы алиментов: {0}\n'.format(await get_sql_one_value(sql))
    sql = """SELECT '✅' ||' '||dep  FROM votes a 
JOIN (select rowid,dep from deps order by dep) b ON b.rowid = a.dep_id
WHERE a.project_code = 'alimentover' and chat_id='{0}'
order by dep """.format(message.from_user.id)
    list = await get_sql_first_column(sql)
    for item in list:
        text += '\n' + item
    await message.answer(text)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # await message.answer(message.chat.id)
    # user_channel_status = await bot.get_chat_member(chat_id=-1001176029164, user_id=message.chat.id)
    # if user_channel_status["status"] != 'left':
    #     await message.answer('text if in group')
    # else:
    #     await message.answer('text if not in group')

    utm_source = ''
    mess_args = message.get_args()
    if mess_args:
        utm_source = mess_args

    text_err = 'Error (/start)'
    try:
        await send_sql(
            "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                message.chat.id, message.chat.username, message.text))
        await send_sql(
            "INSERT INTO users (`chat_id`,`username`,`first_name`,`last_name`,`utm_source`,`created`) SELECT '{0}','{1}','{2}','{3}','{4}',datetime('now') where (select count(*) from `users` where chat_id='{0}')=0".format(
                message.chat.id,
                message.chat.username,
                message.chat.first_name,
                message.chat.last_name,
                utm_source,
            ))
        await send_sql("update users set `username`='{1}',`first_name`='{2}',`last_name`='{3}',`upd`=datetime('now') where `chat_id`='{0}';".format(
                message.chat.id,
                message.chat.username,
                message.chat.first_name,
                message.chat.last_name,
            ))

        user_info = await bot.get_chat_member(chat_id=MAIN_CHANNEL_CHAT_ID, user_id=message.from_user.id)
        if not (user_info['status'] in ['left', 'banned', 'restricted']):
            votes_count = await sql_to_text("SELECT COUNT(*) as 'Кол-во обращений' FROM votes;", header=False)
            await message.answer("""Добро пожаловать!
🔻 Я помогу подать обращение законодателям. 🔻

‼️ Мы вместе уже написали {0} ‼️обращений(я) законодателям! 💪💪💪

Актуальные инициативы:
- 🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов 
👉 /alimentover

- 🔥 Совместное воспитание - письмо Бастрыкину
👉 /copb

💡 как вставить текст /help
        """.format(votes_count))
            res = await get_data("select region_id from users where chat_id = {} limit 1".format(message.from_user.id))
            if res[0][0] == None:
                await set_city(message)
        else:
            await message.answer("""Бот работает для участников канала "Семейный Фронт".
            
Пожалуйста вступайте в канал "Семейного Фронта" и возращайтесь назад в бота:

Жмите сюда 👉 @semfront
                    """)

    except Exception as e:
        text_err += '\n\n{0}\n@{1}\n\n{2}'.format(message.from_user.id, message.chat.username, str(e))
        await send_full_text(80387796, text_err)


""" - ‼️ Жалоба на законопроекты о введении уголовного наказания за частичную неуплату алиментов 
👉 /alijail """


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("""Как писать обращения и жалобы в ГосДуму с помощью бота от Семейного Фронта. ВИДЕОИНСТРУКЦИЯ
https://www.youtube.com/watch?v=dWvOrnXiLkg

Видео инструкция по установке и использованию расширения для вставки текста:
https://youtu.be/hVAcztBylIc

Ссылка на само расширение: https://cloud.mail.ru/public/MuK2/CJSZQJc9w

Ещё инструкция (универсальная) по вставке текста:
https://vinadm.blogspot.com/2017/04/chrome-letterskremlinru.html

Жмите 👉  /start""")


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
    if project == 'copb':
        sql = """SELECT d.rowid,`dep`,`link_send`,d.person_type
                    FROM deps d
                    LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id='{1}'
                    WHERE  "dep" LIKE  '%Бастрыкин%' and v.dep_id IS NULL  LIMIT 1""".format(project, message.chat.id)

        a = await send_sql(sql)
        if not a:
            flag_done = True
    else:
        sql = """SELECT d.rowid,`dep`,`link_send`,d.person_type 
                    FROM deps d
                    LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id='{1}'
                    WHERE  "dep" LIKE  '%Останина%'  AND d."dep" not LIKE  '%Бастрыкин%' and v.dep_id IS NULL  LIMIT 1""".format(
            project, message.chat.id)
        a = await send_sql(sql)
        if not a:
            sql = """SELECT d.rowid,`dep`,`link_send`,d.person_type 
                                FROM deps d
                                LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id='{1}'
                                WHERE  ("dep" LIKE  '%Ларионова%' or "dep" LIKE  '%Буцкая%' or "dep" LIKE  '%Вторыгина%' or "dep" LIKE  '%Дробот%' or "dep" LIKE  '%Милонов%' or "dep" LIKE  '%Коробова%')  AND d."dep" not LIKE  '%Бастрыкин%' and v.dep_id IS NULL  LIMIT 1""".format(
                project, message.chat.id)
            a = await send_sql(sql)
            if not a:
                """ regional deps for user"""
                sql = """SELECT d.rowid,`dep`,`link_send`,d.person_type FROM deps d
                                   JOIN users u ON u.chat_id='{1}' AND d.region_id=u.region_id
                                   LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id=u.chat_id
                                   WHERE v.dep_id IS NULL and person_type='deputat'
                                   ORDER BY RANDOM() LIMIT 1""".format(project, message.chat.id)
                a = await send_sql(sql)
                if not a:
                    sql = """SELECT d.rowid,`dep`,`link_send`,d.person_type FROM deps d
                                LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id={1}
                                WHERE v.dep_id IS null and person_type in('deputat','sf') 
                                ORDER BY RANDOM()
                                LIMIT 1""".format(project, message.chat.id)
                    a = await send_sql(sql)
                    if not a:
                        flag_done = True


    if not flag_done:
        dep_id = str(a[0])
        dep_name = str(a[1])
        link_send = str(a[2])
        person_type = str(a[3])
        if 'sk' in person_type:
            person_type_str = "Следственный комитет"
            url_repson = "sk"
        elif 'sf' in person_type:
            person_type_str = "Совет Федерации"
            url_repson = "sf"
        else:
            person_type_str = "ГосДума"
            url_repson = "dep"
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
            await bot.edit_message_text(query.message.text, query.from_user.id, query.message.message_id,parse_mode = types.ParseMode.HTML,
                                        reply_markup=None)
            votes_count = await get_votes_count(project_code)
            await query.message.answer("""✅ Пометил у себя. Спасибо за Ваше участие! 🙂 \n\n💪💪💪 Мы сила! 💪💪💪\n\n‼️ Вместе мы уже написали {0} обращений(я) ‼️""".format(votes_count))
            await send_projects_list(query.message)

        @dp.callback_query_handler(vote_cb.filter(action='up'))
        async def vote_up_cb_handler(query: types.CallbackQuery, callback_data: dict):
            logging.info(callback_data)
            amount = int(callback_data['amount'])
            amount += 1
            await bot.edit_message_text(f'You voted up! Now you have {amount} votes.',
                                        query.from_user.id,
                                        query.message.message_id,
                                        parse_mode = types.ParseMode.HTML,
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
        project_desc = await get_sql_one_value(
            "SELECT desc from projects where project_code in ('{0}');".format(project))
        text_appeal = """
{3}
        
👉 <b><a href='https://semfront.ru/prog/texter.php?to_person={2}&case={4}&user={0}&face={1}'>Здесь примерный текст обращения</a></b>
""".format(
            message.from_user.id,
            dep_name.replace(' ', '%20'),
            url_repson,
            project_desc,
            project
        )
        await message.answer(
            f"{dep_name} ({person_type_str})\n{text_appeal} \n 👉 <b><a href='{link_send}'>Пишем сюда</a></b>\n\n💡 как вставить текст /help\n\nПосле отправки пожалуйста нажмите кнопку 'Отправлено 👍' \n👇👇👇"
            ,parse_mode=types.ParseMode.HTML, reply_markup=get_keyboard(0))
    else:
        await message.answer("""✅ Спасибо Вам за то, что вы отправили обращения! 💪💪💪 

Список актуальных инициатив 
👉 /start
                         """)


@dp.message_handler(regexp='^[\/]+[\w].*[_]+[A-Za-z].*')
async def write_command(message: types.Message):
    # for write in db votes
    await send_sql(
        "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
            message.chat.id, message.chat.username, message.text))
    project_code = message.text.split('_')[1]
    dep_id = message.text.split('_')[0].replace('/', '')
    votes_count = await get_votes_count('project_code')[0]
    await send_sql(
        "INSERT INTO votes (`chat_id`,`user_answer`,`project_code`,`dep_id`,`upd`) VALUES ('{0}','{1}','{2}','{3}',datetime('now'))".format(
            message.chat.id,
            message.text,
            project_code,
            dep_id))
    await message.answer("""✅ Пометил у себя. Спасибо за Ваше участие! Мы уже написали обращений: {1}. 🙂 Вместе мы сила! 💪💪💪

Чтобы ещё написать другому парламентарию нажмите: 
👉 /{0} .

Список актуальных инициатив /start""".format(project_code,votes_count))


def register_handlers_client(dp: Dispatcher):
    dp.message_handler(set_city)
    dp.message_handler(send_my_appeals)
    dp.message_handler(send_welcome)
    dp.message_handler(send_help)
    dp.message_handler(send_unconfirmed_votes)
    dp.message_handler(send_project_info)
    dp.message_handler(write_command)
