import pytest
from pages.main_page import MainPage
from pages.transfer_kicb_page import TransferKICBPage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
import time


@pytest.mark.transfers
class TestTransfers:
    
    @pytest.fixture(autouse=True)
    def setup_test(self, driver, setup):
        """Подготовка к каждому тесту"""
        self.driver = driver
        self.main_page = MainPage(self.driver)
        self.transfer_page = TransferKICBPage(self.driver)
        
        # Переход в раздел платежей
        self.main_page.go_to_payments()
        time.sleep(2)  # Ждем загрузку страницы
        
        yield
        
        # После каждого теста возвращаемся на главный экран
        try:
            back_button = '//XCUIElementTypeButton[@name="Назад"]'
            self.driver.find_element(AppiumBy.XPATH, back_button).click()
            print("✅ Возврат на главный экран")
            time.sleep(1)
        except NoSuchElementException:
            print("ℹ️ Уже на главном экране")
        except Exception as e:
            print(f"❌ Ошибка при возврате на главный экран: {e}")
    
    def test_transfer_by_card(self):
        """Тест перевода по номеру карты"""
        self.transfer_page.transfer_by_card("4446791000018356")
    
    def test_transfer_by_phone(self):
        """Тест перевода по номеру телефона"""
        self.transfer_page.transfer_by_phone("555515516")

    def test_transfer_by_account(self):
        """Тест перевода по номеру счета"""
        self.transfer_page.transfer_by_account("1280016057421282")        