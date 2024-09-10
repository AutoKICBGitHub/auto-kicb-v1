import time
import logging
import pyotp
from playwright.sync_api import sync_playwright

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция для выполнения автотеста
def test_1(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    logger.info("Переход на страницу входа")
    page.goto("https://ibank.kicb.net/")
    page.goto("https://ibank.kicb.net/login")

    # Ожидание загрузки элементов с таймаутом 30 секунд
    logger.info("Заполнение учетных данных")
    page.locator("input[type=\"text\"]").wait_for(timeout=30000)
    page.locator("input[type=\"text\"]").fill("ataiy")
    page.locator("input[type=\"text\"]").press("Tab")

    page.locator("input[type=\"password\"]").wait_for(timeout=30000)
    page.locator("input[type=\"password\"]").fill("Wsvoboda666")
    time.sleep(2)
    page.locator("input[type=\"password\"]").press("Enter")

    # Ввод OTP через клавиатуру
    logger.info("Ожидание ввода OTP")
    secret = 'WTCSZCDIZXNQBX6FGWXUQ36EGU6ICVEI'
    totp = pyotp.TOTP(secret, interval=30, digest='sha1')
    otp_code = totp.now()
    page.locator(".confirm-otp__input").first.wait_for(timeout=30000)
    page.locator(".confirm-otp__input").first.click()
    page.keyboard.type(otp_code)

    try:
        # Пробуем найти карту 'ELCARD CHIP'
        page.locator("text='ELCARD CHIP'").nth(0).wait_for(timeout=10000)
        logger.info("Карты успешно загружены.")
        cards_loaded = True
    except:
        logger.error("Карты не удалось загрузить после нескольких попыток.")
        page.reload()

    #Платежи
    page.locator("//nav [@class='header-nav'] //a ").nth(1).wait_for(timeout=60000)
    page.locator("//nav [@class='header-nav'] //a ").nth(1).click()

    # Поиск кнопки по классу и тексту
    page.locator("p.operation-card__text:has-text('Обмен валют')").wait_for(timeout=60000)
    page.locator("p.operation-card__text:has-text('Обмен валют')").click()

    # Выбор счета 1
    page.locator("//div [@class='popup-select']").nth(0).wait_for(timeout=60000)
    page.locator("//div [@class='popup-select']").nth(0).click()
    # Выбор счета в долларах
    page.locator("//div [@class='popup-select'] //li").nth(6).wait_for(timeout=10000)
    page.locator("//div [@class='popup-select'] //li").nth(6).click()

    # Выбор счета 2
    page.locator("//div [@class='popup-select']").nth(1).wait_for(timeout=60000)
    page.locator("//div [@class='popup-select']").nth(1).click()
    # Выбор счета в сомах
    page.locator("//div [@class='popup-select'] //li").nth(5).wait_for(timeout=10000)
    page.locator("//div [@class='popup-select'] //li").nth(5).click()

    page.locator("//div [@class='exchange-fields'] //label").nth(0).fill("1")
    page.locator("//div [@class='transfer-own__button'] //button").is_visible(timeout=10000)
    page.locator("//div [@class='transfer-own__button'] //button").click()

    time.sleep(1)

    page.locator("//button [@class='custom-button custom-button--active']").wait_for(timeout=10000)
    page.locator("//button [@class='custom-button custom-button--active']").click()

    page.locator("//nav [@class='header-nav'] //a ").nth(0).click()

    time.sleep(5)

    # Платежи
    page.locator("//nav [@class='header-nav'] //a ").nth(1).wait_for(timeout=60000)
    page.locator("//nav [@class='header-nav'] //a ").nth(1).click()

    # Поиск кнопки по классу и тексту
    page.locator("p.operation-card__text:has-text('Обмен валют')").wait_for(timeout=60000)
    page.locator("p.operation-card__text:has-text('Обмен валют')").click()

    # Выбор счета 1
    page.locator("//div [@class='popup-select']").nth(0).wait_for(timeout=60000)
    page.locator("//div [@class='popup-select']").nth(0).click()
    # Выбор счета в долларах
    page.locator("//div [@class='popup-select'] //li").nth(5).wait_for(timeout=10000)
    page.locator("//div [@class='popup-select'] //li").nth(5).click()

    # Выбор счета 2
    page.locator("//div [@class='popup-select']").nth(1).wait_for(timeout=60000)
    page.locator("//div [@class='popup-select']").nth(1).click()
    # Выбор счета в сомах
    page.locator("//div [@class='popup-select'] //li").nth(6).wait_for(timeout=10000)
    page.locator("//div [@class='popup-select'] //li").nth(6).click()

    page.locator("//div [@class='exchange-fields'] //label").nth(1).fill("1")
    page.locator("//div [@class='transfer-own__button'] //button").is_visible(timeout=10000)
    page.locator("//div [@class='transfer-own__button'] //button").click()

    time.sleep(1)

    page.locator("//button [@class='custom-button custom-button--active']").wait_for(timeout=10000)
    page.locator("//button [@class='custom-button custom-button--active']").click()

    page.locator("//nav [@class='header-nav'] //a ").nth(0).click()
    # Завершение работы и закрытие браузера
    logger.info("Завершение теста и закрытие браузера")
    context.close()
    browser.close()


