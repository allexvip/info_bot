class Deputy(object):
    def __init__(self, dep_id, full_name, party, link):
        self.id = dep_id
        self.full_name = full_name
        self.party = party
        self.link = link

    def __str__(self):
        return '({0}) {1}, {2}'.format(self.id, self.full_name, self.party)