from Web_auto_dev.Other.Users import users

import time

class LoginPage:
    def __init__(self, page):
        self.page = page

    def login_in_system(self, username):
        user_data = users.get(username)
        if not user_data:
            raise ValueError(f"Пользователь с именем {username} не найден.")

        # Ожидание загрузки страницы и ввод данных
        self.page.locator("//div[@class='auth-fields custom-input']//div").nth(0).wait_for(timeout=30000)
        self.page.locator("//div[@class='auth-fields custom-input']//div").nth(0).fill(user_data['login'])
        self.page.locator("//div[@class='auth-fields custom-input']//div").nth(4).wait_for(timeout=30000)
        self.page.locator("//div[@class='auth-fields custom-input']//div").nth(4).fill(user_data['password'])
        self.page.locator("//button[@type='submit']").wait_for(timeout=10000)
        time.sleep(2)
        self.page.locator("//button[@type='submit']").is_enabled = True
        self.page.locator("//button[@type='submit']").click()