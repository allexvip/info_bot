import logging
import datetime
from aiogram import Bot, Dispatcher, executor, types
from settings import *
import sqlite3

con = sqlite3.connect('bot_db.db')

# logging.basicConfig(filename= LOGGING_FILE_NAME , encoding='utf-8', level=logging.DEBUG)
API_TOKEN = TELEGRAM_BOT_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

cur = con.cursor()


def models_init():
    # Create table structure
    cur.execute('''CREATE TABLE IF NOT EXISTS "logs" (
        "chat_id" BIGINT NULL,
        "username" VARCHAR(50) NULL,
        "upd" DATETIME NULL,
        "message" TEXT NULL
    )
    ;
    ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS "deps" (
        "dep_full_name" TEXT NULL,
        "dep" TEXT NULL,
        "party" TEXT NULL,
        "link" TEXT NULL
    )
    ;
    ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS "projects" (
        "project_code" VARCHAR(50) NULL,
        "name" TEXT NULL,
        "desc" TEXT NULL
    )
    ;
    ''')

    cur.execute('''CREATE TABLE IF NOT EXISTS "votes" (
        "user_answer" VARCHAR(50) NULL,
        "chat_id" BIGINT NULL,
        "upd" DATETIME NULL,
        "project_code" VARCHAR(50) NULL,
        "dep_id" INTEGER NULL
    )
    ;
    ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS "users" (
	"chat_id" BIGINT NULL,
	"username" VARCHAR(50) NULL,
	"first_name" VARCHAR(50) NULL,
	"last_name" VARCHAR(50) NULL,
	"region_id" VARCHAR(50) NULL,
	"upd" DATETIME NULL
    )
    ;
    ''')
    cur.execute('''CREATE TABLE IF NOT EXISTS "regions" (
	"region_id" INTEGER NULL,
	"name" VARCHAR(50) NULL
    )
    ;
    ''')

async def table_to_text(con, cur, sql):
    res = ''
    try:
        cur.execute(sql)
        con.commit()
    except Exception as e:
        logging.info('SQL exception' + str(e))

    records = cur.fetchall()
    for row in records:
        res +="""\n\n{0}:
        
Активные пользователи - {3}.
Отправлено обращений - {1}.
Охвачено {2} депутата(-ов).
""".format(row[1],row[2],row[3],row[4])

    return res

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

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
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
- ‼️ Жалоба на законопроекты о введении уголовного наказания за частичную неуплату алиментов жмите /alijail

- 🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов жмите /alimentover

💡 как вставить текст /help
 """)


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer("""Видео инструкция по установке и использованию расширения для вставки текста:
https://youtu.be/hVAcztBylIc

Ссылка на само расширение: https://cloud.mail.ru/public/MuK2/CJSZQJc9w

Жмите /start""")


@dp.message_handler(commands=['total'])
async def send_help(message: types.Message):
    cur_time = await current_time()
    total_str = await table_to_text(con, cur,
                              "SELECT project_code,(SELECT b.name FROM projects b where b.project_code=a.project_code) AS 'project_name',COUNT(*) AS 'all votes',COUNT(DISTINCT `dep_id`) AS 'unique deps',COUNT(DISTINCT `chat_id`) AS 'unique users'  FROM votes a GROUP BY project_code")
    await message.answer("""Статистика по обращениям к депутатам по состоянию на {0}{1} """.format(cur_time,total_str))


@dp.message_handler(regexp='(^[\/]+[a-z].*)')
async def send_welcome(message: types.Message):
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`username`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id, message.chat.username, message.text))

    # write projects content
    project = message.text.replace('/', '')
    sql = """SELECT d.rowid,`dep` FROM deps d
LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}'
WHERE v.dep_id IS null
ORDER BY RANDOM()
LIMIT 1""".format(project)
    a = await send_sql(con, cur, sql)
    if not a:
        """ if all deps already used for first round then we use individual dep for user"""
        sql = """SELECT d.rowid,`dep`FROM deps d
        LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_code='{0}' and v.chat_id='{1}'
        WHERE v.dep_id IS null
        ORDER BY RANDOM()
        LIMIT 1""".format(project, message.chat.id)
        a = await send_sql(con, cur, sql)
    project_obj = await send_sql(con, cur,
                                 "select `desc` from projects where project_code in ('{0}') limit 1".format(project))
    project_desc = project_obj[0]
    print(a)
    print(project_desc)
    dep_id = str(a[0])
    dep_name = str(a[1])
    await message.answer(
        "{0}\n\n{1} \n\nПосле отправки пожалуйста\nнажмите здесь /{2}_{3} \n\n💡 как вставить текст /help".format(
            dep_name,
            project_desc,
            dep_id, project))


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
    models_init()
    executor.start_polling(dp, skip_updates=True)
