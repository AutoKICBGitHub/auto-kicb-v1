import json
import time
from playwright.sync_api import sync_playwright

# Путь для хранения файлов
STORAGE_FILE = "storage_state.json"
COOKIE_FILE = "cookies.json"


def save_storage_state(context):
    """Сохранение storage state (включает куки и данные локального хранилища) в файл."""
    context.storage_state(path=STORAGE_FILE)
    print(f"Состояние хранилища сохранено в {STORAGE_FILE}")


def load_storage_state(context):
    """Загрузка storage state из файла."""
    try:
        context.storage_state(path=STORAGE_FILE)
        print(f"Состояние хранилища загружено из {STORAGE_FILE}")
    except FileNotFoundError:
        print("Файл с storage не найден. Логин через UI.")


def save_cookies(context):
    """Сохранение куки в файл."""
    with open(COOKIE_FILE, "w") as f:
        cookies = context.cookies()
        json.dump(cookies, f)


def load_cookies(context):
    """Загрузка куки из файла."""
    try:
        with open(COOKIE_FILE, "r") as f:
            cookies = json.load(f)
            context.add_cookies(cookies)
            print("Куки загружены.")
    except FileNotFoundError:
        print("Файл с куки не найден.")


def perform_login(page):
    """Функция для выполнения логина."""
    page.goto("https://newibanktest.kicb.net/")
    time.sleep(5)  # Задержка для загрузки страницы

    # Логин
    page.wait_for_selector("input[type=\"text\"]")
    page.locator("input[type=\"text\"]").fill("aigerimk")
    page.locator("input[type=\"text\"]").press("Tab")

    # Пароль
    page.wait_for_selector("input[type=\"password\"]")
    page.locator("input[type=\"password\"]").fill("password1")

    # Входим в систему
    page.locator("button:has-text('Войти')").click()

    # Ожидаем появления поля для OTP
    page.wait_for_selector(".confirm-otp__input")

    # Вводим OTP код
    otp_code = "111111"  # Ваш OTP код
    for index, digit in enumerate(otp_code):
        page.locator(f"div:nth-child({index + 1}) > .confirm-otp__input").fill(digit)

    # Ждем некоторое время для завершения процесса логина
    time.sleep(40)  # Ждем загрузку всех элементов

    # Сохраняем состояние после успешного входа
    save_storage_state(page.context)
    save_cookies(page.context)


def measure_loading_time(page, url):
    """Измеряем время загрузки страницы."""
    start_time = time.time()
    page.goto(url)
    page.wait_for_load_state('networkidle')  # Ждем, пока страница загрузится
    end_time = time.time()
    loading_time = end_time - start_time
    print(f"Время загрузки страницы {url}: {loading_time:.2f} секунд")
    return loading_time


with sync_playwright() as p:
    # Запускаем браузер
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    # Открываем пустую страницу
    page = context.new_page()

    # Загружаем состояние хранилища
    load_storage_state(context)

    # Переходим на сайт и выполняем логин
    perform_login(page)

    # Ждем 40 секунд для полной загрузки элементов
    time.sleep(40)

    # Теперь проверяем загрузку страницы 50 раз
    url_to_test = "https://newibanktest.kicb.net/login"
    for attempt in range(50):
        print(f"Попытка {attempt + 1} из 50...")
        perform_login(page)
        loading_time = measure_loading_time(page, url_to_test)
        print(f"Попытка {attempt + 1} завершена. Время загрузки: {loading_time:.2f} секунд.")

    # Закрываем страницу и браузер
    page.close()
    browser.close()
