import pytest
from pages.main_page import MainPage
from appium.webdriver.common.appiumby import AppiumBy
import time


@pytest.mark.smoke
def test_navigation_to_payments(driver, setup):
    """
    Тест проверяет:
    1. Отображение главной страницы
    2. Переход на страницу платежей
    3. Отображение страницы платежей
    """
    # Инициализация главной страницы
    main_page = MainPage(driver)
    assert main_page.is_main_page_displayed(), "Главная страница не отображается"
    
    # Переход в платежи
    main_page.go_to_payments()
    
    # Проверка, что мы на странице платежей
    time.sleep(2)  # Даем время на загрузку страницы
    payments_title = driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Платежи"]')
    assert payments_title.is_displayed(), "Страница платежей не отображается" 