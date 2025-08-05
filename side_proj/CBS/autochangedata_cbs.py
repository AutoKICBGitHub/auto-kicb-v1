from playwright.sync_api import sync_playwright
import time
import random

def generate_passport_number():
    """
    Генерирует случайный номер паспорта в формате ID + 7 цифр.
    Используется для создания уникального паспортного номера клиента.
    """
    return f"ID{random.randint(1000000, 9999999)}"

def generate_kg_inn():
    """
    Генерирует случайный ИНН Кыргызстана (14 цифр).
    Формат: первая цифра - код пола, следующие 8 цифр - дата рождения,
    последние 5 цифр - случайные.
    """
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
    """
    Генерирует случайное слово на кириллице для заполнения полей
    места работы и должности клиента.
    """
    workplaces = ["БишкекМунай", "КыргызБанк", "АсиаТелеком", "МанасУнивер", "БакайБанк", "ДемирКыргыз", "КыргызстанТелеком"]
    positions = ["Менеджер", "Инженер", "Экономист", "Бухгалтер", "Аналитик", "Консультант", "Специалист"]
    
    return random.choice(workplaces + positions)

def run_automation():
    """
    Основная функция автоматизации работы с CBS системой.
    Выполняет следующие этапы:
    1. Авторизация в системе под пользователем meerimda
    2. Изменение данных клиента (паспорт, ИНН, персональные данные)
    3. Смена пользователя на elinan
    4. Авторизация изменений
    """
    
    with sync_playwright() as playwright:
        # Инициализация браузера с настройками для обхода антибот-защиты
        browser = playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # ID клиента, данные которого будут изменены
        customer_id = "00848797"

        # Скрытие признаков автоматизации от системы
        page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # ==========================================
            # БЛОК 1: НАЧАЛЬНАЯ АВТОРИЗАЦИЯ В СИСТЕМЕ
            # ==========================================
            
            # Шаг 1: Открытие главной страницы CBS системы
            page.goto("https://localhost:8101/FCJNeoWeb/SMMDIFRM.jsp")
            print("Шаг 1: Открыта главная страница CBS системы")
            
            time.sleep(2)
            
            # Шаг 2: Обработка первого системного уведомления
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 2: Обработано первое системное уведомление")
            
            # Шаг 3: Ввод логина первого пользователя (meerimda)
            login_field = page.locator("//input [@id='LOGINUSERID']")
            login_field.wait_for(state="visible", timeout=60000)
            login_field.fill("meerimda")
            print("Шаг 3: Введен логин пользователя meerimda")
            
            # Шаг 4: Ввод пароля (пробел)
            password_field = page.locator("//input [@id='user_pwd']")
            password_field.fill(" ")
            print("Шаг 4: Введен пароль")

            # Шаг 5: Подтверждение входа
            page.keyboard.press('Enter')
            print("Шаг 5: Нажата клавиша Enter для входа")
           
            # Шаг 6: Подтверждение успешной авторизации
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 6: Подтверждена успешная авторизация")
            
            # Шаг 7: Удаление блокирующих элементов интерфейса
            try:
                page.evaluate("document.getElementById('masker').style.display = 'none'")
                page.evaluate("document.getElementById('Div_ChildWin').style.display = 'none'")
                print("Шаг 7: Удалены блокирующие элементы интерфейса")
            except:
                print("Шаг 7: Блокирующие элементы не найдены")
            
            # ==========================================
            # БЛОК 2: НАСТРОЙКА РАБОЧЕЙ СРЕДЫ (ФИЛИАЛ)
            # ==========================================
            
            # Шаг 8: Выбор филиала 533
            branch533= page.locator("//li [@title='533']")
            branch533.wait_for(state="visible", timeout=60000)
            
            try:
                branch533.click()
                print("Шаг 8: Выбран филиал 533")
            except:
                page.evaluate("document.querySelector('li[title=\"533\"]').click()")
                print("Шаг 8: Выбран филиал 533 через JavaScript")

            # Шаг 9: Подтверждение выбора филиала
            select_branch =  page.locator("//li [@id='select_branch']")
            select_branch.wait_for(state="visible", timeout=60000)
            select_branch.click()
            print("Шаг 9: Подтверждён выбор филиала")
 
            # Шаг 10: Переход к настройке кода филиала
            iframe = page.frame_locator("#ifrSubScreen")
            
            # Шаг 11: Ввод кода филиала 700
            Branch_code = iframe.locator("//input[@id='1']")
            Branch_code.wait_for(state="visible", timeout=60000)
            Branch_code.clear()
            Branch_code.fill("700")
            print("Шаг 11: Введен код филиала 700")
           
            # Шаг 12: Получение данных филиала
            fetch = iframe.locator("//button[contains(text(),'Fetch')]")
            fetch.wait_for(state="visible", timeout=60000)
            fetch.click()
            print("Шаг 12: Получены данные филиала")

            # Шаг 13: Переход к транзакционному вводу
            change_branch = iframe.locator("//a [contains(text(),'TRANSACTION INPUT')]")
            change_branch.wait_for(state="visible", timeout=60000)
            change_branch.click()
            print("Шаг 13: Переход к транзакционному вводу")

            # Шаг 14: Подтверждение смены режима
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 14: Подтверждена смена режима")
            
            # ==========================================
            # БЛОК 3: НАВИГАЦИЯ К КЛИЕНТСКИМ ДАННЫМ
            # ==========================================
            
            # Шаг 15: Открытие главного меню
            menu_button = page.locator("#menuExpandCollapse")
            menu_button.wait_for(state="visible", timeout=60000)
            menu_button.click()
            print("Шаг 15: Открыто главное меню")
            
            # Шаг 16: Переход к разделу "Клиенты"
            customers_button = page.locator("#Fid20A")
            customers_button.wait_for(state="visible", timeout=60000)
            customers_button.click()
            print("Шаг 16: Открыт раздел 'Клиенты'")
            
            # Шаг 17: Переход к операциям с клиентами
            operations_button = page.locator("#Fid21A")
            operations_button.wait_for(state="visible", timeout=60000)
            operations_button.click()
            print("Шаг 17: Открыт раздел 'Операции'")
            
            # Шаг 18: Открытие формы ввода данных клиента
            customer_input_button = page.locator("#STDCIF\\|CIF")
            customer_input_button.wait_for(state="visible", timeout=60000)
            customer_input_button.click()
            print("Шаг 18: Открыта форма ввода данных клиента")

            # Шаг 19: Переход к iframe с данными клиента
            customer_iframe = page.frame_locator("iframe").first
            print("Шаг 19: Переход к iframe с данными клиента")
            
            # ==========================================
            # БЛОК 4: ПОИСК И ЗАГРУЗКА ДАННЫХ КЛИЕНТА
            # ==========================================
            
            # Шаг 20: Инициализация поиска клиента
            enter_query = customer_iframe.locator("//a[contains(text(),'Enter Query')]")
            enter_query.wait_for(state="visible", timeout=60000)
            enter_query.click()
            print("Шаг 20: Инициализирован поиск клиента")

            # Шаг 21: Ввод номера клиента для поиска
            customer_field = customer_iframe.locator("#BLK_CUSTOMER__CUSTNO")
            customer_field.wait_for(state="visible", timeout=60000)
            customer_field.clear()
            customer_field.fill(customer_id)
            print(f"Шаг 21: Введен номер клиента {customer_id}")

            # Шаг 22: Выполнение поиска клиента
            execute_query = customer_iframe.locator("//a[contains(text(),'Execute Query')]")
            execute_query.wait_for(state="visible", timeout=60000)
            execute_query.click()
            print("Шаг 22: Выполнен поиск клиента")
            
            # ==========================================
            # БЛОК 5: ПОДГОТОВКА СЛУЧАЙНЫХ ДАННЫХ
            # ==========================================
            
            # Шаг 23: Генерация новых случайных данных
            passport_number = generate_passport_number()
            kg_inn = generate_kg_inn()
            print(f"Шаг 23: Сгенерированы новые данные - Паспорт: {passport_number}, ИНН: {kg_inn}")
            
            # ==========================================
            # БЛОК 6: ИЗМЕНЕНИЕ ОСНОВНЫХ ДАННЫХ КЛИЕНТА
            # ==========================================
            
            # Шаг 24: Разблокировка записи для редактирования
            unlock_button = customer_iframe.locator("//a[contains(text(),'Unlock')]")
            unlock_button.wait_for(state="visible", timeout=60000)
            unlock_button.click()
            print("Шаг 24: Запись разблокирована для редактирования")
            
            # Шаг 25: Установка категории клиента
            customer_category_field = customer_iframe.locator("#BLK_CUSTOMER__CCATEG")
            customer_category_field.wait_for(state="visible", timeout=60000)
            customer_category_field.clear()
            customer_category_field.fill("INDV.RES")
            print("Шаг 25: Установлена категория клиента INDV.RES")
            
            # Шаг 26: Обновление номера паспорта
            passport_field = customer_iframe.locator("#BLK_CUSTPERSONAL__PPTNO")
            passport_field.wait_for(state="visible", timeout=60000)
            passport_field.clear()
            passport_field.fill(passport_number)
            print(f"Шаг 26: Обновлен номер паспорта на {passport_number}")
            
            # ==========================================
            # БЛОК 7: ИЗМЕНЕНИЕ ДОПОЛНИТЕЛЬНЫХ ДАННЫХ
            # ==========================================
            
            # Шаг 27: Переход к дополнительным полям
            auxiliary_button = customer_iframe.locator("//span[contains(text(),'Auxiliary')]")
            auxiliary_button.wait_for(state="visible", timeout=60000)
            auxiliary_button.click()
            print("Шаг 27: Переход к дополнительным полям")
            
            # Шаг 28: Обновление ИНН клиента
            udf1_field = customer_iframe.locator("#BLK_CUSTOMER__UDF1")
            udf1_field.wait_for(state="visible", timeout=60000)
            
            current_inn = udf1_field.input_value()
            print(f"Шаг 28а: Текущий ИНН: {current_inn}")
            
            # Генерация нового ИНН с сохранением первых 9 символов
            if len(current_inn) >= 9:
                new_random_digits = random.randint(10000, 99999)
                new_inn = current_inn[:9] + str(new_random_digits)
            else:
                new_inn = kg_inn
            
            udf1_field.click()
            udf1_field.clear()
            udf1_field.fill(new_inn)
            print(f"Шаг 28б: ИНН обновлен на {new_inn}")
            
            # Шаг 29: Проверка корректности ввода ИНН
            filled_value = udf1_field.input_value()
            print(f"Шаг 29: Проверка ИНН - сохранено: {filled_value}")
            
            # ==========================================
            # БЛОК 8: ИЗМЕНЕНИЕ ПЕРСОНАЛЬНЫХ ДАННЫХ
            # ==========================================
            
            # Шаг 30: Переход к персональным данным
            domestic_button = customer_iframe.locator("//a[contains(text(),'Domestic')]")
            domestic_button.wait_for(state="visible", timeout=60000)
            domestic_button.click()
            print("Шаг 30: Переход к персональным данным")
            
            # Шаг 31: Изменение семейного положения
            domestic_iframe = customer_iframe.frame_locator("#ifrSubScreen")
            
            marital_options = ["M", "D", "R", "S", "P", "E"]
            selected_status = random.choice(marital_options)
            
            marital_status_field = domestic_iframe.locator("select.SELstd#BLK_CUSTDOMESTIC__MARITALSTAT")
            marital_status_field.wait_for(state="visible", timeout=60000)
            marital_status_field.select_option(selected_status)
            print(f"Шаг 31: Изменено семейное положение на {selected_status}")
            
            # Шаг 32: Сохранение персональных данных
            ok_button = domestic_iframe.locator("#BTN_OK")
            ok_button.wait_for(state="visible", timeout=60000)
            ok_button.click()
            print("Шаг 32: Сохранены персональные данные")
            
            # ==========================================
            # БЛОК 9: ИЗМЕНЕНИЕ ПРОФЕССИОНАЛЬНЫХ ДАННЫХ
            # ==========================================
            
            # Шаг 33: Переход к профессиональным данным
            professional_button = customer_iframe.locator("//a[contains(text(),'Professional')]")
            professional_button.wait_for(state="visible", timeout=60000)
            professional_button.click()
            print("Шаг 33: Переход к профессиональным данным")
            
            # Шаг 34: Генерация новых рабочих данных
            professional_iframe = customer_iframe.frame_locator("#ifrSubScreen")
            
            workplace = generate_cyrillic_word()
            position = generate_cyrillic_word()
            print(f"Шаг 34: Сгенерированы рабочие данные - Место: {workplace}, Должность: {position}")
            
            # Шаг 35: Обновление места работы
            workplace_field = professional_iframe.locator("#BLK_CUSTPROF__PREVEMP")
            workplace_field.wait_for(state="visible", timeout=60000)
            workplace_field.fill(workplace)
            print("Шаг 35: Обновлено место работы")
            
            # Шаг 36: Обновление должности
            position_field = professional_iframe.locator("#BLK_CUSTPROF__CURRDESIG")
            position_field.wait_for(state="visible", timeout=60000)
            position_field.fill(position)
            print("Шаг 36: Обновлена должность")

            # Шаг 37: Сохранение профессиональных данных
            ok_button = professional_iframe.locator("#BTN_OK")
            ok_button.wait_for(state="visible", timeout=60000)
            ok_button.click()
            print("Шаг 37: Сохранены профессиональные данные")
            
            # ==========================================
            # БЛОК 10: СОХРАНЕНИЕ ВСЕХ ИЗМЕНЕНИЙ
            # ==========================================
            
            # Шаг 38: Сохранение всех изменений данных клиента
            save_button = customer_iframe.locator("//a[contains(text(),'Save')]")
            save_button.wait_for(state="visible", timeout=60000)
            save_button.click()
            print("Шаг 38: Инициировано сохранение всех изменений")
            
            # Шаг 39: Подтверждение изменений
            alert_iframe = customer_iframe.frame_locator("#ifr_AlertWin")
            
            accept_button = alert_iframe.locator("#BTN_ACCEPT")
            accept_button.wait_for(state="visible", timeout=60000)
            accept_button.click()
            print("Шаг 39: Подтверждены изменения")
            
            # Шаг 40: Финальное подтверждение сохранения
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 40: Получено финальное подтверждение сохранения")
            
            # Шаг 41: Закрытие окна клиентских данных
            customer_maintenance_iframe = page.frame_locator("iframe[id*='ifr_LaunchWin']")
            close_button = customer_maintenance_iframe.locator("#WNDbuttons")
            close_button.wait_for(state="visible", timeout=60000)
            close_button.click()
            print("Шаг 41: Закрыто окно клиентских данных")

            # ==========================================
            # БЛОК 11: ЗАВЕРШЕНИЕ РАБОТЫ ПЕРВОГО ПОЛЬЗОВАТЕЛЯ
            # ==========================================
            
            # Шаг 42: Возврат к домашнему филиалу
            branch700= page.locator("//li [@title='700']")
            branch700.wait_for(state="visible", timeout=60000)
            branch700.click()
            print("Шаг 42: Выбран домашний филиал 700")
            
            # Шаг 43: Подтверждение смены филиала
            home_branch = page.locator("//li [@id='home_branch']")
            home_branch.wait_for(state="visible", timeout=60000)
            home_branch.click()
            print("Шаг 43: Подтверждена смена на домашний филиал")

            # Шаг 44: Обработка уведомления о смене филиала
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 44: Обработано уведомление о смене филиала")
            
            # Шаг 45: Открытие пользовательского меню
            user_menu = page.locator("//li[@class='user']")
            user_menu.wait_for(state="visible", timeout=60000)
            user_menu.click()
            print("Шаг 45: Открыто пользовательское меню")
            
            # Шаг 46: Выход из системы (первый пользователь)
            sign_off_button = page.locator("//li[contains(text(),'Sign Off')]")
            sign_off_button.wait_for(state="visible", timeout=60000)
            sign_off_button.click()
            print("Шаг 46: Выполнен выход из системы (пользователь meerimda)")

            # Шаг 47: Подтверждение выхода
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 47: Подтверждён выход из системы")

            time.sleep(3)

            # Шаг 48: Обработка финального уведомления о выходе
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 48: Обработано финальное уведомление о выходе")
            
            # ==========================================
            # БЛОК 12: АВТОРИЗАЦИЯ ВТОРОГО ПОЛЬЗОВАТЕЛЯ
            # ==========================================
            
            # Шаг 49: Ввод логина второго пользователя (elinan)
            login_field = page.locator("//input [@id='LOGINUSERID']")
            login_field.wait_for(state="visible", timeout=60000)
            login_field.fill("elinan")
            print("Шаг 49: Введен логин второго пользователя elinan")
            
            # Шаг 50: Ввод пароля второго пользователя
            password_field = page.locator("//input [@id='user_pwd']")
            password_field.fill(" ")
            print("Шаг 50: Введен пароль второго пользователя")

            # Шаг 51: Подтверждение входа второго пользователя
            page.keyboard.press('Enter')
            print("Шаг 51: Подтверждён вход второго пользователя")
            
            # Шаг 52: Подтверждение успешной авторизации
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 52: Подтверждена авторизация второго пользователя")

            # ==========================================
            # БЛОК 13: НАСТРОЙКА РАБОЧЕЙ СРЕДЫ (ВТОРОЙ ПОЛЬЗОВАТЕЛЬ)
            # ==========================================
            
            # Шаг 53: Выбор филиала 533 (повторная настройка)
            branch533= page.locator("//li [@title='533']")
            branch533.wait_for(state="visible", timeout=60000)
            
            try:
                branch533.click()
                print("Шаг 53: Выбран филиал 533 для второго пользователя")
            except:
                page.evaluate("document.querySelector('li[title=\"533\"]').click()")
                print("Шаг 53: Выбран филиал 533 через JavaScript")

            # Шаг 54: Подтверждение выбора филиала
            select_branch =  page.locator("//li [@id='select_branch']")
            select_branch.wait_for(state="visible", timeout=60000)
            select_branch.click()
            print("Шаг 54: Подтверждён выбор филиала")
            
            # Шаг 55: Настройка кода филиала
            iframe = page.frame_locator("#ifrSubScreen")
            
            Branch_code = iframe.locator("//input[@id='1']")
            Branch_code.wait_for(state="visible", timeout=60000)
            Branch_code.clear()
            Branch_code.fill("700")
            print("Шаг 55: Настроен код филиала 700")
            
            # Шаг 56: Получение данных филиала
            fetch = iframe.locator("//button[contains(text(),'Fetch')]")
            fetch.wait_for(state="visible", timeout=60000)
            fetch.click()
            print("Шаг 56: Получены данные филиала")

            # Шаг 57: Переход к транзакционному режиму
            change_branch = iframe.locator("//a [contains(text(),'TRANSACTION INPUT')]")
            change_branch.wait_for(state="visible", timeout=60000)
            change_branch.click()
            print("Шаг 57: Переход к транзакционному режиму")

            # Шаг 58: Подтверждение смены режима
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 58: Подтверждена смена режима")
            
            # ==========================================
            # БЛОК 14: НАВИГАЦИЯ К АВТОРИЗАЦИИ ИЗМЕНЕНИЙ
            # ==========================================
            
            # Шаг 59: Открытие главного меню
            menu_button = page.locator("#menuExpandCollapse")
            menu_button.wait_for(state="visible", timeout=60000)
            menu_button.click()
            print("Шаг 59: Открыто главное меню")
            
            # Шаг 60: Переход к разделу "Клиенты"
            customers_button = page.locator("#Fid20A")
            customers_button.wait_for(state="visible", timeout=60000)
            customers_button.click()
            print("Шаг 60: Открыт раздел 'Клиенты'")
            
            # Шаг 61: Переход к операциям с клиентами
            operations_button = page.locator("#Fid21A")
            operations_button.wait_for(state="visible", timeout=60000)
            operations_button.click()
            print("Шаг 61: Открыт раздел 'Операции'")
            
            # Шаг 62: Открытие формы ввода данных клиента
            customer_input_button = page.locator("#STDCIF\\|CIF")
            customer_input_button.wait_for(state="visible", timeout=60000)
            customer_input_button.click()
            print("Шаг 62: Открыта форма ввода данных клиента")
            
            # Шаг 63: Переход к iframe с данными клиента
            customer_iframe = page.frame_locator("iframe").first
            print("Шаг 63: Переход к iframe с данными клиента")
            
            # ==========================================
            # БЛОК 15: ПОИСК КЛИЕНТА ДЛЯ АВТОРИЗАЦИИ
            # ==========================================
            
            # Шаг 64: Инициализация поиска для авторизации
            enter_query = customer_iframe.locator("//a[contains(text(),'Enter Query')]")
            enter_query.wait_for(state="visible", timeout=60000)
            enter_query.click()
            print("Шаг 64: Инициализирован поиск для авторизации")

            # Шаг 65: Ввод номера клиента для авторизации
            customer_field = customer_iframe.locator("#BLK_CUSTOMER__CUSTNO")
            customer_field.wait_for(state="visible", timeout=60000)
            customer_field.clear()
            customer_field.fill(customer_id)
            print(f"Шаг 65: Введен номер клиента {customer_id} для авторизации")

            # Шаг 66: Выполнение поиска клиента
            execute_query = customer_iframe.locator("//a[contains(text(),'Execute Query')]")
            execute_query.wait_for(state="visible", timeout=60000)
            execute_query.click()
            print("Шаг 66: Выполнен поиск клиента")
            
            # ==========================================
            # БЛОК 16: АВТОРИЗАЦИЯ ИЗМЕНЕНИЙ
            # ==========================================
            
            # Шаг 67: Запуск процесса авторизации
            authorize_button = customer_iframe.locator("//a[contains(text(),'Authorize')]")
            authorize_button.wait_for(state="visible", timeout=60000)
            authorize_button.click()
            print("Шаг 67: Запущен процесс авторизации изменений")
            
            # Шаг 68: Получение iframe авторизации
            launch_frame = page.frame_locator("#ifr_LaunchWin")
            authorize_iframe = launch_frame.frame_locator("#ifrSubScreen")
            print("Шаг 68: Получен iframe авторизации")
            
            # Шаг 69: Подтверждение авторизации
            accept_button = customer_iframe.frame_locator("#ifrSubScreen").locator("#BTN_OK")
            accept_button.wait_for(state="visible", timeout=5000)
            accept_button.click()
            print("Шаг 69: Подтверждена авторизация изменений")
            
            # Шаг 70: Обработка уведомления об авторизации
            alert_iframe = customer_iframe.frame_locator("#ifrSubScreen").frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 70: Обработано уведомление об авторизации")
            
            # Шаг 71: Закрытие окна авторизации
            customer_maintenance_iframe = page.frame_locator("iframe[id*='ifr_LaunchWin']")
            close_button = customer_maintenance_iframe.locator("#WNDbuttons")
            close_button.wait_for(state="visible", timeout=60000)
            close_button.click()
            print("Шаг 71: Закрыто окно авторизации")

            # ==========================================
            # БЛОК 17: ЗАВЕРШЕНИЕ РАБОТЫ ВТОРОГО ПОЛЬЗОВАТЕЛЯ
            # ==========================================
            
            # Шаг 72: Возврат к домашнему филиалу
            branch700= page.locator("//li [@title='700']")
            branch700.wait_for(state="visible", timeout=60000)
            branch700.click()
            print("Шаг 72: Выбран домашний филиал 700")
            
            # Шаг 73: Подтверждение смены филиала
            home_branch = page.locator("//li [@id='home_branch']")
            home_branch.wait_for(state="visible", timeout=60000)
            home_branch.click()
            print("Шаг 73: Подтверждена смена на домашний филиал")

            # Шаг 74: Обработка уведомления о смене филиала
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 74: Обработано уведомление о смене филиала")
            
            # Шаг 75: Открытие пользовательского меню
            user_menu = page.locator("//li[@class='user']")
            user_menu.wait_for(state="visible", timeout=60000)
            user_menu.click()
            print("Шаг 75: Открыто пользовательское меню")
            
            # Шаг 76: Выход из системы (второй пользователь)
            sign_off_button = page.locator("//li[contains(text(),'Sign Off')]")
            sign_off_button.wait_for(state="visible", timeout=60000)
            sign_off_button.click()
            print("Шаг 76: Выполнен выход из системы (пользователь elinan)")

            # Шаг 77: Подтверждение выхода
            alert_iframe = page.frame_locator("#ifr_AlertWin")
            alert_ok_button = alert_iframe.locator("#BTN_OK")
            alert_ok_button.wait_for(state="visible", timeout=60000)
            alert_ok_button.click()
            print("Шаг 77: Подтверждён выход из системы")

            time.sleep(3)
            
            # ==========================================
            # ЗАВЕРШЕНИЕ АВТОМАТИЗАЦИИ
            # ==========================================
            
            print("="*50)
            print("АВТОМАТИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("="*50)
            print("Выполненные операции:")
            print(f"• Изменены данные клиента {customer_id}")
            print(f"• Обновлен номер паспорта: {passport_number}")
            print(f"• Обновлен ИНН: {new_inn}")
            print(f"• Изменено семейное положение: {selected_status}")
            print(f"• Обновлено место работы: {workplace}")
            print(f"• Обновлена должность: {position}")
            print("• Все изменения авторизованы")
            print("="*50)
            
        except Exception as e:
            print(f"ОШИБКА: {e}")
            print("Автоматизация прервана из-за ошибки")
            
        finally:
            # Очистка ресурсов
            context.close()
            browser.close()
            print("Браузер закрыт, ресурсы освобождены")

if __name__ == "__main__":
    print("Запуск автоматизации CBS системы...")
    print("="*50)
    run_automation()
