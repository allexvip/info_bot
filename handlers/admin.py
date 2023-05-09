from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import *
from db.sqlite_db import *
from keyboards import admin_kb
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types.chat_member import ChatMember


'''******************** Admin part ********************************'''

'''************* State part '''


# Выход из состояний
@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ок')


"""****** edit project ******"""


class FSMAdmin_edit_project(StatesGroup):
    edit_project_code = State()
    edit_project_name = State()
    edit_project_value = State()


@dp.message_handler(commands='edit_project', state=None)
async def cm_start(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        await FSMAdmin_edit_project.edit_project_code.set()
        await message.reply('Введите код проекта без пробелов')


# Ловим ответ и пишем в словарь
@dp.message_handler(state=FSMAdmin_edit_project.edit_project_code)
async def cm_name(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_chatid_list:
        async with state.proxy() as data:
            data['project_code'] = message.text.lower()
        await FSMAdmin_edit_project.next()
        await message.reply("""Редактирование: название параметра:
        
`project_code`

`name`

`desc`

`short_name`

`activity`""", parse_mode="MARKDOWN")


@dp.message_handler(state=FSMAdmin_edit_project.edit_project_name)
async def cm_name(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_chatid_list:
        async with state.proxy() as data:
            data['name'] = message.text.lower()
        await FSMAdmin_edit_project.next()
        await message.reply("""Редактирование: значение параметра""")


@dp.message_handler(state=FSMAdmin_edit_project.edit_project_value)
async def cm_name(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_chatid_list:
        async with state.proxy() as data:
            if data['name'] == 'project_code':
                data['value'] = message.text.lower()
            else:
                data['value'] = message.text
        await sql_edit_line('projects', state)
        async with state.proxy() as data:
            await message.reply(str(data))
        await state.finish()
        await message.answer('Обновил! Спасибо!')
        # text = await sql_to_str("select * from projects")
        # await send_full_text(message.chat.id, text)
        # await message.answer('Обновил! Спасибо!')


"""****** edit project end******"""

"""****** add project ******"""


class FSMAdmin_add_project(StatesGroup):
    new_project_code = State()
    new_project_name = State()
    new_project_description = State()
    new_project_short_name = State()


# Начало диалога загрузки нового пункта меню
@dp.message_handler(commands='new_project', state=None)
async def cm_start(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        await FSMAdmin_add_project.new_project_code.set()
        await message.reply('Введите код проекта без пробелов')


# Ловим ответ и пишем в словарь
@dp.message_handler(state=FSMAdmin_add_project.new_project_code)
async def load_new_project_name(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_chatid_list:
        async with state.proxy() as data:
            data['project_code'] = message.text.lower()
        await FSMAdmin_add_project.next()
        await message.reply("""Теперь введите название проекта текстом, например:
        
🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов
        """)


# Ловим второй ответ
@dp.message_handler(state=FSMAdmin_add_project.new_project_name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_chatid_list:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin_add_project.next()
        await message.reply("""Дальше введите описание проекта текстом, например:
        
👉 <b><a href="https://vk.cc/c7LhIc">Разово скачайте файл законопроекта</a></b> 

Выбираете тип 'Заявление' и обязательно приложите файл законопроекта к обращению.""")


# Ловим третий ответ
@dp.message_handler(state=FSMAdmin_add_project.new_project_description)
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_chatid_list:
        async with state.proxy() as data:
            data['desc'] = message.text
        await FSMAdmin_add_project.next()
        await message.reply("""Укажите короткое название проекта, например
        
законопроект о введении верхней границы алиментов""")


# Ловим последний ответ и используем полученные данные
@dp.message_handler(state=FSMAdmin_add_project.new_project_short_name)
async def load_price(message: types.Message, state: FSMContext):
    if message.from_user.id in admin_chatid_list:
        async with state.proxy() as data:
            data['short_name'] = message.text

        await sql_add_line('projects', state)
        async with state.proxy() as data:
            await message.reply(str(data))
        await state.finish()
        await message.answer('Добавил! Спасибо!')


"""****** add project end ******"""

'''************* State part end'''

ID = None


# Получаем ID текущего модератора
@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Режим администрирования включен',
                           reply_markup=admin_kb.button_case_admin)
    await message.delete()


@dp.message_handler(commands=['admin'])
async def send_admin_info(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        await message.answer("""Команды администратора:

/backup_db - бэкап БД

/user_info {username} - О пользователе (chatid, username, first last names, region, последняя активность)

/new_project - Новый проект

/edit_project - Редактировать проект

/new_users - Новые пользователи
        
/top_users {project_code} - ТОП пользователей проекта

/total - всего обращений

/stat {project_name} - статистика обращений по инициативе

/appeals_rate_sf - обращения в Совет Ферации

/appeals_rate_dep - обращения в Госдуму 

/users_count - общее количество пользователей бота

/last_votes {30} {project_code} - последние 30 голосов проекта

/no_active_users - неактивные пользователи

/send_to_start_users {текст} - отправить сообщение новым пользователям бота 

/send {chat_id}|{текст} - текст для отправки пользователю по chat_id

/send_region {имя_региона}|{текст} - текст для отправки пользователю по региону

/send_all {текст} - отправить сообщение всем пользователям бота

{любой текст более 15 символов} - пересылка сообщения в чат поддержки
        """)


@dp.message_handler(commands=['stat'])
async def send_df(message: types.Message):
    project_info = None
    if message.from_user.id in admin_chatid_list:
        if ' ' in message.text:
            cur_time = await current_time()
            cur_time = cur_time.replace('-', '.')
            arg_list = message.text.split(' ')
            project_info = await get_sql_one_value(
                f"SELECT name from projects where project_code in ('{arg_list[1]}');")
            users_count_all = await get_users_count(con, cur)
            users_count_regions = await get_region_users_count(con, cur)
            appeals_count_deps = await get_sql_one_value(
                f"""SELECT COUNT(*) AS 'cnt'  FROM votes a
        JOIN deps d ON d.rowid=a.dep_id AND d.person_type='deputat'
        WHERE a.project_code='{arg_list[1]}' """)
            appeals_count_sf = await get_sql_one_value(
                f"""SELECT COUNT(*) AS 'cnt'  FROM votes a
JOIN deps d ON d.rowid=a.dep_id AND d.person_type='sf'
WHERE a.project_code='{arg_list[1]}' """)
            appeals_count_sk = await get_sql_one_value(
                f"""SELECT COUNT(*) AS 'cnt'  FROM votes a
JOIN deps d ON d.rowid=a.dep_id AND d.person_type='sk'
WHERE a.project_code='{arg_list[1]}' """)
            appeals_count_servicegov = await get_sql_one_value(
                f"""SELECT COUNT(*) AS 'cnt'  FROM votes a
JOIN deps d ON d.rowid=a.dep_id AND d.person_type='servicegov'
WHERE a.project_code='{arg_list[1]}' """)

            text = ''
            if int(appeals_count_deps) > 0:
                text += f"""
✅ Количество обращений в Госдуму: {appeals_count_deps}"""
            if int(appeals_count_sf) > 0:
                text += f"""
                
✅ Количество обращений сенаторам Совета Федерации: {appeals_count_sf}"""
            if int(appeals_count_sk) > 0:
                text += f"""
✅ Количество обращений Бастрыкину: {appeals_count_sk}"""
            if int(appeals_count_servicegov) > 0:
                text += f"""
✅ Количество обращений в Правительство России: {appeals_count_servicegov}"""

    await message.answer(f"""https://t.me/{BOT_NAME}
            
ℹ️ Статистика на {cur_time} (МСК) по инициативе:
            
{project_info}
            
✅ Общее количество пользователей бота: {users_count_all}

✅ Количество пользователей, указавших свой регион: {users_count_regions}
{text}

https://t.me/{BOT_NAME}""")


@dp.message_handler(commands=['df'])
async def send_df(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        df = await get_df('SELECT * FROM users')
        print(df)
        await message.answer("df в принте")


@dp.message_handler(commands=['backup_db'])
async def send_backup(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        await bot.send_document(message.chat.id, open(DB_FILE_NAME, 'rb'))


@dp.message_handler(commands=['user_info'])
async def send_user_info(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        username = message.text.split(' ')[1]
        sql_query = f"SELECT chat_id,username, first_name, last_name,region.name, users.upd from users left join region on region.id=users.region_id where username like '%{username}%' or first_name like '%{username}%' or last_name like '%{username}%'"
        res_str = await sql_to_str(sql_query)
        await send_full_text(message.chat.id, f"""Информация о пользователе {username}:\n{str(res_str)} """)
        # await bot.send_document(message.chat.id, open(DB_FILE_NAME, 'rb'))


@dp.message_handler(commands=['new_users'])
async def send_total(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        cur_time = await current_time()
        total_str = await sql_to_str(
            "SELECT DATE(`created`) AS 'data_time',COUNT(*) AS 'cnt',`utm_source` from users GROUP BY DATE(`created`),`utm_source` ORDER BY `data_time` desc")
        await send_full_text(message.chat.id, f"""Статистика новых пользователей на {cur_time}\n{str(total_str)} """)


@dp.message_handler(commands=['total'])
async def send_total(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        cur_time = await current_time()
        total_str = await get_total_text(
            "SELECT project_code,(SELECT b.name FROM projects b where b.project_code=a.project_code) AS 'project_name',COUNT(*) AS 'all votes',COUNT(DISTINCT `dep_id`) AS 'unique deps',COUNT(DISTINCT `chat_id`) AS 'unique users'  FROM votes a where `project_code`<>'' and `project_name`<>''GROUP BY project_code")
        await message.answer(
            f"""Статистика по обращениям к парламентариям по состоянию на {cur_time}{total_str} """)


@dp.message_handler(commands=['users_count'])
async def send_users_count(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        text = 'Общее количество пользователей:'
        text += '\n' + await get_users_count(con, cur)
        await message.answer(text)
        # по регионам
        sql = """SELECT b.cnt||' '||a.name AS answ FROM (
                SELECT u.region_id,COUNT(*) AS cnt FROM users u
                GROUP BY u.region_id) b
                JOIN region a ON a.id=b.region_id
                ORDER BY cnt desc
           """

        text = f'Кол-во пользователей по регионам:'
        text += '\nВсего ' + await get_region_users_count(con, cur) + ':'

        list = await get_sql_first_column(sql)
        for item in list:
            text += '\n' + item
        await message.answer(text)


@dp.message_handler(commands=['top_users'])
async def top_users(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        project_code = 'alimentover'
        try:
            project_code = message.text.split(' ')[1]
        except:
            pass

        sql_count = f"""SELECT 1 as 'id','project_code | ','AVG appeals by one user | ','users count'
UNION
SELECT '2',project_code,sum(cnt)/COUNT(cnt) AS 'appeals by one user',COUNT(chat_id) AS 'users' FROM (
SELECT v.project_code,chat_id,COUNT(v.project_code) AS cnt FROM votes v 
JOIN projects p ON p.project_code=v.project_code
WHERE v.project_code = '{project_code}' 
GROUP BY v.project_code,v.chat_id) a 
GROUP BY project_code ORDER BY id ASC"""
        await send_full_text(message.chat.id, await sql_to_str(sql_count))

        sql = f"""with aa AS (SELECT v.chat_id,COUNT(*) AS cnt FROM votes v WHERE v.project_code='{project_code}' GROUP BY v.chat_id HAVING cnt>20)
SELECT 
iif(username='None','chatid: '||u.chat_id,'@'||username)
||' ('||iif(u.first_name='None','',u.first_name)
||' '||iif(u.last_name='None','',u.last_name)||') '
||' всего: '||cnt||'. '
||iif(r.name is null,'',r.name) 
AS 'answ'
FROM aa
JOIN users u ON u.chat_id=aa.chat_id
LEFT JOIN region r ON r.id=u.region_id
ORDER BY cnt DESC
    """
        text = f'ТОП пользователи инициативы {project_code}:'
        list = await get_sql_first_column(sql)
        for item in list:
            text += '\n\n' + item
        await send_full_text(message.chat.id, text)


@dp.message_handler(commands=['last_votes'])
async def send_last_votes(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        cnt = 30
        project_code = 'alimentover'
        try:
            cnt = message.text.split(' ')[1]
            try:
                project_code = message.text.split(' ')[2]
            except:
                pass
        except:
            pass
        finally:
            sql = f"""SELECT v.upd||' @'||u.username||' ('||u.chat_id||' '||u.first_name||' '||u.last_name||') -> '||d.dep AS 'answ' FROM votes v
        JOIN users u ON u.chat_id=v.chat_id
        JOIN deps d ON d.rowid=v.dep_id
        WHERE v.project_code='{project_code}'
        ORDER BY v.upd DESC LIMIT {cnt}
        """
            text = f'Последние голоса инициативы {project_code}:'
            list = await get_sql_first_column(sql)
            for item in list:
                text += '\n\n' + item
            await send_full_text(message.chat.id, text)


@dp.message_handler(commands=['no_active_users'])
async def no_active_users(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        sql = """SELECT '@'||u.username||' ('||u.first_name||' '||u.last_name||') '||u.chat_id||'\n'||msg AS 'answ' from users u
JOIN (
SELECT a.chat_id,a.message,max(a.upd),group_concat(message) as msg,COUNT(*) AS 'cnt' FROM logs a GROUP BY a.chat_id HAVING message IN ('/start') AND cnt<7
) b ON b.chat_id=u.chat_id
    """
        text = 'Неактивные пользователи:'
        list = await get_sql_first_column(sql)
        for item in list:
            text += '\n\n' + item
        await send_full_text(message.chat.id, text)


@dp.message_handler(commands=['appeals_rate_sf'])
async def send_appeals_rate_sf(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        text = ''

        sql = """SELECT COUNT(DISTINCT a.chat_id) AS 'cnt'  FROM votes a 
JOIN deps b ON b.rowid = a.dep_id  AND b.person_type='sf'
WHERE a.project_code='alimentover'"""
        text += """Пользователей написавших в Совет Федерации: """
        list = await get_sql_first_column(sql)
        text += list[0]

        sql = """SELECT COUNT(*) AS 'cnt'  FROM votes a
JOIN deps d ON d.rowid=a.dep_id AND d.person_type='sf'
WHERE a.project_code='alimentover' """
        text += """\nВсего обращений сенаторам Совета Федерации: """
        list = await get_sql_first_column(sql)
        text += list[0]
        # await send_full_text(message.from_user.id, text)

        await send_full_text(message.from_user.id, text)

        sql = """SELECT b.cnt ||' '||d.dep AS 'asw' FROM deps d
        JOIN (SELECT a.dep_id,COUNT(*) AS cnt FROM votes a GROUP BY a.dep_id) b ON d.rowid=b.dep_id
        WHERE d.person_type IN ('sf') ORDER BY `cnt` desc """
        text = """Статистика обращений по сенаторам Совета Федерации:
Кол-во обращений парламентарию СФ: """
        list = await get_sql_first_column(sql)
        for item in list:
            text += '\n' + item
        await send_full_text(message.from_user.id, text)  # message.answer(text)


@dp.message_handler(commands=['appeals_rate_dep'])
async def send_appeals_rate_dep(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        text = ''

        sql = """SELECT COUNT(DISTINCT a.chat_id) AS 'cnt'  FROM votes a 
JOIN deps b ON b.rowid = a.dep_id  AND b.person_type='deputat'
WHERE a.project_code='alimentover'"""
        text += """Пользователей написавших в Госдуму: """
        list = await get_sql_first_column(sql)
        text += list[0]

        sql = """SELECT COUNT(*) AS 'cnt'  FROM votes a
        JOIN deps d ON d.rowid=a.dep_id AND d.person_type='deputat'
        WHERE a.project_code='alimentover' """
        text += """\nВсего обращений в Госдуму: """
        list = await get_sql_first_column(sql)
        text += list[0]
        await send_full_text(message.from_user.id, text)

        sql = """SELECT b.cnt ||' '||d.dep AS 'asw' FROM deps d
    JOIN (SELECT a.dep_id,COUNT(*) AS cnt FROM votes a GROUP BY a.dep_id) b ON d.rowid=b.dep_id
    WHERE d.person_type IN ('deputat') ORDER BY `cnt` desc """
        text = 'Кол-во обращений парламентарию СФ:'
        list = await get_sql_first_column(sql)
        for item in list:
            text += '\n' + item
        await send_full_text(message.from_user.id, text)  # message.answer(text)


@dp.message_handler(lambda message: '/send ' in message.text)
async def send_to_user(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        text_err = 'Error (send)'
        if message.from_user.id in admin_chatid_list:
            msg = message.text
            data_list = msg.split('/send ')[1].split('|')
            to_chat_id = data_list[0]
            message_for_user = data_list[1]
            # print(to_chat_id + ' ' + message_for_user)
            try:
                await bot.send_message(to_chat_id, message_for_user)
                await message.answer('Отправлено пользователю: ' + str(to_chat_id))
            except Exception as e:
                text_err += '\n\n' + str(e)
                await send_full_text(80387796, text_err)
    else:
        await message.answer('Ничего не понял. Помощь /help')


@dp.message_handler(commands=['send_all'])
async def send_all(message: types.Message):
    text_err = 'Error (send all)'
    if message.from_user.id in admin_chatid_list:
        message_for_users = message.text.replace('/send_all ', '')
        chat_id_list = await get_all_users(con, cur)
        for item_chat_id in chat_id_list:
            print(item_chat_id + ' ' + message_for_users)
            try:
                await bot.send_message(item_chat_id, message_for_users)
            except Exception as e:
                text_err += '\n\n' + str(e)

        await message.answer('Отправили пользователям ' + str(chat_id_list))
        await send_full_text(80387796, 'Отправили пользователям ' + str(chat_id_list))
        await send_full_text(80387796, text_err)
    else:
        await message.answer('Ничего не понял. Помощь /help')


@dp.message_handler(commands=['send_region'])
async def send_to_start_users(message: types.Message):
    text_err = 'Error (send_region)'
    if message.from_user.id in admin_chatid_list:
        region_like = message.text.split('|')[0].split(' ')[1]
        message_for_users = message.text.split('|')[1]
        sql = f"""SELECT a.chat_id,a.username,b.name,b.chat_name,b.chat_url FROM users a
JOIN region b ON b.id=a.region_id and lower(b.name) LIKE '%{region_like[1:]}%'"""
        chat_id_list = await get_sql_first_column(sql)
        for item_chat_id in chat_id_list:
            print(item_chat_id + ' ' + message_for_users)
            # await bot.send_message(80387796, '/send_region :\n'+item_chat_id+'\n' + message_for_users)
            try:
                await bot.send_message(item_chat_id, message_for_users)
            except Exception as e:
                text_err += '\n\n' + str(e)

        await message.answer('Отправили пользователям ' + str(chat_id_list))
        await send_full_text(80387796, 'Отправили пользователям ' + str(chat_id_list))
        await send_full_text(80387796, text_err)
    else:
        await message.answer('Ничего не понял. Помощь /help')


@dp.message_handler(commands=['send_to_start_users'])
async def send_to_start_users(message: types.Message):
    text_err = 'Error (send_to_start_users)'
    if message.from_user.id in admin_chatid_list:
        message_for_users = message.text.replace('/send_to_start_users ', '')
        sql = """SELECT a.chat_id,a.message,max(a.upd) FROM logs a GROUP BY a.chat_id HAVING message IN ('/start') """
        chat_id_list = await get_sql_first_column(sql)
        for item_chat_id in chat_id_list:
            print(item_chat_id + ' ' + message_for_users)
            # await bot.send_message(80387796, '/send_all :\n'+item_chat_id+'\n' + message_for_users)
            try:
                await bot.send_message(item_chat_id, message_for_users)
            except Exception as e:
                text_err += '\n\n' + str(e)

        await message.answer('Отправили пользователям ' + str(chat_id_list))
        await send_full_text(80387796, 'Отправили пользователям ' + str(chat_id_list))
        await send_full_text(80387796, text_err)
    else:
        await message.answer('Ничего не понял. Помощь /help')


# - - - - - - - - - - - - - - - - - - - - - - - - - -

def register_handlers_admin(dp: Dispatcher):
    dp.message_handler(send_admin_info)
    dp.message_handler(send_df)
    dp.message_handler(send_total)
    dp.message_handler(send_users_count)
    dp.message_handler(send_last_votes)
    dp.message_handler(no_active_users)
    dp.message_handler(send_appeals_rate_sf)
    dp.message_handler(send_appeals_rate_dep)
    dp.message_handler(send_all)
    dp.message_handler(send_to_start_users)
