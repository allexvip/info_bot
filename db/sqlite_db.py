import logging
import sqlite3 as sq
from create_bot import *
from models import repository
# import pandas as pd
from sqlalchemy import create_engine
import datetime


async def get_data(sql):
    res = None
    try:
        cur.execute(sql)
        con.commit()
        res = cur.fetchall()
    except Exception as e:
        logging.info('SQL exception get_data(): ' + str(e))
    return res


async def send_full_text(chat_id, info):
    if len(info) > 4096:
        for x in range(0, len(info), 4096):
            await bot.send_message(chat_id, info[x:x + 4096])
    else:
        await bot.send_message(chat_id, info)


async def get_df(sql):
    df = {}
    # df = pd.read_sql(sql, create_engine(f'sqlite:///{DB_FILE_NAME}'))
    return df


# async def sql_to_text(sql, header=True):
#     df = await get_df(sql)
#     dfAsString = df.to_string(header=header, index=False)
#     return dfAsString


async def get_votes_count(project_code):
    sql = "SELECT COUNT(*) AS cnt FROM votes where project_code='{0}'".format(project_code)
    res = await get_sql_first_column(sql)
    return res[0]


async def get_total_text(sql):
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
Охвачено {2} парламентария(ев).
""".format(row[1], row[2], row[3], row[4])

    return res


async def get_all_users(con, cur):
    list = []
    sql = """SELECT distinct chat_id FROM logs where chat_id>0"""
    a = await from_db(sql)
    for item_a in a:
        list.append(str(item_a[0]))
    return list


async def get_sql_first_column(sql):
    list = []
    a = await from_db(sql)
    # print(a)
    for item_a in a:
        list.append(str(item_a[0]))
    return list


async def get_sql_one_value(sql):
    list = []
    a = await from_db(sql)
    # print(a)
    for item_a in a:
        list.append(str(item_a[0]))
    return list[0]


async def sql_to_str(sql):
    list = []
    line_dict = {}
    res = ''
    a = await from_db(sql)
    for item_a in a:
        for item_index in range(len(item_a)):
            # line_dict[item_index] = str(item_a[item_index])
            #list.append(item_a[line_dict])
            res += f'{str(item_a[item_index])}  '
        res +='\n'
        line_dict = {}
    return res


async def get_users_count(con, cur):
    list = []
    sql = "SELECT COUNT(*) 'all users' FROM users"
    a = await from_db(sql)
    for item_a in a:
        list.append(str(item_a[0]))
    return list[0]


async def get_region_users_count(con, cur):
    list = []
    sql = "SELECT COUNT(*) 'all users' FROM users where region_id is not null"
    a = await from_db(sql)
    for item_a in a:
        list.append(str(item_a[0]))
    return list[0]


async def get_users_votes(project, chat_id):
    list = []
    sql = """SELECT chat_id,project_code,group_concat(dep||' /'||b.rowid||'_'||project_code||'_minus '||' /'||b.rowid||'_'||project_code||'_plus', '\n') AS 'deps_string' FROM votes a 
JOIN deps b ON b.rowid = a.dep_id
WHERE a.project_code = 'alimentover' 
GROUP BY chat_id,project_code,chat_id """
    sql = """SELECT chat_id,project_code,group_concat(dep,'\n') AS 'deps_string' FROM votes a 
    JOIN (select rowid,dep from deps order by dep) b ON b.rowid = a.dep_id
    WHERE a.project_code = '{0}' and chat_id='{1}'
    GROUP BY chat_id,project_code,chat_id """.format(project, chat_id)
    a = await from_db(sql)
    for item_a in a:
        inList = []
        # print(item_a)
        for item in item_a:
            inList.append(item)
        list.append(inList)
    return list


async def get_project_info(project, field):
    res_list = []
    res_dict = {}
    sql = f"""select {field} from projects where `project_code` in ('{project}') """
    a = await send_sql(sql)
    for item_a in a:
        return str(item_a[0])


async def current_time():
    current_time_res = datetime.datetime.now()
    return current_time_res.strftime(" %d-%m-%Y %H:%M")


async def from_db(sql):
    res = ''
    try:
        # Insert a row of data
        res = cur.execute(sql)
        # Save (commit) the changes
        con.commit()
    except Exception as e:
        logging.info('SQL exception' + str(e))

    if sql.lower()[0:6] == 'select' or sql.lower()[0:4] == 'with':
        return res.fetchall()


async def send_sql(sql):
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


def sql_start():
    global con, cur
    con = sq.connect(DB_FILE_NAME)
    cur = con.cursor()
    if con:
        print('DB connected')
    # con.execute('Create table if not exists menu(img TEXT, name TEXT PRIMARY KEY, description TEXT, price TEXT)')
    # con.commit()


async def sql_add_line(table,state):
    async with state.proxy() as data:
        cur.execute(f'insert into {table} values (?,?,?,?,0)', tuple(data.values()))
        con.commit()

async def sql_edit_line(table,state):
    async with state.proxy() as data:
        cur.execute(f"UPDATE `{table}` set `{data['name']}`='{data['value']}' where `project_code`='{data['project_code']}';" )
        con.commit()

async def sql_read(message):
    for ret in cur.execute('SELECT * from menu').fetchall():
        await bot.send_photo(message.from_user.id, ret[0],
                             '{0}\nОписание: {1}\nЦена: {2} руб.'.format(ret[1], ret[2], ret[-1]))


async def sql_read_for_delete():
    return cur.execute('SELECT * from menu').fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM menu where name == ?', (data,))
    con.commit()
