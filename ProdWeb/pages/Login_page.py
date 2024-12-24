import json
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

    def login(self, credentials_file='C:/project_kicb/ProdWeb/user_data/users.json'):

        with open(credentials_file, 'r') as file:
            self.credentials = json.load(file)
        

        self.otp_key_google = self.credentials['otp_key_google']
        # username = "ataiy"
        # password = "Wdarkempiremate666"

         
        self.page.wait_for_selector(self.username_input)
        # Кликаем на поле логина и вводим имя пользователя
        self.page.click(self.username_input)
        self.page.keyboard.type(self.credentials['username'])

        # Кликаем на поле пароля и вводим пароль
        self.page.click(self.password_input)
        self.page.keyboard.type(self.credentials['password'])
        sleep(3)
        if self.page.locator(self.login_button).is_visible():
            self.page.locator(self.login_button).click()
            print("Успешный Вход в систему")
        else:
            raise Login_errors("Ошибка: Неверный код подтверждения. Повторный ввод OTP.", 400)  



         

         





    
