class User:
    def __init__(self, username, password, otp):
        self.username = username
        self.password = password
        self.otp = otp

users = {
    '1': User(username="00727272", password="password1", otp="111111"),
    '2': User(username="aigerimk", password="password1", otp="111111"),
    # Добавьте других пользователей по мере необходимости
}

def get_user(name):
    return users.get(name)
