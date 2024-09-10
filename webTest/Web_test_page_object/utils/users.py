
class users:
    def __init__(self, username, password, otp):
        self.username = username
        self.password = password
        self.otp = otp

    users = {
        '1': users(username="ataiy", password="Wsvoboda666", otp_secret="WTCSZCDIZXNQBX6FGWXUQ36EGU6ICVEI"),

}

def get_user(name):
    return users.get(name)


