users = {
    '1': {"username": "aigerimk", "password": "password1", "otp": "111111", 'account': '1280010101232070'},
    '2': {"username": "01365", "password": "password1", "otp": "111111", 'account': '1280176053049146'},
    '3': {"username": "aigerimk", "password": "password1", "otp": "111111", 'account': '1280010001232043'},
    '4': {"username": "aigerimk", "password": "password1", "otp": "111111", 'account': '1285090000630562'},
    '5': {"username": "00364985", "password": "password1", "otp": "111111", 'account': '1280176054888005'},
    '6': {"username": "00412137", "password": "password1", "otp": "111111", 'account': '1280176054933774'},
    # не работает карта из за переводов'7': {"username": "00457926", "password": "password1", "otp": "111111", 'account': '1280016056879496'},
    '7': {"username": "09816", "password": "password1", "otp": "111111", 'account': '1280013109816103'},
    '8': {"username": "11090", "password": "password1", "otp": "111111", 'account': '1280010011090172'},
    '9': {"username": "00375174", "password": "password1", "otp": "111111", 'account': '1285010000478831'},
    '10': {"username": "11090", "password": "password1", "otp": "111111", 'account': '1280010111090102'},
    '11': {"username": "00762437", "password": "password1", "otp": "111111", 'account': '1280186053756321'}
}
def get_user(name):
    return users.get(name)


