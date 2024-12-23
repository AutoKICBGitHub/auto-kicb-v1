from playwright.sync_api import sync_playwright
from pages.Login_page import LoginPage
from pages.Otp_page import OtpPage
from pages.Exchange_page import ExchangePage1
from time import sleep
from Exceptions.Invalid_otp_exception import OTP_errors
from Exceptions.Loading_errors import Loading_errors
from Exceptions.Login_errors import Login_errors




def test_exchange_flow():
    with sync_playwright() as playwright:
        # Укажите путь к папке профиля
        user_data_dir = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\Default"  # Замените на путь к вашему профилю
        # Используем launch_persistent_context для открытия браузера с пользовательским профилем
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False  # Открываем браузер в обычном режиме
        )
        page = context.new_page()
        page.goto("https://ibank.kicb.net/")
            
        # Работа с LoginPage
        login_page = LoginPage(page)
        otp_page = OtpPage(page)
        sleep(3)
        
        # Проверка текущего URL
        if login_page.page.locator(login_page.username_input).is_visible() and login_page.page.locator(login_page.password_input).is_visible():
            print("Находимся на странице входа.")
            
            
            print("Находимся на странице входа.") 
            login_page.login()
            
            
            
            otp_key = "WTCSZCDIZXNQBX6FGWXUQ36EGU6ICVEI"
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
             
            
        


        # обменка с доллара на сом
        exchange_page = ExchangePage1(page)
        exchange_page.exchange_1()
        # обменка с сома на доллар 
        exchange_page.exchange_2()

        

 
        context.close()  # Закрываем контекст, что также закроет браузер