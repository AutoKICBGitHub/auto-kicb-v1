class User:
    def __init__(self, username, password, otp):
        self.username = username
        self.password = password
        self.otp = otp

users = {
    '1': User(username="aigerimk", password="password1", otp="111111"),
    '3': User(username="aigerimk", password="password1", otp="111111"),
}

def get_user(name):
    return users.get(name)