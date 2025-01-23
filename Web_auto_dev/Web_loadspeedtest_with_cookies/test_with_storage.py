import json
import time
from playwright.sync_api import sync_playwright

STORAGE_FILE = "storage_state.json"
COOKIE_FILE = "cookies.json"

def save_storage_state(context):
    """Сохранение состояния хранилища в файл."""
    context.storage_state(path=STORAGE_FILE)
    print(f"Состояние хранилища сохранено в {STORAGE_FILE}")

def test_perform_login(page, context):
    """Функция для выполнения логина."""
    page.goto("https://newibanktest.kicb.net/")
    page.wait_for_timeout(2000)  # Задержка для загрузки страницы

    # Логин
    page.wait_for_selector("input[type='text']")
    page.locator("input[type='text']").fill("aigerimk")
    page.locator("input[type='text']").press("Tab")

    # Пароль
    page.wait_for_selector("input[type='password']")
    page.locator("input[type='password']").fill("password1")

    # Входим в систему
    page.locator("button:has-text('Войти')").click()

    # Ожидаем появления поля для OTP
    page.wait_for_selector(".confirm-otp__input")

    # Вводим OTP код
    otp_code = "111111"  # Ваш OTP код
    for index, digit in enumerate(otp_code):
        page.locator(f"div:nth-child({index + 1}) > .confirm-otp__input").fill(digit)

    # Ждем, пока страница загрузится
    page.wait_for_selector("//span[contains(text(), '29 529.53 ₸')]")
    save_storage_state(context)  # Сохраняем состояние хранилища после успешного входа

    # Выйти из аккаунта
    page.locator("//div[@class='header-bar__btn'] //img").wait_for(timeout=5000)
    page.locator("//div[@class='header-bar__btn'] //img").click()


def measure_loading_time(page):
    page.goto("https://newibanktest.kicb.net/")
    page.wait_for_timeout(2000)  # Задержка для загрузки страницы

    # Логин
    page.wait_for_selector("input[type='text']")
    page.locator("input[type='text']").fill("aigerimk")
    page.locator("input[type='text']").press("Tab")

    # Пароль
    page.wait_for_selector("input[type='password']")
    page.locator("input[type='password']").fill("password1")

    # Входим в систему
    page.locator("button:has-text('Войти')").click()

    # Ожидаем появления поля для OTP
    page.wait_for_selector(".confirm-otp__input")

    # Вводим OTP код
    otp_code = "111111"  # Ваш OTP код
    for index, digit in enumerate(otp_code):
        page.locator(f"div:nth-child({index + 1}) > .confirm-otp__input").fill(digit)
    start_time = time.time()
    # Ждем, пока страница загрузится
    page.locator("//span[contains(text(), '29 529.53 ₸')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Платежи')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Платежи')]").click()
    page.locator("//p[contains(text(), 'Оплата штрафов безопасный город')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'История')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'История')]").click()
    page.locator("//span[contains(text(), 'Сегодня')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Витрина')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Витрина')]").click()
    page.locator("//span[contains(text(), 'Получить справку по кредиту')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Сообщения')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Сообщения')]").click()
    page.locator("//div[contains(text(), 'Жалобы')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Профиль')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Профиль')]").click()
    page.locator("//div[contains(text(), 'Номер телефона')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Счета')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Счета')]").click()
    page.locator("//span[contains(text(), '29 529.53 ₸')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Платежи')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Платежи')]").click()
    page.locator("//p[contains(text(), 'Оплата штрафов безопасный город')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'История')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'История')]").click()
    page.locator("//span[contains(text(), 'Сегодня')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Витрина')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Витрина')]").click()
    page.locator("//span[contains(text(), 'Получить справку по кредиту')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Сообщения')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Сообщения')]").click()
    page.locator("//div[contains(text(), 'Жалобы')]").wait_for(timeout=300000)

    page.locator("//a[contains(text(),'Профиль')]").wait_for(timeout=300000)
    page.locator("//a[contains(text(),'Профиль')]").click()
    page.locator("//div[contains(text(), 'Номер телефона')]").wait_for(timeout=300000)

    page.locator("//div[@class='header-bar__btn'] //img").wait_for(timeout=5000)
    page.locator("//div[@class='header-bar__btn'] //img").click()



    end_time = time.time()
    loading_time = end_time - start_time
    print(f"Время загрузки страницы : {loading_time:.2f} секунд")
    return loading_time

def test_50_times(page):
    """Функция для выполнения теста 50 раз."""
    total_time = 0
    for _ in range(50):
        loading_time = measure_loading_time(page)
        total_time += loading_time

    average_time = total_time / 1
    print(f"Среднее время загрузки за 50 тестов: {average_time:.2f} секунд")
