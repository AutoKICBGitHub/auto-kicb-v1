from playwright.sync_api import Page
from pages.Base_page import BasePage
from Exceptions.Login_errors import Login_errors
from time import sleep

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        self.username_input = "//input [@type='text']"
        self.password_input = "//input [@type='password']"
        self.login_button = "//button [contains(text(), 'Войти')]"


    def navigate(self, url: str):
        """Переходит по указанному URL."""
        self.page.goto(url)

    def login(self):
        # if self.page.locator(self.username_input).is_hidden() and self.page.locator(self.password_input).is_hidden():
        #     print("Вход в систему уже выполнен")
        #     raise Login_errors("Ошибка: Вход в систему уже выполнен.", 202)
        """Выполняет вход в систему с фиксированными учетными данными."""
        username = "ataiy"
        password = "Wdarkempiremate666"

         

        # Кликаем на поле логина и вводим имя пользователя
        self.page.click(self.username_input)
        self.page.keyboard.type(username)

        # Кликаем на поле пароля и вводим пароль
        self.page.click(self.password_input)
        self.page.keyboard.type(password)
        sleep(3)
        if self.page.locator(self.login_button).is_visible():
            self.page.locator(self.login_button).click()
            print("Успешный Вход в систему")
        else:
            raise Login_errors("Ошибка: Неверный код подтверждения. Повторный ввод OTP.", 400)   
         

         





    
