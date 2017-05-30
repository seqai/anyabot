class UserService(object):
    def __init__(self, users):
        self.users = []
        self.aliases = {}
        self.reportnames = {}

        for user in users:
            self.add(user)

    def add(self, user):
        self.users.append(user["id"])
        self.aliases[user["username"]] = user["id"]
        self.reportnames[user["id"]] = user["name"]

    def authorized(self, user_id):
        return user_id in self.users