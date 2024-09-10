class User:
    def __init__(self, username, password, otp_secret):
        self.username = username
        self.password = password
        self.otp_secret = otp_secret

users = {
    '1': User(username="ataiy", password="Wsvoboda666", otp_secret="WTCSZCDIZXNQBX6FGWXUQ36EGU6ICVEI"),
}

def get_user(name):
    return users.get(name)