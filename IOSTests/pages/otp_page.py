from .base_page import BasePage
import pyotp
import json
import os


class OTPPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        # Локаторы
        self.page_title = "//XCUIElementTypeStaticText[@name='Код подтверждения']"
        self.otp_input = '//XCUIElementTypeApplication[@name="KICB"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]'
        self.help_link = '//XCUIElementTypeStaticText[@name="Получить код инициализации Google Authenticator на электронную почту"]'
        self.submit_button = '//XCUIElementTypeButton[@name="Подтвердить"]'
        self.not_now_button = '//XCUIElementTypeButton[@name="Не сейчас"]'
        
        # Загружаем секретный ключ из test_data.json
        self.otp_secret = self.load_otp_secret()
    
    def handle_save_password_alert(self):
        """Обработка алерта сохранения пароля"""
        try:
            self.click_element(self.not_now_button)
            print("✅ Нажата кнопка 'Не сейчас' на алерте сохранения пароля")
            return True
        except:
            print("ℹ️ Алерт сохранения пароля не найден")
            return False
    
    def load_otp_secret(self):
        """Загрузка OTP секрета из test_data.json"""
        json_path = os.path.join(os.path.dirname(__file__), '../test_data/test_data.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('otp_secret')
    
    def is_page_displayed(self):
        """Проверка, что мы на странице OTP"""
        return self.wait_for_element_to_be_visible(self.page_title)
    
    def get_otp_code(self):
        """Получение текущего OTP кода"""
        if not self.otp_secret:
            raise ValueError("OTP secret key not found in test_data.json")
        totp = pyotp.TOTP(self.otp_secret)
        return totp.now()
    
    def enter_otp(self):
        """Ввод OTP кода"""
        # Сначала обрабатываем алерт сохранения пароля
        self.handle_save_password_alert()
        
        # Затем вводим OTP
        otp_code = self.get_otp_code()
        self.send_keys_to_element(self.otp_input, otp_code)
        self.click_element(self.submit_button)
    
    
