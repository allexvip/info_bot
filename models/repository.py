import sqlite3
from .votes import Vote
from .deps import Deputy
from .projects import Project


class RepositorySQLite(object):
    def __init__(self):
        self.projects = dict()
        self.connection = None
        self.cursor = None

    def connect(self, filename):
        try:
            self.connection = sqlite3.connect(filename)
            self.cursor = self.connection.cursor()
        except Exception as e:
            print('SQLite3 connection error: {0}'.format(e))
            raise e

    def get_all_votes_by_chat(self, chat_id):
        self.get_projects()
        result = []
        sql = 'select * from votes where chat_id={0}'.format(chat_id)
        for v in self.cursor.execute(sql).fetchall():
            result.append(Vote(
                    v[0], self.projects[v[1]],
                    v[2], v[3], v[4], v[5],
                    self.get_deputy_by_id(v[3]), v[6]
            ))
        return result

    def get_unconfirmed_votes_by_chat(self, chat_id):
        self.get_projects()
        result = []
        sql = 'select *, rowid from votes where chat_id={0} and confirmed=0'.format(chat_id)
        for v in self.cursor.execute(sql).fetchall():
            result.append(Vote(
                v[0], self.projects[v[1]],
                v[2], v[3], v[4], v[5],
                self.get_deputy_by_id(v[3]), v[6]
            ))
        return result

    def get_all_deputies(self):
        pass

    def get_deputy_by_id(self, dep_id):
        sql = 'select * from deps where rowid={0}'.format(dep_id)
        for r in self.cursor.execute(sql):
            return Deputy(dep_id, full_name=r[1], party=r[2], link=r[3])
        return None

    def get_projects(self):
        sql = 'select * from projects'
        for row in self.cursor.execute(sql).fetchall():
            self.projects[row[0]] = Project(*row)
