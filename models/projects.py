class Project(object):
    def __init__(self, project_code, name, desc, short_name):
        self.code = project_code
        self.name = name
        self.description = desc
        self.short_name = short_name

    def __str__(self):
        return '({code}) {short_name}'.format(
            code = self.code,
            short_name = self.short_name,
        )
