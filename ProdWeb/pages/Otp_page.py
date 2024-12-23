import pyotp
from time import sleep
from playwright.sync_api import Page
from Exceptions.Invalid_otp_exception import OTP_errors
from Exceptions.Loading_errors import Loading_errors




class OtpPage:
    def __init__(self, page: Page):
        self.page = page
        self.otp_inputs = "//input[@class='confirm-otp__input']"  # Локатор для полей OTP
        self.confirm_button = "//button[contains(text(), 'Подтвердить')]"  # Локатор для кнопки подтверждения
        self.error_message_locator1 = "//span[contains(text(), 'Неверный код подтверждения')]"
        self.error_message_locator2 = "//span[contains(text(), 'Неизвестная ошибка')]"  # Локатор для сообщения об ошибке
        self.listener_exchange_course = "//div[contains(text(), 'EUR')]"
        self.listener_card_status = "//span[contains(text(), 'ELCARD')]"
        self.cards_status = "//div [@class='expand-data']"

    def enter_otp(self, otp_key: str):
        totp = pyotp.TOTP(otp_key)  # Генерация OTP
        otp = totp.now()

        # Вводим каждый символ OTP в соответствующее поле
        for i, digit in enumerate(otp):
            self.page.locator(self.otp_inputs).nth(i).fill(digit)
        sleep(2)
        if self.page.locator(self.error_message_locator1).is_visible():
            raise OTP_errors("Ошибка: Неверный код подтверждения. Повторный ввод OTP.", 400)
        
        if self.page.locator(self.error_message_locator2).is_visible():
            raise OTP_errors("Ошибка: Неизвестная ошибка. Повторный ввод OTP.", 401)
            

 
    def accounts_status(self):
        self.page.locator(self.cards_status).nth(1).wait_for(timeout=30000)

        


        

    def clear_otp_fields(self):
        """Очищает поля ввода OTP."""
        for i in range(6):  # Предполагаем, что OTP состоит из 6 символов
            self.page.locator(self.otp_inputs).nth(i).fill("")  # Очищаем каждое поле


    def listener_exchange_course1(self, max_reloads=2):
        reloads = 0
        while reloads < max_reloads:
            if self.page.locator(self.listener_exchange_course).is_visible():
                print("Курс обмена валюты подгружен")
                break
            else:
                raise Loading_errors("Ошибка: Курс обмена валюты не подгружен", 402)
                reloads += 1
                self.page.reload()
        
        reloads = 0
        while reloads < max_reloads:
            if self.page.locator(self.listener_card_status).nth(0).is_visible():
                print("Статус карты подгружен")
                break
            else:
                raise Loading_errors("Ошибка: Статус карты не подгружен", 403)
                reloads += 1
                self.page.reload()
    
               



    
