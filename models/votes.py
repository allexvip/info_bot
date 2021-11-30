from .deps import Deputy
from .projects import Project


class Vote(object):
    def __init__(self, chat_id, project: Project, user_answer, dep_id, upd, confirmed, deputy: Deputy, rowid):
        self.chat_id = chat_id
        self.project = project
        self.user_answer = user_answer
        self.dep_id = dep_id
        self.upd = upd
        self.confirmed = confirmed
        self.deputy = deputy
        self.id = rowid

    def __str__(self):
        return '{deputy} ({project}), {upd}'.format(
            deputy = self.deputy,
            project = self.project.short_name,
            upd = self.upd,
        )

    def get_confirm_link(self):
        return 'confirm_{dep_id}_{project_code}_{vote_id}'.format(
            dep_id = self.deputy.id,
            project_code = self.project.code,
            vote_id = self.id
        )
