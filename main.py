import logging
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.chat_member import ChatMember

from settings import *
import sqlite3
from models import repository

con = sqlite3.connect('bot_db.db')

# logging.basicConfig(filename= LOGGING_FILE_NAME , encoding='utf-8', level=logging.DEBUG)
API_TOKEN = TELEGRAM_BOT_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
cur = con.cursor()


async def get_total_text(con, cur, sql):
    res = ''
    try:
        cur.execute(sql)
        con.commit()
    except Exception as e:
        logging.info('SQL exception' + str(e))

    records = cur.fetchall()
    for row in records:
        res += """\n\n{0}:
        
Активные пользователи - {3}.
Отправлено обращений - {1}.
Охвачено {2} депутата(-ов).
""".format(row[1],row[2],row[3],row[4])

    return res

async def get_all_users(con, cur):
    list = []
    sql= """SELECT distinct chat_id FROM logs where chat_id>0"""
    a = await from_db(con, cur, sql)
    for item_a in a:
        list.append(str(item_a[0]))
    return list


async def get_users_votes(con, cur, project):
    list = []
    sql= """SELECT chat_id,project_code,group_concat(dep||' /'||b.rowid||'_'||project_code||'_minus '||' /'||b.rowid||'_'||project_code||'_plus', '\n') AS 'deps_string' FROM votes a 
JOIN deps b ON b.rowid = a.dep_id
WHERE a.project_code = 'alimentover' 
GROUP BY chat_id,project_code,chat_id """
    a = await from_db(con, cur, sql)
    for item_a in a:
        inList = []
        print(item_a)
        for item in item_a:
            inList.append(item)
        list.append(inList)
    return list

async def get_project_info(con, cur, project, field):
    res_list = []
    res_dict = {}
    sql = """select {1} from projects where `project_code` in ('{0}') """.format(project, field)
    a = await send_sql(con, cur, sql)
    for item_a in a:
        return str(item_a[0])


async def current_time():
    current_time_res = datetime.datetime.now()
    return current_time_res.strftime("%d-%m-%Y %H:%M")


async def from_db(con, cur, sql):
    res = ''
    try:
        # Insert a row of data
        res = cur.execute(sql)
        # Save (commit) the changes
        con.commit()
    except Exception as e:
        logging.info('SQL exception' + str(e))

    if sql.lower()[0:6] == 'select':
        return res.fetchall()

async def send_sql(con, cur, sql):
    res = ''
    try:
        # Insert a row of data
        res = cur.execute(sql)
        # Save (commit) the changes
        con.commit()
    except Exception as e:
        logging.info('SQL exception' + str(e))

    if sql.lower()[0:6] == 'select':
        return res.fetchone()


# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
# con.close()

@dp.message_handler(commands=['my_appeals'])
async def send_my_appeals(message: types.Message):
    await message.answer(str(message.chat.id)+'\n\n'+message.text)
    list = await get_users_votes(con, cur, 'alijail')
    for item in list:
        if item[0] == message.chat.id:
            await message.answer('Вы писали депутатам:\n\n{}'.format(item[2]))

@dp.message_handler(commands=['send_all'])
async def send_all(message: types.Message):
    if message.chat.id == ADMIN_CHAT_ID:
        message_for_users = message.text.replace('/send_all ','')
        # await message.answer(str(message.chat.id)+'\n\n'+message.text)
        chat_id_list = await get_all_users(con, cur)
        #print(chat_id_list)
        #await bot.send_message(80387796,'/send_all :\n\n' + message_for_users)
        for item_chat_id in chat_id_list:
            print(item_chat_id+' '+message_for_users)
            #await bot.send_message(80387796, '/send_all :\n'+item_chat_id+'\n' + message_for_users)
            try:
                await bot.send_message(item_chat_id, message_for_users)
            except Exception as e:
                await bot.send_message(80387796, item_chat_id +' Error (send all)\n\n' + str(e))
        await message.answer('Отправили пользователям '+str(chat_id_list))

    else:
        await message.answer('Ничего не понял. Помощь /help')



@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    #await message.answer(message.chat.id)
    #user_channel_status = await bot.get_chat_member(chat_id=-1001176029164, user_id=message.chat.id)
    # if user_channel_status["status"] != 'left':
    #     await message.answer('text if in group')
    # else:
    #     await message.answer('text if not in group')
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id, message.chat.username, message.text))
    await send_sql(con, cur,
                   "INSERT INTO users (`chat_id`,`username`,`first_name`,`last_name`,`upd`) SELECT '{0}','{1}','{2}','{3}',datetime('now') where (select count(*) from `users` where chat_id='{0}')=0".format(
                       message.chat.id,
                       message.chat.username,
                       message.chat.first_name,
                       message.chat.last_name,
                   ))
    await message.answer("""Добро пожаловать!
Я помогу подать обращение к депутатам госдумы.

Актуальные инициативы:
- 🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов жмите /alimentover

💡 как вставить текст /help
 """)
""" - ‼️ Жалоба на законопроекты о введении уголовного наказания за частичную неуплату алиментов жмите /alijail """

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("""Как писать обращения и жалобы депутатам ГосДумы с помощью бота от Семейного Фронта. ВИДЕОИНСТРУКЦИЯ
https://www.youtube.com/watch?v=dWvOrnXiLkg
    
Видео инструкция по установке и использованию расширения для вставки текста:
https://youtu.be/hVAcztBylIc

Ссылка на само расширение: https://cloud.mail.ru/public/MuK2/CJSZQJc9w

Ещё инструкция (универсальная) по вставке текста:
https://vinadm.blogspot.com/2017/04/chrome-letterskremlinru.html

Жмите /start""")


@dp.message_handler(commands=['total'])
async def send_help(message: types.Message):
    cur_time = await current_time()
    total_str = await get_total_text(con, cur,
                              "SELECT project_code,(SELECT b.name FROM projects b where b.project_code=a.project_code) AS 'project_name',COUNT(*) AS 'all votes',COUNT(DISTINCT `dep_id`) AS 'unique deps',COUNT(DISTINCT `chat_id`) AS 'unique users'  FROM votes a where `project_code`<>'' GROUP BY project_code")
    await message.answer("""Статистика по обращениям к депутатам по состоянию на {0}{1} """.format(cur_time,total_str))


@dp.message_handler(commands=['get_unconfirmed_votes', 'get_uv'])
async def send_unconfirmed_votes(message: types.Message):
    repo = repository.RepositorySQLite()
    repo.connection = con
    repo.cursor = cur
    votes = repo.get_unconfirmed_votes_by_chat(message.chat.id)
    text = ''
    for v in votes:
        formated_str = '{deputy} ({project_name}) - /{confirm_link}'.format(
            deputy = v.deputy.full_name,
            project_name = v.project.short_name,
            confirm_link = v.get_confirm_link()
        )
        print(formated_str)
        text += '{0}\n'.format(formated_str)

    await message.answer(text)


@dp.message_handler(regexp='(^[\/]+[a-z].*)')
async def send_welcome(message: types.Message):
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id, message.chat.username, message.text))

    # write projects content
    project = message.text.replace('/', '')
    sql = """SELECT d.rowid,`dep`,`link_send` FROM deps d
LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}'
WHERE v.dep_id IS null
ORDER BY RANDOM()
LIMIT 1""".format(project)
    a = await send_sql(con, cur, sql)
    if not a:
        """ if all deps already used for first round then we use individual dep for user"""
        sql = """SELECT d.rowid,`dep`,`link_send` FROM deps d
        LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id='{1}'
        WHERE v.dep_id IS null
        ORDER BY RANDOM()
        LIMIT 1""".format(project, message.chat.id)
        a = await send_sql(con, cur, sql)
    project_obj = await send_sql(con, cur,
                                 "select `desc` from projects where project_code in ('{0}') limit 1".format(project))
    project_desc = project_obj[0]
    dep_id = str(a[0])
    dep_name = str(a[1])
    link_send = str(a[2])
    await message.answer(
        "{0}\n\n{1} \nПишем сюда: {4}\n\nПосле отправки пожалуйста\nнажмите здесь /{2}_{3} \n\n💡 как вставить текст /help".format(
            dep_name,
            project_desc,
            dep_id,
            project,
            link_send
        )
    )


@dp.message_handler(regexp='^[\/]+[\w].*[_]+[A-Za-z].*')
async def write_command(message: types.Message):
    # for write in db votes
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id, message.chat.username, message.text))
    project_code = message.text.split('_')[1]
    dep_id = message.text.split('_')[0].replace('/', '')
    await send_sql(con, cur,
                   "INSERT INTO votes (`chat_id`,`user_answer`,`project_code`,`dep_id`,`upd`) VALUES ('{0}','{1}','{2}','{3}',datetime('now'))".format(
                       message.chat.id,
                       message.text,
                       project_code,
                       dep_id))
    await message.answer("""✅ Пометил у себя. Спасибо за Ваше участие! 🙂 Вместе мы сила! 💪💪💪 

Чтобы ещё написать другому депутату нажмите: /{0} .

Список актуальных инициатив /start""".format(project_code))


@dp.message_handler()
async def echo(message: types.Message):
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id,
                       message.chat.username,
                       message.text))

    await message.answer('Ничего не понял. Помощь /help')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
