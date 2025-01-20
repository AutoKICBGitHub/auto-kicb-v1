import pytest
from pages.main_page import MainPage
from pages.exchange_page import ExchangePage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
import time


@pytest.mark.exchange
class TestExchange:
    
    @pytest.fixture(autouse=True)
    def setup_test(self, driver, setup):
        """Подготовка к каждому тесту"""
        self.driver = driver
        self.main_page = MainPage(self.driver)
        self.exchange_page = ExchangePage(self.driver)
        
        # Переход в раздел платежей
        self.main_page.go_to_payments()
        time.sleep(2)
        
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
    
    def test_exchange_som_to_dollar(self):
        """Тест обмена сомов на доллары"""
        self.exchange_page.exchange_som_to_dollar("10")
    
    def test_exchange_dollar_to_som(self):
        """Тест обмена долларов на сомы"""
        self.exchange_page.exchange_dollar_to_som("0.11") 