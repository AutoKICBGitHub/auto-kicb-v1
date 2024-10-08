from Web_auto_dev.Other.Users import users
import pyotp

class OTPPage:
    def __init__(self, page):
        self.page = page

    def login_in_system(self, username):
        user_data = users.get(username)
        if not user_data:
            raise ValueError(f"Пользователь с именем {username} не найден.")
        otp_code = user_data['otp_secret']


        self.page.locator(".confirm-otp__input").first.wait_for(timeout=30000)
        self.page.locator(".confirm-otp__input").first.click()
        self.page.keyboard.type(str(otp_code))