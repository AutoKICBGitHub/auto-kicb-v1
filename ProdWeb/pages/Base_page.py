from playwright.sync_api import Page
from Exceptions.payment_errors import MinimalLimitError, MaximalLimitError, ButtonNotFoundError
from time import sleep


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def go_to(self, url: str):
        """Переходит по указанному URL."""  # ЗАДАТЬ: URL для перехода
        self.page.goto(url)

    def click(self, locator: str):
        """Кликает по указанному локатору."""  # ЗАДАТЬ: локатор для клика
        self.page.locator(locator).click()

    def type_text(self, locator: str, text: str):
        """Вводит текст в указанный элемент."""  # ЗАДАТЬ: локатор и текст для ввода
        self.page.locator(locator).fill(text)

    def get_text(self, locator: str) -> str:
        """Возвращает текст элемента."""  # ЗАДАТЬ: локатор для получения текста
        return self.page.locator(locator).inner_text()

    def is_visible(self, locator: str) -> bool:
        """Проверяет, виден ли элемент."""  # ЗАДАТЬ: локатор для проверки видимости
        return self.page.locator(locator).is_visible()

    def wait_for_url(self, url_fragment: str):
        """Ожидает, пока URL изменится."""  # ЗАДАТЬ: фрагмент URL для ожидания
        self.page.wait_for_url(url_fragment)

    def get_locator_by_text(self, text: str) -> str:
        """Возвращает XPath локатор по тексту элемента."""
        return f"//*[text()='{text}']"

    def click_by_text(self, text: str):
        """Кликает по элементу, найденному по тексту."""
        locator = self.get_locator_by_text(text)
        self.page.locator(locator).click()

    def handle_minimal_limit(self, amount: int, max_amount: int = 110, step: int = 10) -> int:
        """
        Обрабатывает ошибку минимального лимита
        Возвращает новую сумму или вызывает исключение
        """
        new_amount = amount + step
        if new_amount > max_amount:
            raise MaximalLimitError(
                f"Сумма {new_amount} превысила максимальный тестовый лимит в {max_amount}",
                amount=new_amount
            )
        return new_amount

    def check_minimal_limit_error(self, bank_key: str, current_amount: int) -> bool:
        """Проверяет наличие ошибки минимального лимита"""
        error_message = "//span [contains(text(), 'Сумма меньше минимального лимита.')]"
        if self.page.locator(error_message).is_visible(timeout=2000):
            print(f"Для банка {bank_key} сумма {current_amount} меньше минимального лимита")
            return True
        return False

    def handle_payment_buttons(self, bank_key: str, amount: int):
        """Обрабатывает нажатие кнопок оплаты и подтверждения"""
        try:
            # Проверка кнопки оплаты
            if not self.page.locator("//button [contains(text(), 'Оплатить')]").is_visible(timeout=5000):
                raise ButtonNotFoundError(f"Кнопка Оплатить не найдена для банка {bank_key}", bank=bank_key)
            self.page.locator("//button [contains(text(), 'Оплатить')]").click()
            print(f"Нажата кнопка Оплатить для банка {bank_key}")

            # Даем время для появления ошибки или кнопки подтверждения
            sleep(2)

            # Проверяем ошибку минимального лимита
            error_message = "//span [contains(text(), 'Сумма меньше минимального лимита.')]"
            if self.page.locator(error_message).is_visible(timeout=2000):
                print(f"Обнаружена ошибка минимального лимита для банка {bank_key}")
                return True

            # Проверяем разные варианты кнопок подтверждения
            confirm_buttons = [
                "//button [contains(text(), 'Отправить на подтверждение')]",
                "//button [contains(text(), 'Подтвердить')]"
            ]
            
            button_found = False
            for button in confirm_buttons:
                if self.page.locator(button).is_visible(timeout=2000):
                    self.page.locator(button).click()
                    print(f"Нажата кнопка подтверждения '{button}' для банка {bank_key}")
                    button_found = True
                    break
                
            if not button_found:
                raise ButtonNotFoundError(f"Кнопка подтверждения не найдена для банка {bank_key}", bank=bank_key)

            # Ждем немного после нажатия кнопки подтверждения
            sleep(2)
            
            # Получаем и вводим OTP код
            otp_code = self.get_otp_code()
            print(f"Получен OTP код: {otp_code}")
            self.page.keyboard.type(str(otp_code))
            print(f"OTP код введен для банка {bank_key}")
            
            # Нажимаем Enter для подтверждения
            sleep(1)
            self.page.keyboard.press('Enter')
            print("Нажат Enter для подтверждения OTP")
            
            # Ждем и проверяем сообщение "Принят к обработке"
            sleep(2)
            processing_message = "//p [contains(text(), 'Принят к обработке')]"
            
            # Проверяем 5 раз с интервалом в 2 секунды
            for _ in range(5):
                if self.page.locator(processing_message).is_visible():
                    print("✅ Платеж принят к обработке")
                    return False
                sleep(2)
            
            # Если сообщение не найдено - тест не пройден
            raise Exception("Сообщение 'Принят к обработке' не появилось")
            
        except Exception as e:
            print(f"❌ Ошибка при обработке платежа для банка {bank_key}: {str(e)}")
            raise

    def handle_otp_confirmation(self):
        """Обработка ввода OTP кода"""
        try:
            # Получаем OTP код
            otp_code = self.get_otp_code()
            print(f"Вводим OTP код: {otp_code}")
            
            # Вводим код с клавиатуры
            self.page.keyboard.type(otp_code)
            sleep(1)
            
            # Ждем появления сообщения о принятии к обработке
            processing_message = "//div[contains(text(), 'принят к обработке')]"
            self.page.locator(processing_message).wait_for(timeout=5000)
            print("Платеж принят к обработке")
            
        except Exception as e:
            print(f"❌ Ошибка при вводе OTP: {str(e)}")
            raise

    def safe_return_to_main(self):
        """Безопасное возвращение на главную страницу"""
        try:
            self.page.locator("//a [@href='/']").nth(0).click()
        except Exception as e:
            print(f"Не удалось вернуться на главную страницу: {str(e)}")
