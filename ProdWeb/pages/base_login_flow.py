from pages.Login_page import LoginPage
from pages.Otp_page import OtpPage
from time import sleep
from Exceptions.Invalid_otp_exception import OTP_errors
from Exceptions.Loading_errors import Loading_errors


class Login_flow():
    def test_login_flow(self, page):
        # Работа с LoginPage
        login_page = LoginPage(page)
        otp_page = OtpPage(page)
        sleep(3)

        # Проверка текущего URL
        if login_page.page.locator(login_page.username_input).is_visible() and login_page.page.locator(login_page.password_input).is_visible():
            print("Находимся на странице входа.")
            login_page.login()

            otp_key = login_page.otp_key_google
            try:
                otp_page.enter_otp(otp_key)
            except OTP_errors as e:
                print(f"Ошибка: {e}")
                otp_page.clear_otp_fields()  # Очищаем поля ввода
                otp_page.enter_otp(otp_key)  # Повторяем ввод OTP

            def error_catcher(otp_page, max_reloads=2, reloads=0):
                sleep(10)
                while reloads < max_reloads:
                    try:
                        otp_page.listener_exchange_course1()
                        break  # Если курс обмена валюты успешно подгружен, выходим из цикла
                    except Loading_errors as e:
                        print(f"Ошибка: {e}")
                        reloads += 1
                        page.reload()  # Перезагружаем страницу
                        error_catcher(otp_page, max_reloads, reloads)

            error_catcher(otp_page)      
        else:
            print(page)
            print("Не удалось перейти на страницу входа.")
            otp_page.accounts_status()     

