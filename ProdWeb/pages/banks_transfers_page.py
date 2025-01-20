from playwright.sync_api import Page
from pages.Base_page import BasePage
from time import sleep
from Exceptions.payment_errors import MinimalLimitError, MaximalLimitError, ButtonNotFoundError
import pyotp
import json
import os

class BanksTransfersPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Основные локаторы
        self.payment_button = "//a [@href='/payment']"
        self.banks_wallets_button = "//p [contains(text(),'Банки и кошельки КР')]"  # XPath для кнопки "Банки и кошельки КР"
        self.kyrgyz_banks_button = "//div [contains(text(),'Банки Кыргызской Республики')]"   # XPath для "Банки Кыргызской Республики"
        
        # Список банков и их локаторы
        self.bank_links = {
            "optima": "//div [contains(text(),'Оптима Банк')]", # XPath для Оптима Банка
            "mbank": "//div [contains(text(),'MBANK')]",
            "bakai": "//div [contains(text(),'Bakai Bank')]",  # XPath для Бакай Банка
            "simbank": "//div [contains(text(),'Simbank')]",
            "demir": "//div [contains(text(),'Демир Банк')]",
            "kompanion": "//div [contains(text(),'Банк Компаньон')]",
            "ayil": "//div [contains(text(),'Айыл Банк')]",
            "obank": "//div [contains(text(),'O!Bank')]",
        }
        
        # Локаторы для формы перевода
        self.account_locator = "//p [contains(text(), 'Счет списания')]//..//div"
        self.account_locator_som = "//p [contains(text(), '1280016059196988')]"
        self.phone_number_input = "//input [@class='generic-payment__input']"
        self.amount_input = "//input [@type = 'text']"
        self.pay_button = "//button [contains(text(), 'Оплатить')]"
        self.confirm_button = "//button [contains(text(), 'Подтвердить')]"
        self.goto_main_page = "//a [@href='/']"
        
        # Получаем путь к файлу users.json относительно текущего файла
        current_dir = os.path.dirname(os.path.dirname(__file__))
        users_file = os.path.join(current_dir, 'user_data', 'users.json')
        
        # Читаем секретный ключ из файла
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            self.totp_secret = users_data["otp_key_google"]
            self.totp = pyotp.TOTP(self.totp_secret)

    def open_banks_transfers(self):
        """Открывает раздел переводов на банки"""
        self.page.click(self.payment_button)
        self.page.click(self.banks_wallets_button)
        self.page.click(self.kyrgyz_banks_button)

    def transfer_to_bank(self, bank_key: str, phone_number: str, amount=20):
        """Выполняет перевод в выбранный банк по номеру телефона"""
        try:
            # Клик по банку из списка
            self.page.click(self.bank_links[bank_key])
            
            # Особая обработка для разных банков
            if bank_key == "mbank":
                self.page.locator("//div [contains(text(),'MBANK')]").click()
            elif bank_key == "kompanion":
                self.page.locator("//div [contains(text(),'Электронный кошелек')]").click()
            else:
                self.page.locator("//div [contains(text(),'по номеру телефона')]").click()
            
            # Выбор счета списания
            self.page.locator(self.account_locator).nth(1).click()
            self.page.locator(self.account_locator_som).click()
            
            # Обработка оплаты и проверка минимального лимита
            while True:
                self.page.locator(self.phone_number_input).fill(phone_number)
                self.page.locator(self.amount_input).fill(str(amount))
                
                has_error = self.handle_payment_buttons(bank_key, amount)
                if has_error:
                    amount = self.handle_minimal_limit(amount)
                    continue
                break
            
            sleep(2)  # Ждем для уверенности
            self.safe_return_to_main()
            
        except Exception as e:
            print(f"❌ Ошибка при переводе в банк {bank_key}: {str(e)}")
            self.safe_return_to_main()
            raise

    def get_otp_code(self) -> str:
        """Получает актуальный OTP код из Google Authenticator"""
        try:
            otp_code = self.totp.now()  # Получаем текущий код
            print(f"Получен OTP код из Google Authenticator: {otp_code}")
            return otp_code
        except Exception as e:
            print(f"Ошибка при получении OTP кода: {str(e)}")
            raise 