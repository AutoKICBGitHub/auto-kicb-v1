from playwright.sync_api import sync_playwright
import time
import random

def generate_passport_number():
    """Генерирует случайный номер паспорта в формате ID + 7 цифр"""
    return f"ID{random.randint(1000000, 9999999)}"

def generate_kg_inn():
    """Генерирует случайный ИНН Кыргызстана (14 цифр)"""
    # Первая цифра: 1 или 2 (код пола)
    gender_code = random.choice([1, 2])
    
    # Следующие 8 цифр: дата рождения (YYYYMMDD)
    year = random.randint(1970, 2005)  # Случайный год рождения
    month = random.randint(1, 12)      # Случайный месяц
    day = random.randint(1, 28)        # Случайный день (28 чтобы избежать проблем с февралем)
    
    birth_date = f"{day:02d}{month:02d}{year:04d}"
    
    # Последние 5 цифр: случайные
    random_digits = random.randint(10000,11111)
    
    # Собираем ИНН
    inn = f"{gender_code}{birth_date}{random_digits}"
    
    return inn

def generate_cyrillic_word():
    """Генерирует случайное слово на кириллице"""
    workplaces = ["БишкекМунай", "КыргызБанк", "АсиаТелеком", "МанасУнивер", "БакайБанк", "ДемирКыргыз", "КыргызстанТелеком"]
    positions = ["Менеджер", "Инженер", "Экономист", "Бухгалтер", "Аналитик", "Консультант", "Специалист"]
    
    return random.choice(workplaces + positions)

def run_automation():
    """Автоматизация работы с CBS системой"""
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        customer_id = "00845707"

        # Убираем признаки автоматизации
        page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # Открываем ссылку
            page.goto("https://localhost:8101/FCJNeoWeb/SMMDIFRM.jsp")
            
            time.sleep(2)
            # Нажимаем OK в Alert
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            
            # Вводим логин "меерида" с имитацией человеческого ввода
            login_field = page.locator("//input [@id='LOGINUSERID']")
            login_field.wait_for(state="visible", timeout=60000)
            login_field.fill("meerimda")
            
            # Вводим пароль " " (пробел)
            password_field = page.locator("//input [@id='user_pwd']")
            password_field.fill(" ")

            # Нажимаем OK в Alert после ввода логина/пароля
            page.keyboard.press('Enter')
           
            
            # Нажимаем OK в Alert
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            
            # Убираем блокирующие элементы
            try:
                page.evaluate("document.getElementById('masker').style.display = 'none'")
                page.evaluate("document.getElementById('Div_ChildWin').style.display = 'none'")
                print("Убрали блокирующие элементы")
            except:
                pass
            
            branch533= page.locator("//li [@title='533']")
            branch533.wait_for(state="visible", timeout=60000)
            
            # Пробуем обычный клик
            try:
                branch533.click()
                print("Клик по branch533 успешен")
            except:
                # Если не работает, используем JavaScript клик
                page.evaluate("document.querySelector('li[title=\"533\"]').click()")
                print("Использован JavaScript клик по branch533")

            select_branch =  page.locator("//li [@id='select_branch']")
            select_branch.wait_for(state="visible", timeout=60000)
            select_branch.click()
 
            # Ждем загрузки iframe с Branch Code
            
            
            
            # Переключаемся на iframe
            iframe = page.frame_locator("#ifrSubScreen")
            
            # Теперь ищем поле Branch Code внутри iframe
            Branch_code = iframe.locator("//input[@id='1']")
            Branch_code.wait_for(state="visible", timeout=60000)
            Branch_code.clear()  # Очищаем поле от значения "%"
            Branch_code.fill("700")
            print("Поле Branch Code заполнено")
           
 
            # Кнопка Fetch тоже находится внутри iframe
            fetch = iframe.locator("//button[contains(text(),'Fetch')]")
            fetch.wait_for(state="visible", timeout=60000)
            fetch.click()
            print("Кнопка Fetch нажата")


            change_branch = iframe.locator("//a [contains(text(),'TRANSACTION INPUT')]")
            change_branch.wait_for(state="visible", timeout=60000)
            change_branch.click()


            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            
            # Нажимаем на кнопку меню
            menu_button = page.locator("#menuExpandCollapse")
            menu_button.wait_for(state="visible", timeout=60000)
            menu_button.click()
            print("Кнопка меню нажата")
            
            # Нажимаем на Customers
            customers_button = page.locator("#Fid20A")
            customers_button.wait_for(state="visible", timeout=60000)
            customers_button.click()
            print("Customers нажат")
            
            # Нажимаем на Operations
            operations_button = page.locator("#Fid21A")
            operations_button.wait_for(state="visible", timeout=60000)
            operations_button.click()
            print("Operations нажат")
            
            # Нажимаем на Customer Input
            customer_input_button = page.locator("#STDCIF\\|CIF")
            customer_input_button.wait_for(state="visible", timeout=60000)
            customer_input_button.click()
            print("Customer Input нажат")

           
            
            # Переключаемся на iframe с Customer Input
            customer_iframe = page.frame_locator("iframe").first
            

            
            enter_query = customer_iframe.locator("//a[contains(text(),'Enter Query')]")
            enter_query.wait_for(state="visible", timeout=60000)
            enter_query.click()
            print("Enter Query нажат")

            customer_field = customer_iframe.locator("#BLK_CUSTOMER__CUSTNO")
            customer_field.wait_for(state="visible", timeout=60000)
            customer_field.clear()
            customer_field.fill(customer_id)
            print("Customer No заполнен")

            execute_query = customer_iframe.locator("//a[contains(text(),'Execute Query')]")
            execute_query.wait_for(state="visible", timeout=60000)
            execute_query.click()
            print("Execute Query нажат")
            
            # Генерируем случайные данные
            passport_number = generate_passport_number()
            kg_inn = generate_kg_inn()
            print(f"Сгенерированный номер паспорта: {passport_number}")
            print(f"Сгенерированный ИНН: {kg_inn}")
            
            # Нажимаем на Unlock
            unlock_button = customer_iframe.locator("//a[contains(text(),'Unlock')]")
            unlock_button.wait_for(state="visible", timeout=60000)
            unlock_button.click()
            print("Кнопка Unlock нажата")
            
            # Вводим Customer Category
            customer_category_field = customer_iframe.locator("#BLK_CUSTOMER__CCATEG")
            customer_category_field.wait_for(state="visible", timeout=60000)
            customer_category_field.clear()
            customer_category_field.fill("INDV.RES")
            print("Customer Category заполнена")
            
            # Меняем номер паспорта на случайный
            passport_field = customer_iframe.locator("#BLK_CUSTPERSONAL__PPTNO")
            passport_field.wait_for(state="visible", timeout=60000)
            passport_field.clear()
            passport_field.fill(passport_number)
            print("Passport Number заполнен")
            
            # Нажимаем на Auxiliary
            auxiliary_button = customer_iframe.locator("//span[contains(text(),'Auxiliary')]")
            auxiliary_button.wait_for(state="visible", timeout=60000)
            auxiliary_button.click()
            print("Auxiliary нажат")
            
            # Изменяем последние 5 цифр в поле UDF1
            udf1_field = customer_iframe.locator("#BLK_CUSTOMER__UDF1")
            udf1_field.wait_for(state="visible", timeout=60000)
            
            # Получаем текущее значение ИНН
            current_inn = udf1_field.input_value()
            print(f"Текущий ИНН: {current_inn}")
            
            # Берем первые 9 символов и добавляем новые 5 случайных цифр
            if len(current_inn) >= 9:
                new_random_digits = random.randint(10000, 99999)
                new_inn = current_inn[:9] + str(new_random_digits)
            else:
                new_inn = kg_inn  # Если поле пустое, используем сгенерированный ИНН
            
            udf1_field.click()
            udf1_field.clear()
            udf1_field.fill(new_inn)
            print(f"UDF1 (ИНН) изменен: {new_inn}")
            
            # Проверяем что поле действительно заполнилось
            filled_value = udf1_field.input_value()
            print(f"Проверка UDF1: {filled_value}")
            
            # Нажимаем на Domestic
            domestic_button = customer_iframe.locator("//a[contains(text(),'Domestic')]")
            domestic_button.wait_for(state="visible", timeout=60000)
            domestic_button.click()
            print("Domestic нажат")
            
           
            
            # Переключаемся на iframe Domestic Details
            domestic_iframe = customer_iframe.frame_locator("#ifrSubScreen")
            
            # Выбираем случайный статус в Marital Status
            print("Выбираем Marital Status...")
            marital_options = ["M", "D", "R", "S", "P", "E"]
            selected_status = random.choice(marital_options)
            
            # Заполняем Marital Status в iframe
            marital_status_field = domestic_iframe.locator("select.SELstd#BLK_CUSTDOMESTIC__MARITALSTAT")
            marital_status_field.wait_for(state="visible", timeout=60000)
            marital_status_field.select_option(selected_status)
            print(f"Выбран Marital Status: {selected_status}")
            
            # Нажимаем OK для Domestic Details
            ok_button = domestic_iframe.locator("#BTN_OK")
            ok_button.wait_for(state="visible", timeout=60000)
            ok_button.click()
            print("OK для Domestic нажат")
            
     
            
            # Нажимаем на Professional
            professional_button = customer_iframe.locator("//a[contains(text(),'Professional')]")
            professional_button.wait_for(state="visible", timeout=60000)
            professional_button.click()
            print("Professional нажат")
            
    
            
            # Переключаемся на iframe Professional Details
            professional_iframe = customer_iframe.frame_locator("#ifrSubScreen")
            
            # Генерируем случайные слова на кириллице
            workplace = generate_cyrillic_word()
            position = generate_cyrillic_word()
            print(f"Место работы: {workplace}, Должность: {position}")
            
            # Заполняем место работы
            workplace_field = professional_iframe.locator("#BLK_CUSTPROF__PREVEMP")
            workplace_field.wait_for(state="visible", timeout=60000)
            workplace_field.fill(workplace)
            print("Место работы заполнено")
            
            # Заполняем должность
            position_field = professional_iframe.locator("#BLK_CUSTPROF__CURRDESIG")
            position_field.wait_for(state="visible", timeout=60000)
            position_field.fill(position)
            print("Должность заполнена")

            
            # Нажимаем OK для Professional Details
            ok_button = professional_iframe.locator("#BTN_OK")
            ok_button.wait_for(state="visible", timeout=60000)
            ok_button.click()
            print("Professional заполнен")
            
            
            
            # Нажимаем на Save для сохранения всех данных
            save_button = customer_iframe.locator("//a[contains(text(),'Save')]")
            save_button.wait_for(state="visible", timeout=60000)
            save_button.click()
            print("Save нажат - данные сохранены")
            
            
            # Переключаемся на iframe Alert
            alert_iframe = customer_iframe.frame_locator("#ifr_AlertWin")
            


            # Нажимаем Accept
            accept_button = alert_iframe.locator("#BTN_ACCEPT")
            accept_button.wait_for(state="visible", timeout=60000)
            accept_button.click()
            print("Accept нажат")
            
            # Нажимаем Ok в Alert
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Alert Ok нажат")
            
            
            # Закрываем Customer Maintenance iframe
            customer_maintenance_iframe = page.frame_locator("iframe[id*='ifr_LaunchWin']")
            close_button = customer_maintenance_iframe.locator("#WNDbuttons")
            close_button.wait_for(state="visible", timeout=60000)
            close_button.click()
            print("Customer Maintenance закрыт")

            branch700= page.locator("//li [@title='700']")
            branch700.wait_for(state="visible", timeout=60000)
            branch700.click()
            
            

            home_branch = page.locator("//li [@id='home_branch']")
            home_branch.wait_for(state="visible", timeout=60000)
            home_branch.click()

            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            
            # Нажимаем на пользователя (Nurbekova Elina)
            user_menu = page.locator("//li[@class='user']")
            user_menu.wait_for(state="visible", timeout=60000)
            user_menu.click()
            print("Меню пользователя открыто")
            
            # Выбираем Sign Off
            sign_off_button = page.locator("//li[contains(text(),'Sign Off')]")
            sign_off_button.wait_for(state="visible", timeout=60000)
            sign_off_button.click()
            print("Sign Off нажат")


            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()

            time.sleep(3)

            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            
            # Вводим логин "меерида" с имитацией человеческого ввода
            login_field = page.locator("//input [@id='LOGINUSERID']")
            login_field.wait_for(state="visible", timeout=60000)
            login_field.fill("elinan")
            
            # Вводим пароль " " (пробел)
            password_field = page.locator("//input [@id='user_pwd']")
            password_field.fill(" ")

            # Нажимаем OK в Alert после ввода логина/пароля
            page.keyboard.press('Enter')


           
            
            # Нажимаем OK в Alert
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()

            branch533= page.locator("//li [@title='533']")
            branch533.wait_for(state="visible", timeout=60000)
            
            # Пробуем обычный клик
            try:
                branch533.click()
                print("Клик по branch533 успешен")
            except:
                # Если не работает, используем JavaScript клик
                page.evaluate("document.querySelector('li[title=\"533\"]').click()")
                print("Использован JavaScript клик по branch533")

            select_branch =  page.locator("//li [@id='select_branch']")
            select_branch.wait_for(state="visible", timeout=60000)
            select_branch.click()
 
            # Ждем загрузки iframe с Branch Code
            
            
            
            # Переключаемся на iframe
            iframe = page.frame_locator("#ifrSubScreen")
            
            # Теперь ищем поле Branch Code внутри iframe
            Branch_code = iframe.locator("//input[@id='1']")
            Branch_code.wait_for(state="visible", timeout=60000)
            Branch_code.clear()  # Очищаем поле от значения "%"
            Branch_code.fill("700")
            print("Поле Branch Code заполнено")
           
 
            # Кнопка Fetch тоже находится внутри iframe
            fetch = iframe.locator("//button[contains(text(),'Fetch')]")
            fetch.wait_for(state="visible", timeout=60000)
            fetch.click()
            print("Кнопка Fetch нажата")


            change_branch = iframe.locator("//a [contains(text(),'TRANSACTION INPUT')]")
            change_branch.wait_for(state="visible", timeout=60000)
            change_branch.click()


            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            
            # Нажимаем на кнопку меню
            menu_button = page.locator("#menuExpandCollapse")
            menu_button.wait_for(state="visible", timeout=60000)
            menu_button.click()
            print("Кнопка меню нажата")
            
            # Нажимаем на Customers
            customers_button = page.locator("#Fid20A")
            customers_button.wait_for(state="visible", timeout=60000)
            customers_button.click()
            print("Customers нажат")
            
            # Нажимаем на Operations
            operations_button = page.locator("#Fid21A")
            operations_button.wait_for(state="visible", timeout=60000)
            operations_button.click()
            print("Operations нажат")
            
            # Нажимаем на Customer Input
            customer_input_button = page.locator("#STDCIF\\|CIF")
            customer_input_button.wait_for(state="visible", timeout=60000)
            customer_input_button.click()
            print("Customer Input нажат")

           
            
            # Переключаемся на iframe с Customer Input
            customer_iframe = page.frame_locator("iframe").first
            

            
            enter_query = customer_iframe.locator("//a[contains(text(),'Enter Query')]")
            enter_query.wait_for(state="visible", timeout=60000)
            enter_query.click()
            print("Enter Query нажат")

            customer_field = customer_iframe.locator("#BLK_CUSTOMER__CUSTNO")
            customer_field.wait_for(state="visible", timeout=60000)
            customer_field.clear()
            customer_field.fill(customer_id)
            print("Customer No заполнен")

            execute_query = customer_iframe.locator("//a[contains(text(),'Execute Query')]")
            execute_query.wait_for(state="visible", timeout=60000)
            execute_query.click()
            print("Execute Query нажат")
            
            # Нажимаем на Authorize
            authorize_button = customer_iframe.locator("//a[contains(text(),'Authorize')]")
            authorize_button.wait_for(state="visible", timeout=60000)
            authorize_button.click()
            print("Authorize нажат")
            
            launch_frame = page.frame_locator("#ifr_LaunchWin")

            # Переключаемся на iframe авторизации
            authorize_iframe = launch_frame.frame_locator("#ifrSubScreen")



            
            accept_button = customer_iframe.frame_locator("#ifrSubScreen").locator("#BTN_OK")
            accept_button.wait_for(state="visible", timeout=5000)
            accept_button.click()
            print("Accept нажат через customer_iframe - авторизация завершена")
    

    

            # Обрабатываем Alert после авторизации
            alert_iframe = customer_iframe.frame_locator("#ifrSubScreen").frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Alert после авторизации обработан")
            
            # Закрываем Customer Maintenance iframe
            customer_maintenance_iframe = page.frame_locator("iframe[id*='ifr_LaunchWin']")
            close_button = customer_maintenance_iframe.locator("#WNDbuttons")
            close_button.wait_for(state="visible", timeout=60000)
            close_button.click()
            print("Customer Maintenance закрыт")

            branch700= page.locator("//li [@title='700']")
            branch700.wait_for(state="visible", timeout=60000)
            branch700.click()
            
            home_branch = page.locator("//li [@id='home_branch']")
            home_branch.wait_for(state="visible", timeout=60000)
            home_branch.click()

            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            
            # Нажимаем на пользователя (Nurbekova Elina)
            user_menu = page.locator("//li[@class='user']")
            user_menu.wait_for(state="visible", timeout=60000)
            user_menu.click()
            print("Меню пользователя открыто")
            
            # Выбираем Sign Off
            sign_off_button = page.locator("//li[contains(text(),'Sign Off')]")
            sign_off_button.wait_for(state="visible", timeout=60000)
            sign_off_button.click()
            print("Sign Off нажат")

            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()

            time.sleep(3)
            
            print("Автоматизация завершена успешно!")
            
        except Exception as e:
            print(f"Ошибка при выполнении автоматизации: {e}")
            
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run_automation()
