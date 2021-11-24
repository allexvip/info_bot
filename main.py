import logging
import datetime
from aiogram import Bot, Dispatcher, executor, types

from settings import *
import sqlite3
con = sqlite3.connect('bot_db.db')

#logging.basicConfig(filename= LOGGING_FILE_NAME , encoding='utf-8', level=logging.DEBUG)
API_TOKEN = TELEGRAM_BOT_API_KEY



# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

cur = con.cursor()

# Create table
cur.execute('''CREATE TABLE IF not exists "log" (
	"chat_id" BIGINT NULL,
	"user_name" VARCHAR(50) NULL,
	"upd" DATETIME NULL
	)
;
''')

async def get_project_info(con,cur,project,field):
    res_list = []
    res_dict ={}
    sql = """select {1} from projects where `project_code` in ('{0}') """.format(project,field)
    a = await send_sql(con, cur, sql)
    for item_a in a:
        return str(item_a[0])

async def current_time():
    current_time =  datetime.datetime.now()
    return current_time.strftime("%Y-%m-%d %H:%M")

async def send_sql(con,cur,sql):
    res = ''
    try:
        # Insert a row of data
        res = cur.execute(sql)
        # Save (commit) the changes
        con.commit()
    except Exception as e:
        logging.info('SQL exception'+str(e))
    return res.fetchone()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
#con.close()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`user_name`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id, message.chat.username, message.text))

    """
    This handler will be called when user sends `/start` or `/help` command
    """
    #await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
    await message.answer("""Добро пожаловать!
Я помогу подать обращение к депутатам госдумы.

Актуальные инициативы:
- ‼️ Жалоба на законопроекты о введении уголовного наказания за частичную неуплату алиментов жмите /alijail

- 🔥 Заявление о внесении в ГД законопроекта о введении верхней границы алиментов жмите /alimentover
 """)

@dp.message_handler(regexp='(^[\/]+[a-z].*)')
async def send_welcome(message: types.Message):
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`user_name`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id, message.chat.username, message.text))

    # write projects content
    project = message.text.replace('/','')
    sql = """SELECT d.rowid,* FROM deps d
LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_name='{0}'
WHERE v.dep_id IS null
ORDER BY RANDOM()
LIMIT 1""".format(project)
    a = await send_sql(con,cur,sql)
    if not a:
        """ if all deps already used for first round then we use individual dep for user"""
        sql = """SELECT d.rowid,* FROM deps d
        LEFT JOIN votes v ON v.dep_id=d.rowid and v.project_name='{0}' and v.user_id='{1}'
        WHERE v.dep_id IS null
        ORDER BY RANDOM()
        LIMIT 1""".format(project,message.chat.id)
        a = await send_sql(con, cur, sql)
    project_obj = await send_sql(con,cur,"select desc from projects where project_code in ('{0}') limit 1".format(project))
    project_desc = project_obj[0]
    print(a)
    print(project_desc)
    dep_id = str(a[0])
    dep_name = str(a[1])
    await message.answer("{0}\n\n{1} \n\nПосле отправки нажмите здесь /{2}_{3}".format(dep_name,project_desc,dep_id,project))
        #await message.answer("{2}\n\n{3}  \n\n/{0}_{1} ".format(dep_id,project,dep_name,project_desc))

@dp.message_handler(regexp='^[\/]+[\w].*[_]+[A-Za-z].*')
#for write in db votes
async def write_command(message: types.Message):
    await send_sql(con,cur,"INSERT INTO logs (`chat_id`,`user_name`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(message.chat.id,message.chat.username,message.text))
    project_name = message.text.split('_')[1]
    dep_id = message.text.split('_')[0].replace('/', '')
    sql = "INSERT INTO votes (`user_id`,`user_answer`,`project_name`,`dep_id`,`upd`) VALUES ('{0}','{1}','{2}','{3}',datetime('now'))".format(
    message.chat.id,
    message.text,
    project_name,
    dep_id )
    print(sql)
    await send_sql(con, cur,sql)

    await message.answer("""✅ Пометил у себя. Спасибо за Ваше участие! 🙂 
 Вместе мы сила! 💪💪💪 
Чтобы ещё написать другому депутату нажмите: /{0} .
Список актуальных инициатив /start""".format(project_name))

@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await send_sql(con, cur,
                   "INSERT INTO logs (`chat_id`,`user_name`,`message`,`upd`) VALUES ('{0}','{1}','{2}',datetime('now'))".format(
                       message.chat.id,
                       message.chat.username,
                       message.text))

    await message.answer('Ничего не понял. Помощь /help')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)