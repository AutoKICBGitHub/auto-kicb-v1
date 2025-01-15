from .base_page import BasePage
import json
import os
from appium.webdriver.common.appiumby import AppiumBy


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.username_field = "//XCUIElementTypeSecureTextField[@value='Логин']"
        self.password_field = "//XCUIElementTypeSecureTextField[@value='Пароль']"
        self.login_button = "//XCUIElementTypeButton[@name='Войти']"
        self.test_data = self.load_test_data()
    
    def load_test_data(self):
        json_path = os.path.join(os.path.dirname(__file__), '../test_data/test_data.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def login_as_valid_user(self, username=None, password=None):
        """
        Выполняет вход в систему. Если username и password не указаны,
        использует данные valid_user из test_data.json
        """
        if username is None and password is None:
            user_data = self.test_data['valid_user']
            username = user_data['username']
            password = user_data['password']
            
        self.send_keys_to_element(self.username_field, username)
        self.send_keys_to_element(self.password_field, password)
        self.click_element(self.login_button)
    
    
