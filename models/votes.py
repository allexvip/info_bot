from .deps import Deputy


class Vote(object):
    def __init__(self, chat_id, project_code, user_answer, dep_id, upd, confirmed, deputy: Deputy):
        self.chat_id = chat_id
        self.project_code = project_code
        self.user_answer = user_answer
        self.dep_id = dep_id
        self.upd = upd
        self.confirmed = confirmed
        self.deputy = deputy

    def __str__(self):
        return '{deputy} - {project_code}, {upd}'.format(
            deputy = self.deputy,
            project_code = self.project_code,
            upd = self.upd,
        )
