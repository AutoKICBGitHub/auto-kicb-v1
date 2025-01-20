import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from utils.capabilities import get_ios_simulator_capabilities
from pages.login_page import LoginPage
from pages.otp_page import OTPPage
from pages.loader_page import LoaderPage
from selenium.common.exceptions import NoSuchElementException
import time

# Константа с bundle ID приложения
APP_BUNDLE_ID = 'kg.cbk.mobile'  # Используйте реальный bundle ID вашего приложения


def is_user_logged_in(driver):
    """Проверка, авторизован ли пользователь"""
    try:
        # Проверяем наличие имени пользователя на главном экране
        user_name = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Ырысбеков Атай Айбекович")
        return user_name.is_displayed()
    except NoSuchElementException:
        return False


def is_login_required(driver):
    """Проверка, нужен ли логин"""
    try:
        # Сначала ждем загрузочный экран
        loader_page = LoaderPage(driver)
        loader_page.wait_for_loader_to_disappear()
        
        # Затем проверяем наличие поля для ввода логина
        login_field = driver.find_element(
            AppiumBy.XPATH, 
            "//XCUIElementTypeSecureTextField[@value='Логин']"
        )
        return login_field.is_displayed()
    except NoSuchElementException:
        return False


def force_close_app(driver):
    """Закрытие приложения через кнопку назад/крестик"""
    try:
        # Локатор для кнопки назад/крестик
        back_button = '//XCUIElementTypeButton[@name="Назад"]'
        
        # Пытаемся найти и нажать кнопку назад
        try:
            driver.find_element(AppiumBy.XPATH, back_button).click()
            print("✅ Выполнен переход назад")
            time.sleep(1)  # Даем время на анимацию
            return True
        except NoSuchElementException:
            # Если не нашли кнопку "Назад", попробуем поискать другие варианты
            try:
                # Можно добавить другие варианты кнопок возврата
                alt_back_button = '//XCUIElementTypeButton[@name="Close"]'
                driver.find_element(AppiumBy.XPATH, alt_back_button).click()
                print("✅ Выполнен переход назад (альтернативная кнопка)")
                time.sleep(1)
                return True
            except NoSuchElementException:
                print("ℹ️ Кнопка возврата не найдена, возможно уже на главном экране")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка при возврате на предыдущий экран: {e}")
        return False


@pytest.fixture(scope="session")
def driver():
    # Инициализация драйвера
    caps = get_ios_simulator_capabilities()
    options = XCUITestOptions()
    for key, value in caps.items():
        options.set_capability(key, value)
    
    driver = None
    try:
        driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723',
            options=options
        )
        yield driver
    finally:
        if driver:
            driver.quit()


@pytest.fixture(autouse=True)
def restart_app(driver):
    """Перезапуск приложения после каждого теста"""
    yield
    # Запускаем приложение заново только если нужно
    if not is_user_logged_in(driver):
        try:
            driver.execute_script('mobile: launchApp', {'bundleId': APP_BUNDLE_ID})
            print("✅ Приложение перезапущено")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Ошибка при перезапуске приложения: {e}")


@pytest.fixture(scope="function")
def setup(driver):
    # Проверяем, авторизован ли пользователь
    if is_user_logged_in(driver):
        print("✅ Пользователь уже авторизован, пропускаем шаги логина")
        yield
        return
        
    # Проверяем, нужен ли логин
    if is_login_required(driver):
        # Логин
        login_page = LoginPage(driver)
        login_page.login_as_valid_user()
        
        # Ввод OTP
        otp_page = OTPPage(driver)
        assert otp_page.is_page_displayed(), "Страница OTP не отображается"
        otp_page.enter_otp()
    else:
        print("ℹ️ Форма логина не найдена, возможно пользователь уже авторизован")
    
    yield
