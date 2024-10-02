users = {
    '1': {"username": "aigerimk", "password": "password1", "otp": "111111"},
    '3': {"username": "aigerimk", "password": "password1", "otp": "111111"},
}

def get_user(name):
    return users.get(name)
