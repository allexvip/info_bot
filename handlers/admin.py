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

/new_users - new users
        
/top_users - ТОП пользователей

/total - всего обращений

/stat {project_name} - статистика обращений по инициативе

/appeals_rate_sf - обращения в Совет Ферации

/appeals_rate_dep - обращения в Госдуму 

/users_count - общее количество пользователей бота

/last_votes - последние голоса

/no_active_users - неактивные пользователи

/send_to_start_users {текст} - отправить сообщение новым пользователям бота 

/send {chat_id}|{текст} - текст для отправки пользователю по chat_id

/send_all {текст} - отправить сообщение всем пользователям бота

{любой текст более 15 символов} - пересылка сообщения в чат поддержки
        """)




@dp.message_handler(commands=['stat'])
async def send_df(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        if ' ' in message.text:
            cur_time = await current_time()
            cur_time = cur_time.replace('-', '.')
            arg_list = message.text.split(' ')
            project_info = await get_sql_one_value(
                "SELECT name from projects where project_code in ('{0}');".format(arg_list[1]))
            users_count_all = await get_users_count(con, cur)
            users_count_regions = await get_region_users_count(con, cur)
            appeals_count_deps = await get_sql_one_value(
                """SELECT COUNT(*) AS 'cnt'  FROM votes a
        JOIN deps d ON d.rowid=a.dep_id AND d.person_type='deputat'
        WHERE a.project_code='{0}' """.format(arg_list[1]))
            appeals_count_sf = await get_sql_one_value(
                """SELECT COUNT(*) AS 'cnt'  FROM votes a
JOIN deps d ON d.rowid=a.dep_id AND d.person_type='sf'
WHERE a.project_code='{0}' """.format(arg_list[1]))
            appeals_count_sk = await get_sql_one_value(
                """SELECT COUNT(*) AS 'cnt'  FROM votes a
JOIN deps d ON d.rowid=a.dep_id AND d.person_type='sk'
WHERE a.project_code='{0}' """.format(arg_list[1]))

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

    await message.answer("""https://t.me/{4}
            
ℹ️ Статистика на {3} (МСК) по инициативе:
            
{0}
            
✅ Общее количество пользователей бота: {1}

✅ Количество пользователей, указавших свой регион: {2}
{5}

https://t.me/{4}""".format(project_info,
                           users_count_all,
                           users_count_regions,
                           cur_time,
                           BOT_NAME,
                           text
                           ))


@dp.message_handler(commands=['df'])
async def send_df(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        df = await get_df('SELECT * FROM users')
        print(df)
        await message.answer("df в принте")

@dp.message_handler(commands=['new_users'])
async def send_total(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        cur_time = await current_time()
        total_str = await sql_to_text(
            "SELECT DATE(`created`) AS 'data_time',`utm_source`,COUNT(*) AS 'cnt' from users GROUP BY DATE(`created`),`utm_source` ORDER BY `data_time` desc")
        await send_full_text(message.chat.id, """Количество новых пользователей по состоянию на {0}\n{1} """.format(cur_time, total_str))


@dp.message_handler(commands=['total'])
async def send_total(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        cur_time = await current_time()
        total_str = await get_total_text(
            "SELECT project_code,(SELECT b.name FROM projects b where b.project_code=a.project_code) AS 'project_name',COUNT(*) AS 'all votes',COUNT(DISTINCT `dep_id`) AS 'unique deps',COUNT(DISTINCT `chat_id`) AS 'unique users'  FROM votes a where `project_code`<>'' GROUP BY project_code")
        await message.answer(
            """Статистика по обращениям к парламентариям по состоянию на {0}{1} """.format(cur_time, total_str))


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
async def send_last_votes(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        sql = """with aa AS (SELECT v.chat_id,COUNT(*) AS cnt FROM votes v WHERE v.project_code='alimentover' GROUP BY v.chat_id HAVING cnt>20)
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
        text = 'ТОП пользователи:'
        list = await get_sql_first_column(sql)
        for item in list:
            text += '\n\n' + item
        await message.answer(text)

@dp.message_handler(commands=['last_votes'])
async def send_last_votes(message: types.Message):
    if message.from_user.id in admin_chatid_list:
        sql = """SELECT v.upd||' @'||u.username||' ('||u.chat_id||' '||u.first_name||' '||u.last_name||') -> '||d.dep AS 'answ' FROM votes v
    JOIN users u ON u.chat_id=v.chat_id
    JOIN deps d ON d.rowid=v.dep_id
    WHERE v.project_code='alimentover'
    ORDER BY v.upd DESC LIMIT 10
    """
        text = 'Последние голоса:'
        list = await get_sql_first_column(sql)
        for item in list:
            text += '\n\n' + item
        await message.answer(text)


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

        sql = "SELECT COUNT(DISTINCT a.chat_id) AS 'cnt'  FROM votes a WHERE a.dep_id>448 and a.project_code='alimentover'"
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

        sql = "SELECT COUNT(DISTINCT a.chat_id) AS 'cnt'  FROM votes a WHERE a.dep_id<448 and a.project_code='alimentover'"
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
        # await message.answer(str(message.chat.id)+'\n\n'+message.text)
        chat_id_list = await get_all_users(con, cur)
        # print(chat_id_list)
        # await bot.send_message(80387796,'/send_all :\n\n' + message_for_users)
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
