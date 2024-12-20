from playwright.sync_api import sync_playwright
from pages.Login_page import LoginPage
from pages.Otp_page import OtpPage
from pages.Exchange_page import ExchangePage1
from time import sleep
from Exceptions.Invalid_otp_exception import OTP_errors
from Exceptions.Loading_errors import Loading_errors
from Exceptions.Login_errors import Login_errors


def test_login_and_otp():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        # Работа с LoginPage
        login_page = LoginPage(page)
        login_page.navigate("https://ibank.kicb.net/login")
        login_page.login()

        # Работа с OtpPage
        otp_page = OtpPage(page)
        otp_key = "WTCSZCDIZXNQBX6FGWXUQ36EGU6ICVEI"
        try:
            otp_page.enter_otp(otp_key)
        except OTP_errors as e:
            print(f"Ошибка: {e}")
            otp_page.clear_otp_fields()  # Очищаем поля ввода
            otp_page.enter_otp(otp_key)  # Повторяем ввод OTP

 
        def error_catcher(otp_page, max_reloads=2, reloads=0):
            sleep(1)
            while reloads < max_reloads:
                try:
                    otp_page.listener_exchange_course1()
                    break  # Если курс обмена валюты успешно подгружен, выходим из цикла
                except Loading_errors as e:
                    print(f"Ошибка: {e}")
                    reloads += 1
                    page.reload()  # Перезагружаем страницу
                    error_catcher(otp_page, max_reloads, reloads)  # Вызываем функцию рекурсивно с обновленным счетчиком перезагрузок

        error_catcher(otp_page)        




            # обменка с доллара на сом
        exchange_page = ExchangePage1(page)
        exchange_page.exchange_1()
        exchange_page.account_locator()
        exchange_page.account_locator_som()
        exchange_page.account_locator_2()
        exchange_page.account_locator_dollar()
        exchange_page.amount_debit()
        sleep(2)
        exchange_page.exchange_button_accept()
        exchange_page.exchange_button_confirm()

        sleep(10)
        browser.close()